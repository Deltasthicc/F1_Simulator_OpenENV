"""Matplotlib rollout renderer and Gradio control panel."""

from __future__ import annotations

import json
from pathlib import Path


def render_rollout(rollout_jsonl_path: Path, output_path: Path, fmt: str = "gif") -> None:
    """Animate a rollout JSONL into a GIF or MP4."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation, PillowWriter
    import numpy as np

    from server.track import load_track

    rollout_jsonl_path = Path(rollout_jsonl_path)
    output_path = Path(output_path)
    frames = _read_rollout_frames(rollout_jsonl_path)
    if not frames:
        raise ValueError(f"No frames found in {rollout_jsonl_path}")

    track_name = frames[0].get("track_name") or frames[0].get("observation", {}).get("track_name") or "Monza"
    if "observation" in frames[0]:
        first_obs = frames[0]["observation"]
        track_name = first_obs.get("track_name", track_name)
    try:
        track = load_track(track_name)
    except FileNotFoundError:
        track = load_track("Monza")
    xy = track.centerline
    fig, (ax_track, ax_strip) = plt.subplots(
        2,
        1,
        figsize=(8, 7),
        gridspec_kw={"height_ratios": [4, 1]},
        constrained_layout=True,
    )
    ax_track.plot(xy[:, 0], xy[:, 1], color="#262626", linewidth=2.0)
    ax_track.set_aspect("equal", adjustable="box")
    ax_track.axis("off")
    ax_track.set_title(f"{track.name} rollout", fontsize=12)
    ego_dot, = ax_track.plot([], [], "o", color="#e10600", markersize=8, label="Ego")
    opp_dots = ax_track.scatter([], [], s=28, c="#1f77b4")
    label = ax_track.text(0.02, 0.98, "", transform=ax_track.transAxes, va="top", fontsize=9)

    ax_strip.set_xlim(0, max(1, _max_laps(frames)))
    ax_strip.set_ylim(0, 1)
    ax_strip.set_yticks([])
    ax_strip.set_xlabel("Lap")
    ax_strip.grid(axis="x", alpha=0.25)
    weather_bar = ax_strip.imshow(
        np.zeros((1, max(1, _max_laps(frames)), 3)),
        extent=[0, max(1, _max_laps(frames)), 0.05, 0.35],
        aspect="auto",
    )
    pit_marks = ax_strip.scatter([], [], marker="v", color="#e10600", s=50)

    def update(i: int):
        obs = _obs_from_frame(frames[i])
        lap = int(obs.get("current_lap", i))
        total_laps = max(1, int(obs.get("total_laps", _max_laps(frames))))
        idx = int((lap / total_laps) * (len(xy) - 1)) % len(xy)
        ego_dot.set_data([xy[idx, 0]], [xy[idx, 1]])

        opp_xy = []
        for j, _opp in enumerate(obs.get("opponents", [])[:8]):
            opp_idx = int(((lap / total_laps) + (j + 1) * 0.025) * (len(xy) - 1)) % len(xy)
            opp_xy.append([xy[opp_idx, 0], xy[opp_idx, 1]])
        opp_dots.set_offsets(np.array(opp_xy) if opp_xy else np.empty((0, 2)))

        message = obs.get("message", "")
        label.set_text(
            f"Lap {lap}/{total_laps} | P{obs.get('ego_position', '?')} | "
            f"{obs.get('ego_tyre_compound', '')} | {obs.get('race_status', '')}\n"
            f"{message[:95]}"
        )

        colors = np.zeros((1, total_laps, 3))
        for l in range(total_laps):
            frame_obs = _nearest_obs_for_lap(frames, l + 1)
            rain = frame_obs.get("weather_current", {}).get("rain_intensity", 0.0)
            colors[0, l, :] = [0.1, 0.45 + 0.4 * rain, 0.15 + 0.75 * rain]
        weather_bar.set_data(colors)

        pit_laps = [
            int(_obs_from_frame(f).get("current_lap", 0))
            for f in frames[: i + 1]
            if str(_obs_from_frame(f).get("message", "")).lower().startswith("box")
        ]
        pit_marks.set_offsets(np.array([[p, 0.72] for p in pit_laps]) if pit_laps else np.empty((0, 2)))
        return ego_dot, opp_dots, label, weather_bar, pit_marks

    anim = FuncAnimation(fig, update, frames=len(frames), interval=500, blit=False)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "mp4" or output_path.suffix.lower() == ".mp4":
        anim.save(output_path, fps=2)
    else:
        anim.save(output_path, writer=PillowWriter(fps=2))
    plt.close(fig)


def build_gradio_panel(env):
    """Return a Gradio Blocks app for interactive demos."""
    import gradio as gr

    def reset(task: str, seed: int):
        obs = env.reset(task=task, seed=int(seed))
        return obs.model_dump()

    def step(command: str):
        from models import F1Action

        obs = env.step(F1Action(command=command))
        return obs.model_dump()

    with gr.Blocks(title="F1 Strategist") as demo:
        gr.Markdown("# F1 Strategist")
        with gr.Row():
            task = gr.Dropdown(
                choices=["dry_strategy_sprint", "weather_roulette", "late_safety_car", "championship_decider"],
                value="dry_strategy_sprint",
                label="Scenario",
            )
            seed = gr.Number(value=42, precision=0, label="Seed")
            reset_btn = gr.Button("Reset", variant="primary")
        with gr.Row():
            command = gr.Textbox(value="STAY_OUT", label="Command")
            step_btn = gr.Button("Step")
        state = gr.JSON(label="Observation")
        reset_btn.click(reset, inputs=[task, seed], outputs=state)
        step_btn.click(step, inputs=command, outputs=state)
    return demo


def _read_rollout_frames(path: Path) -> list[dict]:
    frames = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            frames.append(json.loads(line))
    return frames


def _obs_from_frame(frame: dict) -> dict:
    return frame.get("observation", frame)


def _max_laps(frames: list[dict]) -> int:
    return max(int(_obs_from_frame(f).get("total_laps", _obs_from_frame(f).get("current_lap", 1))) for f in frames)


def _nearest_obs_for_lap(frames: list[dict], lap: int) -> dict:
    obs_rows = [_obs_from_frame(f) for f in frames]
    return min(obs_rows, key=lambda obs: abs(int(obs.get("current_lap", 0)) - lap))
