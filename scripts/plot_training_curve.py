"""Plot loss + reward curves from GRPO trainer_state.json.

Designed for the demo: smoothed reward trace with rolling mean, key
milestone annotations, and a clean dual-axis chart that reads well in
the README and blog post. Loss is plotted in log-space so LoRA-scale
deltas (1e-5 to 1e-4) are still legible.
"""

import argparse
import json
import statistics
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# Paddock palette
COLOR_LOSS = "#c1121f"          # red — Ferrari
COLOR_REWARD_RAW = "#a8c8e6"    # pale blue
COLOR_REWARD_SMOOTH = "#003e8a" # deep blue — Williams
COLOR_BAND = "#e8f1fa"
COLOR_GRID = "#cfcfcf"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", default="./grpo_v1")
    parser.add_argument("--output", default="results/training_loss_curve.png")
    parser.add_argument("--smooth-window", type=int, default=5,
                        help="Rolling-mean window for the reward trace")
    parser.add_argument("--title", default=None,
                        help="Override the default chart title")
    args = parser.parse_args()

    state_path = _find_state(Path(args.run_dir))
    state = json.loads(state_path.read_text(encoding="utf-8"))
    rows = [r for r in state.get("log_history", []) if "step" in r]
    if not rows:
        raise SystemExit(f"No plottable log_history rows in {state_path}")

    steps = [r["step"] for r in rows]
    losses = [r.get("loss") for r in rows]
    rewards = [r.get("reward", r.get("rewards/mean")) for r in rows]
    rewards_clean = [r for r in rewards if r is not None]
    rewards_smoothed = _rolling_mean(rewards, args.smooth_window)

    fig, ax_reward = plt.subplots(figsize=(11, 5.2), dpi=160)
    fig.patch.set_facecolor("white")

    # Reward band: ±1σ around the rolling mean
    if len(rewards_clean) >= 3:
        sd = statistics.pstdev(rewards_clean)
        upper = [v + sd if v is not None else None for v in rewards_smoothed]
        lower = [v - sd if v is not None else None for v in rewards_smoothed]
        valid = [(s, l, u) for s, l, u in zip(steps, lower, upper)
                 if l is not None and u is not None]
        if valid:
            xs, ls, us = zip(*valid)
            ax_reward.fill_between(xs, ls, us, color=COLOR_BAND, alpha=0.6,
                                   label="reward ±σ", zorder=1)

    # Raw reward (faint)
    if any(v is not None for v in rewards):
        ax_reward.plot(
            steps,
            [v if v is not None else float("nan") for v in rewards],
            color=COLOR_REWARD_RAW, linewidth=1.0, alpha=0.7,
            label="reward (raw)", zorder=2,
        )
    # Smoothed reward (bold)
    if any(v is not None for v in rewards_smoothed):
        ax_reward.plot(
            steps,
            [v if v is not None else float("nan") for v in rewards_smoothed],
            color=COLOR_REWARD_SMOOTH, linewidth=2.6,
            label=f"reward (smoothed, window={args.smooth_window})", zorder=4,
        )

    ax_reward.set_xlabel("Training step", fontsize=11)
    ax_reward.set_ylabel("Mean episode reward", color=COLOR_REWARD_SMOOTH,
                         fontsize=11, fontweight="bold")
    ax_reward.tick_params(axis="y", labelcolor=COLOR_REWARD_SMOOTH)
    ax_reward.grid(True, alpha=0.3, color=COLOR_GRID)
    ax_reward.set_axisbelow(True)

    # Auto-pad y-axis so the reward trace doesn't squish against the top
    if rewards_clean:
        rmin, rmax = min(rewards_clean), max(rewards_clean)
        pad = max(0.02, (rmax - rmin) * 0.5)
        ax_reward.set_ylim(max(0.0, rmin - pad), min(1.0, rmax + pad))

    # Loss on a secondary axis — log scale because LoRA loss stays tiny
    ax_loss = ax_reward.twinx()
    if any(v is not None and v > 0 for v in losses):
        positive_losses = [v if (v is not None and v > 1e-9) else float("nan")
                           for v in losses]
        ax_loss.plot(steps, positive_losses, color=COLOR_LOSS, linewidth=1.4,
                     alpha=0.85, label="loss (log scale)", zorder=3)
        ax_loss.set_yscale("log")
        ax_loss.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0e"))
    ax_loss.set_ylabel("Loss (log scale)", color=COLOR_LOSS,
                       fontsize=11, fontweight="bold")
    ax_loss.tick_params(axis="y", labelcolor=COLOR_LOSS)

    # Annotations: early/late/peak summary
    if rewards_clean:
        early_n = max(1, len(rewards_clean) // 10)
        late_n = max(1, len(rewards_clean) // 10)
        early_reward = statistics.mean(rewards_clean[:early_n])
        late_reward = statistics.mean(rewards_clean[-late_n:])
        delta = late_reward - early_reward
        peak_reward = max(rewards_clean)
        peak_idx = rewards.index(peak_reward) if peak_reward in rewards else 0
        peak_step = steps[peak_idx]

        headline = (
            f"early {early_reward:.3f} → late {late_reward:.3f}  (Δ {delta:+.3f})\n"
            f"peak {peak_reward:.3f} @ step {peak_step}"
        )
        ax_reward.text(
            0.02, 0.97, headline,
            transform=ax_reward.transAxes,
            fontsize=10.5, fontweight="bold",
            verticalalignment="top",
            color="#1a1a1a",
            bbox=dict(boxstyle="round,pad=0.5",
                      facecolor="white", edgecolor=COLOR_REWARD_SMOOTH,
                      linewidth=1.5, alpha=0.95),
            zorder=10,
        )

        # Mark the peak
        ax_reward.scatter([peak_step], [peak_reward], color="#ffd60a",
                          edgecolor=COLOR_REWARD_SMOOTH, s=140, zorder=11,
                          marker="*", label=f"peak ({peak_reward:.3f})")

    # Title
    title = args.title or f"GRPO training: {Path(args.run_dir).name}"
    ax_reward.set_title(title, fontsize=14, fontweight="bold", pad=14)

    # Combined legend
    lines_r, labels_r = ax_reward.get_legend_handles_labels()
    lines_l, labels_l = ax_loss.get_legend_handles_labels()
    fig.legend(lines_r + lines_l, labels_r + labels_l,
               loc="lower right", bbox_to_anchor=(0.98, 0.04),
               fontsize=9.5, framealpha=0.95)

    fig.tight_layout()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {output} from {state_path}")


def _rolling_mean(values, window: int) -> list:
    """Centered rolling mean. Returns same length; edges fall back to one-sided mean."""
    n = len(values)
    out = [None] * n
    half = window // 2
    for i in range(n):
        start = max(0, i - half)
        stop = min(n, i + half + 1)
        chunk = [v for v in values[start:stop] if v is not None]
        if chunk:
            out[i] = sum(chunk) / len(chunk)
    return out


def _find_state(run_dir: Path) -> Path:
    direct = run_dir / "trainer_state.json"
    if direct.exists():
        return direct
    candidates = sorted(run_dir.glob("checkpoint-*/trainer_state.json"))
    if candidates:
        return candidates[-1]
    raise SystemExit(f"No trainer_state.json found under {run_dir}")


if __name__ == "__main__":
    main()
