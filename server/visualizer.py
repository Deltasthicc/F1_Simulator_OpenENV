"""
F1 Strategist — Matplotlib Replay + Gradio Panel
=================================================

Two layers:
    1. render_rollout(jsonl_path, output_path, fmt) — top-down GIF/MP4 of any
       rollout. Used for blog/video/post-Space sanity checks.
    2. build_gradio_panel(env) — Gradio interface mounted under /web. Lets
       judges hit Reset and step the env interactively without writing client
       code.

Owner: Person 1.
Spec: docs/physics-model.md §visualisation, docs/build-order.md §Phase-5.

TODO Phase 5:
    - render_rollout: matplotlib FuncAnimation, blit=True for speed
    - track polygon from data/tracks/<n>.csv
    - cars as coloured circles animated along centerline
    - per-lap strip below: pit events, mode changes, weather, SC zones
    - text overlay each step: RADIO_DRIVER calls, inspection reveals
    - output GIF (blog) and MP4 (video)
    - build_gradio_panel: simple Reset/Action text input + JSON state display
"""
from pathlib import Path


def render_rollout(rollout_jsonl_path: Path, output_path: Path, fmt: str = "gif") -> None:
    """Animate a rollout. Saves to output_path. fmt = 'gif' or 'mp4'."""
    raise NotImplementedError("Phase 5, Person 1")


def build_gradio_panel(env):
    """Return a Gradio app for interactive demo. Mounted under /web."""
    raise NotImplementedError("Phase 5, Person 1")
