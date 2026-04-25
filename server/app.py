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

from openenv.core.env_server import create_app

from models import F1Action, F1Observation
from server.environment import F1StrategistEnvironment

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
