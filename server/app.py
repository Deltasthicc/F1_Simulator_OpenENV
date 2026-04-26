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


@app.post("/simulate", include_in_schema=True)
def simulate_episode(req: SimulateRequest) -> dict[str, Any]:
    """Run one episode with the heuristic policy and return the full trajectory."""
    from inference import _heuristic_generator, format_obs, parse_action, SYSTEM_PROMPT

    env = F1StrategistEnvironment()
    obs = env.reset(task=req.task, seed=req.seed)
    history: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    laps: list[dict] = []

    while not obs.done:
        prompt = format_obs(obs)
        history.append({"role": "user", "content": prompt})
        action_str = _heuristic_generator(history, obs, req.task)
        action = parse_action(action_str)
        history.append({"role": "assistant", "content": action.command})

        rain = (obs.weather_current or {}).get("rain_intensity", 0.0)
        key = action.command.upper().startswith(("PIT_NOW", "RADIO_DRIVER", "REQUEST_FORECAST", "DONE"))
        laps.append({
            "lap":        obs.current_lap,
            "action":     action.command,
            "position":   obs.ego_position,
            "compound":   obs.ego_tyre_compound,
            "health":     round(obs.ego_tyre_health_pct, 1),
            "fuel":       round(obs.ego_fuel_remaining_kg, 2),
            "weather":    obs.weather_current.get("condition", "dry") if obs.weather_current else "dry",
            "rain":       round(rain, 2),
            "total_laps": obs.total_laps,
            "key":        key,
        })
        obs = env.step(action)

    # Final lap record
    rain = (obs.weather_current or {}).get("rain_intensity", 0.0)
    laps.append({
        "lap":        obs.current_lap,
        "action":     "DONE",
        "position":   obs.ego_position,
        "compound":   obs.ego_tyre_compound,
        "health":     round(obs.ego_tyre_health_pct, 1),
        "fuel":       round(obs.ego_fuel_remaining_kg, 2),
        "weather":    obs.weather_current.get("condition", "dry") if obs.weather_current else "dry",
        "rain":       round(rain, 2),
        "total_laps": obs.total_laps,
        "key":        True,
    })

    score = float(obs.multi_objective_scores.get("weighted_final", obs.score or 0))
    dims  = {k: float(obs.multi_objective_scores.get(k, 0.0)) for k in
             ["race_result", "strategic_decisions", "tyre_management",
              "fuel_management", "comms_quality", "operational_efficiency"]}

    return {
        "task":        req.task,
        "seed":        req.seed,
        "laps":        laps,
        "final_score": round(score, 4),
        "final_pos":   obs.ego_position,
        "dims":        dims,
        "policy":      "heuristic",
    }


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
