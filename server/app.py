"""
F1 Strategist — FastAPI Server
================================

Single shared environment instance so HTTP callers see a persistent episode.
The OpenEnv SIMULATION-mode handlers create a fresh env per request by default,
which makes multi-step interactive demos (HF Space, smoke tests) misbehave because
every /step sees total_issues=0 and flips done=True on step 1.

True per-client concurrency is provided via Docker mode or the MCP WebSocket.
This is the same fix we landed in OpsTwin V1 — see GPU_HANDOFF.md history.
"""
import os
from openenv.core.env_server import create_fastapi_app

from models import F1Action, F1Observation
from server.environment import F1StrategistEnvironment

# Single shared environment instance. See module docstring for rationale.
_shared_env = F1StrategistEnvironment()

app = create_fastapi_app(lambda: _shared_env, F1Action, F1Observation)


# Optional Gradio web UI at /web
if os.environ.get("ENABLE_WEB_INTERFACE") == "1":
    try:
        from server.visualizer import build_gradio_panel
        gradio_app = build_gradio_panel(_shared_env)
        # Mount under /web — implementation provided by visualizer.py
    except ImportError:
        pass  # Gradio not installed; skip silently


def main():
    """Entry point for `uv run server` / pyproject [project.scripts]."""
    import uvicorn
    port = int(os.environ.get("F1_STRATEGIST_PORT", 8000))
    uvicorn.run("server.app:app", host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
