"""
F1 Strategist — Bulk Rollout Capture (SFT Seed Data)
======================================================

Generates SFT training data by running the rule-based expert solver on N seeds
across every scenario family. Output: a JSONL of (prompt, response) pairs
suitable for warm-start SFT before GRPO.

Owner: Person 2.
Spec: TRAINING.md §three-stage-training §Stage-1.

TODO Phase 3:
    - For each (family, seed) tuple:
        - reset env
        - run expert_solver, collect (obs, action) pairs
        - format as chat: [{"role": "user", "content": format_obs(obs)},
                            {"role": "assistant", "content": action.command}]
        - serialise to jsonl
    - argparse: --tasks, --n-seeds, --output

CLI:
    python capture_everything.py \\
        --tasks dry_strategy_sprint weather_roulette late_safety_car championship_decider \\
        --n-seeds 100 \\
        --output sft_dataset_v1.jsonl
"""
import argparse


def main(args):
    raise NotImplementedError("Phase 3, Person 2")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", nargs="+",
                        default=["dry_strategy_sprint", "weather_roulette",
                                 "late_safety_car", "championship_decider"])
    parser.add_argument("--n-seeds", type=int, default=100)
    parser.add_argument("--output", default="sft_dataset_v1.jsonl")
    main(parser.parse_args())
