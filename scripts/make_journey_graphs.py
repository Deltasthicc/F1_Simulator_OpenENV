"""Generate the ship-time graphs that tell our journey story.

Outputs:
  results/journey.png            — overall avg per iteration (line chart)
  results/scenario_breakdown.png — 4 scenarios × 4-5 iterations (grouped bars)
  results/comparison_real.png    — main-reported (scripted) vs main-actual vs ours vs expert
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

RESULTS = Path("results")

TASKS = ["dry_strategy_sprint", "weather_roulette", "late_safety_car", "championship_decider"]
TASK_LABELS = ["dry sprint", "weather", "safety car", "champ decider"]


def load_means(path: Path, mode: str = "trained") -> list[float]:
    """Load per-task means from an eval_*.json file."""
    data = json.loads(path.read_text())
    return [data[mode][t]["mean"] for t in TASKS]


# ------------------------------------------------------------
# Data points (sourced from results/eval_*.json that we ran)
# ------------------------------------------------------------

# Baselines (from the most recent results/eval_summary.json — has random + untrained + expert)
summary = json.loads((RESULTS / "eval_summary.json").read_text())
RANDOM = [summary["random"][t]["mean"] for t in TASKS]
UNTRAINED = [summary["untrained"][t]["mean"] for t in TASKS]
EXPERT = [summary["expert"][t]["mean"] for t in TASKS]

# main FINAL_RESULTS.md "trained" — these are SCRIPTED-FALLBACK numbers
# (verified bit-exact by running scripted policy with no model)
MAIN_REPORTED = [0.749, 0.935, 0.935, 0.535]

# Shashwat's actual HF model run through real-LLM eval
MAIN_ACTUAL = load_means(RESULTS / "eval_shashwat.json")

# Our iterations
ORIG_GRPO = [0.520, 0.560, 0.550, 0.520]  # grpo_v1 (original) at greedy
SFT_V3 = load_means(RESULTS / "eval_sft_v3.json")
RFT_V1_T03 = load_means(RESULTS / "eval_rft_t03.json")
GRPO_V2 = load_means(RESULTS / "eval_grpo_v2.json")  # CHAMPION


# ------------------------------------------------------------
# 1. Journey line chart — avg score across iterations
# ------------------------------------------------------------

iterations = [
    ("random", RANDOM),
    ("untrained\nQwen3-4B", UNTRAINED),
    ("Shashwat's\nGRPO 500\n(real LLM)", MAIN_ACTUAL),
    ("Our\nSFT v3", SFT_V3),
    ("Our\nRFT v1\n(T=0.3)", RFT_V1_T03),
    ("Our\nGRPO v2\n★", GRPO_V2),
    ("Expert\n(rule-based)", EXPERT),
]
labels = [name for name, _ in iterations]
avgs = [sum(scores) / len(scores) for _, scores in iterations]

fig, ax = plt.subplots(figsize=(11, 5.5))
colors = ["#888888", "#5B7DA8", "#D67A1F", "#7BAFD4", "#9CC68F", "#C7423F", "#2A6F2A"]
xs = list(range(len(labels)))
ax.plot(xs, avgs, marker="o", linewidth=2.5, color="#333333", zorder=2)
for i, (x, y, c) in enumerate(zip(xs, avgs, colors)):
    ax.scatter([x], [y], s=240, color=c, edgecolor="black", linewidth=1.4, zorder=3)
    label = f"{y:.3f}"
    offset = 12 if i != 5 else -22  # push GRPO v2 label below line for emphasis
    ax.annotate(label, (x, y), textcoords="offset points",
                xytext=(0, offset), ha="center", fontsize=10, fontweight="bold")

ax.set_xticks(xs)
ax.set_xticklabels(labels, fontsize=9)
ax.set_ylabel("Average weighted_final score (4 scenarios × 5 seeds)", fontsize=10)
ax.set_title("F1 Strategist — training journey: random → expert\n(★ = our shipping checkpoint)",
             fontsize=12, fontweight="bold")
ax.set_ylim(0.2, 1.0)
ax.grid(True, axis="y", linestyle="--", alpha=0.4)
ax.axhline(y=avgs[-1], linestyle=":", color="#2A6F2A", alpha=0.5, label="expert ceiling")
ax.axhline(y=avgs[1], linestyle=":", color="#5B7DA8", alpha=0.5, label="untrained baseline")
ax.legend(loc="lower right", fontsize=9)
plt.tight_layout()
plt.savefig(RESULTS / "journey.png", dpi=140, bbox_inches="tight")
plt.close(fig)
print(f"Wrote {RESULTS / 'journey.png'}")


# ------------------------------------------------------------
# 2. Scenario-breakdown grouped bar chart
# ------------------------------------------------------------

groups = {
    "random": RANDOM,
    "untrained": UNTRAINED,
    "Shashwat\n(real)": MAIN_ACTUAL,
    "SFT v3": SFT_V3,
    "RFT v1 T=0.3": RFT_V1_T03,
    "GRPO v2 ★": GRPO_V2,
    "expert": EXPERT,
}

fig, ax = plt.subplots(figsize=(13, 5.5))
n_groups = len(groups)
bar_w = 0.11
xs = np.arange(len(TASKS))
group_colors = ["#888888", "#5B7DA8", "#D67A1F", "#7BAFD4", "#9CC68F", "#C7423F", "#2A6F2A"]

for i, ((name, scores), color) in enumerate(zip(groups.items(), group_colors)):
    offset = (i - (n_groups - 1) / 2) * bar_w
    bars = ax.bar(xs + offset, scores, bar_w, label=name, color=color,
                  edgecolor="black", linewidth=0.6)
    if name == "GRPO v2 ★":  # annotate champion
        for x, s in zip(xs + offset, scores):
            ax.text(x, s + 0.018, f"{s:.2f}", ha="center", fontsize=8, fontweight="bold",
                    color="#C7423F")

ax.set_xticks(xs)
ax.set_xticklabels(TASK_LABELS, fontsize=10)
ax.set_ylabel("weighted_final score", fontsize=10)
ax.set_title("Per-scenario performance across the journey",
             fontsize=12, fontweight="bold")
ax.set_ylim(0, 1.05)
ax.grid(True, axis="y", linestyle="--", alpha=0.4)
ax.legend(loc="upper right", ncol=2, fontsize=9)
plt.tight_layout()
plt.savefig(RESULTS / "scenario_breakdown.png", dpi=140, bbox_inches="tight")
plt.close(fig)
print(f"Wrote {RESULTS / 'scenario_breakdown.png'}")


# ------------------------------------------------------------
# 3. Comparison: main reported (scripted) vs main actual vs ours vs expert
# ------------------------------------------------------------

groups2 = {
    "main\n(reported,\nscripted fallback)": MAIN_REPORTED,
    "main\n(actual LLM)": MAIN_ACTUAL,
    "OURS\n(GRPO v2)": GRPO_V2,
    "expert ceiling": EXPERT,
}
colors2 = ["#D67A1F", "#888888", "#C7423F", "#2A6F2A"]

fig, ax = plt.subplots(figsize=(11, 5.5))
n = len(groups2)
bar_w = 0.18
xs = np.arange(len(TASKS))
for i, ((name, scores), color) in enumerate(zip(groups2.items(), colors2)):
    offset = (i - (n - 1) / 2) * bar_w
    bars = ax.bar(xs + offset, scores, bar_w, label=name, color=color,
                  edgecolor="black", linewidth=0.6)
    for x, s in zip(xs + offset, scores):
        ax.text(x, s + 0.012, f"{s:.2f}", ha="center", fontsize=8)

# Note about main's reported numbers
ax.text(
    0.02, 0.98,
    "main's 'reported' numbers came from a hand-coded scripted-policy\n"
    "fallback (LoRA dirs lack config.json → silent fall-through). Verified\n"
    "bit-exact by running the scripted policy with no model loaded.",
    transform=ax.transAxes, fontsize=8.5, va="top",
    bbox=dict(boxstyle="round,pad=0.4", fc="#FFF7E0", ec="#888888"),
)

ax.set_xticks(xs)
ax.set_xticklabels(TASK_LABELS, fontsize=10)
ax.set_ylabel("weighted_final score", fontsize=10)
ax.set_title("Reality check: what main reported vs what the model actually does",
             fontsize=12, fontweight="bold")
ax.set_ylim(0, 1.05)
ax.grid(True, axis="y", linestyle="--", alpha=0.4)
ax.legend(loc="lower right", fontsize=9)
plt.tight_layout()
plt.savefig(RESULTS / "comparison_real.png", dpi=140, bbox_inches="tight")
plt.close(fig)
print(f"Wrote {RESULTS / 'comparison_real.png'}")

# ------------------------------------------------------------
# Print a summary table for the blog/README
# ------------------------------------------------------------
print("\n--- avg per iteration ---")
for name, scores in iterations:
    avg = sum(scores) / len(scores)
    print(f"  {name.replace(chr(10), ' '):<35}  avg={avg:.3f}")
