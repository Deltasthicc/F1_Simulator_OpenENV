"""
F1 Strategist — Held-Out Seed Evaluation
==========================================

Runs random / untrained / trained / expert across N held-out seeds for each
scenario. Outputs canonical numbers (JSON) and a four-bar grouped chart (PNG).

Owner: Person 2.
Spec: docs/build-order.md §Phase-3, TRAINING.md.

TODO Phase 3:
    - run_one(task, mode, seed, model) → final score
    - Aggregate: mean, std per (mode, task)
    - JSON output: results/eval_summary.json
    - PNG output: results/eval_curve.png (matplotlib grouped bar chart with error bars)
    - argparse: --model, --tasks, --n-seeds, --modes, --output-json, --output-png,
        --no-memory, --use-memory (for the postmortem ablation)

CLI:
    python evaluate.py --model Deltasthic/f1-strategist-qwen3-4b-grpo \\
        --tasks dry_strategy_sprint weather_roulette late_safety_car championship_decider \\
        --n-seeds 5 --modes random untrained trained expert
"""
import argparse


def run_one(task: str, mode: str, seed: int, model: str | None) -> float:
    raise NotImplementedError("Phase 3, Person 2")


def main(args):
    raise NotImplementedError("Phase 3, Person 2")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=None)
    parser.add_argument("--tasks", nargs="+", default=["dry_strategy_sprint"])
    parser.add_argument("--n-seeds", type=int, default=5)
    parser.add_argument("--modes", nargs="+",
                        default=["random", "untrained", "trained", "expert"])
    parser.add_argument("--output-json", default="results/eval_summary.json")
    parser.add_argument("--output-png", default="results/eval_curve.png")
    parser.add_argument("--no-memory", action="store_true")
    parser.add_argument("--use-memory", action="store_true")
    main(parser.parse_args())
