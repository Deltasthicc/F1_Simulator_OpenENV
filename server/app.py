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
    model: str = "heuristic"  # "heuristic" | "random"


# Minimal valid action pool for the random policy
_RANDOM_ACTIONS = [
    "STAY_OUT", "INSPECT_TYRE_DEGRADATION", "REQUEST_FORECAST",
    "ASSESS_UNDERCUT_WINDOW", "INSPECT_FUEL_MARGIN",
    "PIT_NOW soft", "PIT_NOW medium", "PIT_NOW hard",
    "SET_MODE push", "SET_MODE conserve", "SET_MODE race",
    "DEFEND_POSITION", "HOLD_GAP 1",
]

_DIM_KEYS = [
    "race_result", "strategic_decisions", "tyre_management",
    "fuel_management", "comms_quality", "operational_efficiency",
]


def _surface_label(weather_dict: dict) -> str:
    """Convert the WeatherState dict to a readable label."""
    rain = weather_dict.get("rain_intensity", 0.0) if weather_dict else 0.0
    surface = weather_dict.get("surface_state", "dry") if weather_dict else "dry"
    if rain > 0.5 or surface == "wet":
        return "heavy rain"
    if rain > 0.15 or surface == "damp":
        return "light rain"
    return "dry"


@app.post("/simulate", include_in_schema=True)
def simulate_episode(req: SimulateRequest) -> dict[str, Any]:
    """Run one episode with the chosen policy and return the full lap-by-lap trajectory."""
    import random as _random
    import traceback

    try:
        policy_name = req.model.lower().strip()
        env = F1StrategistEnvironment()
        obs = env.reset(task=req.task, seed=req.seed)

        # Build the generator based on requested model
        import sys as _sys, pathlib as _pl
        _root = str(_pl.Path(__file__).parent.parent)
        if _root not in _sys.path:
            _sys.path.insert(0, _root)

        from inference import _heuristic_generator as _heur, parse_action as _parse, SYSTEM_PROMPT as _sysprompt

        policy_note = ""
        generator = None  # callable(history, obs, task) -> str, or None for random

        if policy_name == "random":
            pass  # generator stays None

        elif policy_name in ("grpo_v1", "grpo"):
            # Try to load the trained LoRA checkpoint
            checkpoint = _pl.Path(__file__).parent.parent / "grpo_v1"
            if checkpoint.exists():
                try:
                    from transformers import AutoModelForCausalLM, AutoTokenizer
                    import torch
                    _tok = AutoTokenizer.from_pretrained(str(checkpoint), trust_remote_code=True)
                    _dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
                    _lm  = AutoModelForCausalLM.from_pretrained(
                        str(checkpoint), torch_dtype=_dtype,
                        device_map="auto", trust_remote_code=True,
                    )
                    def generator(history, obs, task):
                        if hasattr(_tok, "apply_chat_template"):
                            txt = _tok.apply_chat_template(history, tokenize=False, add_generation_prompt=True)
                        else:
                            txt = "\n".join(f"{m['role']}: {m['content']}" for m in history) + "\nassistant:"
                        inp = _tok(txt, return_tensors="pt").to(_lm.device)
                        with torch.no_grad():
                            out = _lm.generate(**inp, max_new_tokens=64, do_sample=False)
                        return _tok.decode(out[0][inp["input_ids"].shape[-1]:], skip_special_tokens=True)
                    policy_name = "grpo_v1"
                    policy_note = "Loaded grpo_v1 checkpoint."
                except Exception as _e:
                    generator = _heur
                    policy_name = "grpo_v1 (heuristic fallback)"
                    policy_note = f"Checkpoint found but transformers load failed: {_e}. Using heuristic."
            else:
                generator = _heur
                policy_name = "grpo_v1 (heuristic fallback)"
                policy_note = "grpo_v1 checkpoint not present on this server. Using heuristic stand-in."

        elif policy_name in ("qwen3", "qwen3-0.6b", "llm"):
            try:
                from transformers import AutoModelForCausalLM, AutoTokenizer
                import torch
                _model_id = "Qwen/Qwen3-0.6B"
                _tok = AutoTokenizer.from_pretrained(_model_id, trust_remote_code=True)
                _dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
                _lm  = AutoModelForCausalLM.from_pretrained(
                    _model_id, torch_dtype=_dtype,
                    device_map="auto", trust_remote_code=True,
                )
                def generator(history, obs, task):
                    if hasattr(_tok, "apply_chat_template"):
                        txt = _tok.apply_chat_template(history, tokenize=False, add_generation_prompt=True)
                    else:
                        txt = "\n".join(f"{m['role']}: {m['content']}" for m in history) + "\nassistant:"
                    inp = _tok(txt, return_tensors="pt").to(_lm.device)
                    with torch.no_grad():
                        out = _lm.generate(**inp, max_new_tokens=64, do_sample=False)
                    return _tok.decode(out[0][inp["input_ids"].shape[-1]:], skip_special_tokens=True)
                policy_name = "qwen3-0.6b"
                policy_note = "Loaded Qwen/Qwen3-0.6B from HuggingFace Hub."
            except Exception as _e:
                generator = _heur
                policy_name = "qwen3 (heuristic fallback)"
                policy_note = f"Could not load Qwen3-0.6B ({_e}). Using heuristic stand-in."

        else:
            # Default: heuristic
            generator = _heur
            policy_name = "heuristic"

        history: list[dict] = [{"role": "system", "content": _sysprompt}]
        laps: list[dict] = []
        safety_limit = max(obs.total_laps + 5, 60)

        for _ in range(safety_limit):
            if obs.done:
                break

            # Choose action
            if generator is None:
                # Random policy
                action_str = _random.choice(_RANDOM_ACTIONS)
                if obs.current_lap >= obs.total_laps:
                    action_str = "DONE"
            else:
                history.append({"role": "user", "content": str(obs.message)})
                raw = generator(history, obs, req.task)
                action_str = _parse(raw).command
                history.append({"role": "assistant", "content": action_str})

            action = F1Action(command=action_str)
            rain = (obs.weather_current or {}).get("rain_intensity", 0.0)
            key_decision = action_str.upper().startswith(
                ("PIT_NOW", "RADIO_DRIVER", "REQUEST_FORECAST", "DONE",
                 "ASSESS_UNDERCUT_WINDOW", "CHECK_OPPONENT")
            )
            laps.append({
                "lap":        obs.current_lap,
                "action":     action_str,
                "position":   int(obs.ego_position),
                "compound":   obs.ego_tyre_compound,
                "health":     round(float(obs.ego_tyre_health_pct), 1),
                "fuel":       round(float(obs.ego_fuel_remaining_kg), 2),
                "weather":    _surface_label(obs.weather_current),
                "rain":       round(float(rain), 2),
                "total_laps": int(obs.total_laps),
                "key":        key_decision,
            })
            obs = env.step(action)

        # Add terminal record
        laps.append({
            "lap":        int(obs.current_lap),
            "action":     "DONE",
            "position":   int(obs.ego_position),
            "compound":   obs.ego_tyre_compound,
            "health":     round(float(obs.ego_tyre_health_pct), 1),
            "fuel":       round(float(obs.ego_fuel_remaining_kg), 2),
            "weather":    _surface_label(obs.weather_current),
            "rain":       round(float((obs.weather_current or {}).get("rain_intensity", 0.0)), 2),
            "total_laps": int(obs.total_laps),
            "key":        True,
        })

        mos = obs.multi_objective_scores or {}
        score = float(mos.get("weighted_final", obs.score or 0.0))
        dims  = {k: round(float(mos.get(k, 0.0)), 3) for k in _DIM_KEYS}

        return {
            "task":        req.task,
            "seed":        req.seed,
            "laps":        laps,
            "final_score": round(score, 4),
            "final_pos":   int(obs.ego_position),
            "dims":        dims,
            "policy":      policy_name,
            "policy_note": policy_note,
        }

    except Exception as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}")


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
