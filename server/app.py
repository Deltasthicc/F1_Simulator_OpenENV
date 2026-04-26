"""
F1 Strategist — FastAPI Server
================================

Uses openenv's `create_app` helper which handles the ENABLE_WEB_INTERFACE env
var natively:
  - ENABLE_WEB_INTERFACE=0 (default): plain FastAPI with /reset /step /health /schema
  - ENABLE_WEB_INTERFACE=1 (Dockerfile default): adds the openenv built-in Gradio
    web panel at /web, plus a custom F1 scenario selector panel at /demo

The shared-environment singleton pattern keeps episode state alive across HTTP
requests (reset → step → step …) without WebSocket overhead.  close() is a
no-op so the factory lambda safely returns the same instance on every call.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from openenv.core.env_server import create_app
from pydantic import BaseModel

from models import F1Action, F1Observation
from server.environment import F1StrategistEnvironment

_STATIC_DIR = Path(__file__).parent / "static"

# ---------------------------------------------------------------------------
# Shared environment singleton
# ---------------------------------------------------------------------------
_shared_env = F1StrategistEnvironment()


def _env_factory() -> F1StrategistEnvironment:
    """Always return the same instance.  close() is a no-op, so state persists."""
    return _shared_env


# ---------------------------------------------------------------------------
# Build the FastAPI application
# ---------------------------------------------------------------------------
# create_app checks ENABLE_WEB_INTERFACE and mounts the Gradio panel at /web
# when it is set to "1" or "true".  We also layer our custom F1 demo panel on
# top of that when Gradio is available.

app = create_app(
    _env_factory,
    F1Action,
    F1Observation,
    env_name="F1 Strategist",
)

# Mount static assets and the line-drawing landing page at GET /
# openenv's create_app may register a "/" redirect to /web — strip it first
# so our landing page is what visitors see at the root URL. /web (Gradio
# panel) and /reset /step /health are unaffected.
if _STATIC_DIR.exists():
    # Remove any existing route at "/" that openenv may have added
    app.router.routes = [
        r for r in app.router.routes
        if not (getattr(r, "path", None) == "/" and "GET" in getattr(r, "methods", set()) | {"GET"})
    ]
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    def _landing():
        index = _STATIC_DIR / "index.html"
        if index.exists():
            return FileResponse(str(index), media_type="text/html")
        return {"status": "ok", "name": "F1 Strategist", "see": "/web"}

# ---------------------------------------------------------------------------
# /simulate endpoint — runs a full episode with heuristic policy, returns
# lap-by-lap trajectory as JSON so the landing page JS can animate it.
# Uses a fresh env instance to avoid disturbing the shared singleton.
# ---------------------------------------------------------------------------

class SimulateRequest(BaseModel):
    task: str = "weather_roulette"
    seed: int = 7
    model: str = "heuristic"  # "heuristic" | "random" | "grpo_v1" | "qwen3"


@app.post("/simulate", include_in_schema=True)
def simulate_episode(req: SimulateRequest) -> dict[str, Any]:
    """Run one episode with the chosen policy and return the full lap-by-lap trajectory."""
    import traceback
    from pathlib import Path as _Path

    # Import from server.simulate_utils — always resolvable since it's in the
    # same package as app.py, no root-level sys.path manipulation needed.
    from server.simulate_utils import (
        SYSTEM_PROMPT, DIM_KEYS, parse_action, surface_label,
        heuristic, random_action, get_scenario_family,
    )

    try:
        policy_name = req.model.lower().strip()
        policy_note = ""

        env = F1StrategistEnvironment()
        obs = env.reset(task=req.task, seed=req.seed)
        family = get_scenario_family(req.task)

        # ── Build LLM generator for grpo_v1 / qwen3 ──────────────────────
        llm_gen = None  # if None, we use the rule-based heuristic

        if policy_name in ("grpo_v1", "grpo"):
            # Prefer /app/grpo_v1 (Docker absolute path), then relative to this file
            checkpoint = _Path("/app/grpo_v1")
            if not checkpoint.exists():
                checkpoint = _Path(__file__).parent.parent / "grpo_v1"
            if checkpoint.exists():
                try:
                    import torch
                    from transformers import AutoModelForCausalLM, AutoTokenizer
                    from peft import PeftModel
                    _tok = AutoTokenizer.from_pretrained(
                        str(checkpoint), trust_remote_code=True)
                    # float16 halves memory vs float32; no CUDA needed
                    _base = AutoModelForCausalLM.from_pretrained(
                        "unsloth/Qwen3-4B",
                        torch_dtype=torch.float16,
                        low_cpu_mem_usage=True,
                        trust_remote_code=True,
                    )
                    _lm = PeftModel.from_pretrained(_base, str(checkpoint))
                    _lm.eval()

                    def llm_gen(history: list[dict]) -> str:
                        txt = _tok.apply_chat_template(
                            history, tokenize=False, add_generation_prompt=True
                        ) if hasattr(_tok, "apply_chat_template") else (
                            "\n".join(f"{m['role']}: {m['content']}" for m in history) + "\nassistant:"
                        )
                        inp = _tok(txt, return_tensors="pt")
                        with torch.no_grad():
                            out = _lm.generate(**inp, max_new_tokens=64, do_sample=False)
                        return _tok.decode(out[0][inp["input_ids"].shape[-1]:], skip_special_tokens=True)

                    policy_name = "grpo_v1"
                    policy_note = "Loaded grpo_v1 (Qwen3-4B + LoRA). Running CPU inference."
                except MemoryError:
                    policy_note = "grpo_v1: not enough RAM to load Qwen3-4B (needs ~8 GB). Fell back to heuristic."
                    policy_name = "grpo_v1 → heuristic fallback"
                except Exception as _e:
                    policy_note = f"grpo_v1 load failed ({type(_e).__name__}: {str(_e)[:120]}). Fell back to heuristic."
                    policy_name = "grpo_v1 → heuristic fallback"
            else:
                policy_note = "grpo_v1 adapter not found on this server. Fell back to heuristic."
                policy_name = "grpo_v1 → heuristic fallback"

        elif policy_name in ("qwen3", "qwen3-0.6b", "llm"):
            try:
                import torch
                from transformers import AutoModelForCausalLM, AutoTokenizer
                _model_id = "Qwen/Qwen3-0.6B"
                _tok = AutoTokenizer.from_pretrained(_model_id, trust_remote_code=True)
                _lm  = AutoModelForCausalLM.from_pretrained(
                    _model_id,
                    torch_dtype=torch.float16,
                    low_cpu_mem_usage=True,
                    trust_remote_code=True,
                )
                _lm.eval()

                def llm_gen(history: list[dict]) -> str:
                    txt = _tok.apply_chat_template(
                        history, tokenize=False, add_generation_prompt=True
                    ) if hasattr(_tok, "apply_chat_template") else (
                        "\n".join(f"{m['role']}: {m['content']}" for m in history) + "\nassistant:"
                    )
                    inp = _tok(txt, return_tensors="pt")
                    with torch.no_grad():
                        out = _lm.generate(**inp, max_new_tokens=64, do_sample=False)
                    return _tok.decode(out[0][inp["input_ids"].shape[-1]:], skip_special_tokens=True)

                policy_name = "qwen3-0.6b"
                policy_note = "Loaded Qwen3-0.6B from HuggingFace Hub. Running CPU inference."
            except Exception as _e:
                policy_note = f"Qwen3-0.6B failed ({type(_e).__name__}: {str(_e)[:120]}). Fell back to heuristic."
                policy_name = "qwen3 → heuristic fallback"

        # ── Episode loop ─────────────────────────────────────────────────
        history: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
        seen: set[str] = set()
        laps: list[dict] = []
        safety_limit = max(obs.total_laps + 5, 60)

        for _ in range(safety_limit):
            if obs.done:
                break

            if policy_name == "random":
                action_str = random_action(obs.current_lap, obs.total_laps)
            elif llm_gen is not None:
                history.append({"role": "user", "content": str(obs.message)})
                raw = llm_gen(history)
                action_str = parse_action(raw)
                history.append({"role": "assistant", "content": action_str})
            else:
                # heuristic (also used as fallback for grpo/qwen when model unavailable)
                action_str = heuristic(family, obs.current_lap, obs.total_laps, obs, seen)

            action = F1Action(command=action_str)
            rain = (obs.weather_current or {}).get("rain_intensity", 0.0)
            key = action_str.upper().startswith(
                ("PIT_NOW", "RADIO_DRIVER", "REQUEST_FORECAST", "DONE",
                 "ASSESS_UNDERCUT_WINDOW", "CHECK_OPPONENT", "INSPECT_TYRE"))
            laps.append({
                "lap":        obs.current_lap,
                "action":     action_str,
                "position":   int(obs.ego_position),
                "compound":   obs.ego_tyre_compound,
                "health":     round(float(obs.ego_tyre_health_pct), 1),
                "fuel":       round(float(obs.ego_fuel_remaining_kg), 2),
                "weather":    surface_label(obs.weather_current),
                "rain":       round(float(rain), 2),
                "total_laps": int(obs.total_laps),
                "key":        key,
            })
            obs = env.step(action)

        # Terminal record
        rain_f = (obs.weather_current or {}).get("rain_intensity", 0.0)
        laps.append({
            "lap": int(obs.current_lap), "action": "DONE",
            "position": int(obs.ego_position), "compound": obs.ego_tyre_compound,
            "health": round(float(obs.ego_tyre_health_pct), 1),
            "fuel": round(float(obs.ego_fuel_remaining_kg), 2),
            "weather": surface_label(obs.weather_current),
            "rain": round(float(rain_f), 2),
            "total_laps": int(obs.total_laps), "key": True,
        })

        mos   = obs.multi_objective_scores or {}
        score = float(mos.get("weighted_final", obs.score or 0.0))
        dims  = {k: round(float(mos.get(k, 0.0)), 3) for k in DIM_KEYS}

        return {
            "task": req.task, "seed": req.seed,
            "laps": laps, "final_score": round(score, 4),
            "final_pos": int(obs.ego_position), "dims": dims,
            "policy": policy_name, "policy_note": policy_note,
        }

    except Exception as exc:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail=f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}",
        )


# ---------------------------------------------------------------------------
# /readme endpoint — serves README.md for the OpenEnv playground sidebar
# ---------------------------------------------------------------------------

@app.get("/readme", include_in_schema=False)
def get_readme() -> Response:
    readme = Path(__file__).parent.parent / "README.md"
    if readme.exists():
        return Response(content=readme.read_text(encoding="utf-8"), media_type="text/markdown")
    return Response(
        content="# F1 Strategist\nLLM race strategy environment. "
                "See [GitHub](https://github.com/Deltasthicc/F1_Simulator_OpenENV).",
        media_type="text/markdown",
    )


# Optional: also mount our richer custom Gradio demo panel at /demo
if os.environ.get("ENABLE_WEB_INTERFACE") == "1":
    try:
        import gradio as gr
        from server.visualizer import build_gradio_panel

        _demo_app = build_gradio_panel(_shared_env)
        app = gr.mount_gradio_app(app, _demo_app, path="/demo")
    except Exception:
        pass  # gradio not installed or panel failed — degrade gracefully


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry point for `uv run server` / pyproject [project.scripts]."""
    import uvicorn

    port = int(os.environ.get("F1_STRATEGIST_PORT", 8000))
    uvicorn.run("server.app:app", host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
