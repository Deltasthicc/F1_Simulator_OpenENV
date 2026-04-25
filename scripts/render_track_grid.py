"""Run the trained policy on multiple tracks and produce a montage.

Demonstrates that the trained F1 strategist generalises across the 26
tracks in our racetrack-database. Renders one rollout GIF per track and
then composites the final-lap stills into a single results/track_grid.png
that's perfect for the README and blog post hero.

Usage:
    python scripts/render_track_grid.py
    python scripts/render_track_grid.py --tracks Monza Spa Suzuka --task weather_roulette
    python scripts/render_track_grid.py --no-individual-gifs    # only the grid
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Default 8-track lineup spans every track character bucket
DEFAULT_TRACKS = [
    "Monza",         # power
    "Spa",           # weather_prone
    "Silverstone",   # balanced (high-speed)
    "Suzuka",        # balanced (figure-eight)
    "Spielberg",     # power (short)
    "Catalunya",     # balanced (reference)
    "Zandvoort",     # downforce (banked)
    "Sakhir",        # power (abrasive)
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tracks", nargs="+", default=DEFAULT_TRACKS)
    parser.add_argument("--task", default="dry_strategy_sprint")
    parser.add_argument("--mode", default="trained",
                        choices=["random", "untrained", "trained", "expert"])
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--no-individual-gifs", action="store_true",
                        help="Only emit the grid PNG, skip per-track GIFs")
    parser.add_argument("--output", default="results/track_grid.png")
    args = parser.parse_args()

    from server.scenarios import SCENARIOS
    from rollout import run_rollout

    # We need to override the scenario's track_name per run.
    base_scenario = SCENARIOS[args.task]
    captures = REPO_ROOT / "captures"
    captures.mkdir(parents=True, exist_ok=True)

    rollout_records = []
    for track in args.tracks:
        scenario_key = f"{args.task}__{track}"
        # Inject a fresh scenario with the desired track_name
        scenario = dict(base_scenario)
        scenario["track_name"] = track
        scenario["display_name"] = f"{track} — {args.task}"
        SCENARIOS[scenario_key] = scenario

        print(f"[track={track}] running rollout (mode={args.mode}, seed={args.seed})")
        try:
            score, jsonl_path = run_rollout(
                model="heuristic", task=scenario_key,
                seed=args.seed, mode=args.mode,
                render=not args.no_individual_gifs,
                verbose=False,
            )
        except Exception as exc:
            print(f"  [skip] {track}: {exc}")
            continue
        finally:
            SCENARIOS.pop(scenario_key, None)

        rollout_records.append((track, score, jsonl_path))

    if not rollout_records:
        raise SystemExit("No rollouts succeeded.")

    print(f"[grid] composing {len(rollout_records)} tracks into {args.output}")
    _build_grid_png(rollout_records, Path(args.output), args.task, args.mode)
    print(f"[done] wrote {args.output}")


def _build_grid_png(records, output: Path, task: str, mode: str) -> None:
    """Compose a 4-column grid of static track diagrams with score badges."""
    import matplotlib.pyplot as plt
    import numpy as np

    from server.track import load_track

    n = len(records)
    cols = 4 if n >= 4 else n
    rows = (n + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 3.6, rows * 3.4),
                             dpi=140, squeeze=False)
    fig.patch.set_facecolor("#fafafa")
    fig.suptitle(
        f"Trained policy across {n} tracks — task: {task.replace('_', ' ')}",
        fontsize=15, fontweight="bold", y=0.995,
    )

    for ax in axes.flat:
        ax.axis("off")

    for idx, (track_name, score, jsonl_path) in enumerate(records):
        r, c = idx // cols, idx % cols
        ax = axes[r][c]

        try:
            track = load_track(track_name)
        except FileNotFoundError:
            ax.set_title(track_name, fontsize=11)
            ax.text(0.5, 0.5, "(track not loadable)", transform=ax.transAxes,
                    ha="center", va="center", color="#999")
            continue

        xy = np.asarray(track.centerline)
        ax.plot(xy[:, 0], xy[:, 1], color="#1a1a1a", linewidth=2.0,
                solid_capstyle="round")
        ax.plot(xy[:, 0], xy[:, 1], color="#cfcfcf", linewidth=0.9)
        ax.set_aspect("equal", adjustable="box")
        ax.axis("off")

        # Replay marker: ego car at the final-lap point
        try:
            final_obs = _final_obs_from_jsonl(jsonl_path)
            lap = int(final_obs.get("current_lap", track.length_m * 0))
            total = max(1, int(final_obs.get("total_laps", 10)))
            tip_idx = int((lap / total) * (len(xy) - 1)) % len(xy)
            ax.scatter([xy[tip_idx, 0]], [xy[tip_idx, 1]],
                       s=130, color="#e10600", edgecolors="#1a1a1a",
                       linewidths=1.4, zorder=5)
        except Exception:
            pass

        # Score badge
        badge_color = "#1a8754" if score >= 0.85 else ("#ef8a17" if score >= 0.6 else "#c1121f")
        ax.set_title(f"{track_name}", fontsize=12, fontweight="bold", pad=4)
        ax.text(
            0.5, -0.05, f"score: {score:.2f}",
            transform=ax.transAxes,
            ha="center", va="top",
            fontsize=11, fontweight="bold",
            color="white",
            bbox=dict(boxstyle="round,pad=0.35",
                      facecolor=badge_color, edgecolor="none"),
        )

    fig.tight_layout(rect=[0, 0.02, 1, 0.97])
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=140, bbox_inches="tight")
    plt.close(fig)


def _final_obs_from_jsonl(path: Path) -> dict:
    last = None
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                last = json.loads(line)
    if not last:
        return {}
    return last.get("observation", last)


if __name__ == "__main__":
    main()
