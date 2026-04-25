"""
F1 Strategist — Single-Rollout Helper
=======================================

Runs one episode end-to-end with a given model + task + seed, prints a
chat-style transcript, and optionally renders the visualiser GIF.

Owner: Person 2 (drives) / Person 1 (renders).

TODO Phase 2/5:
    - run_rollout(model, task, seed, mode, render) -> (final_score, jsonl_path)
    - --render flag invokes server.visualizer.render_rollout
    - --verbose flag prints full chat transcript

CLI:
    python rollout.py --task dry_strategy_sprint --seed 0 --mode trained --render
"""
import argparse


def run_rollout(model: str, task: str, seed: int, mode: str, render: bool = False) -> float:
    raise NotImplementedError("Phase 2, Person 2")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="Qwen/Qwen3-0.6B")
    parser.add_argument("--task", default="dry_strategy_sprint")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--mode", choices=["random", "untrained", "trained", "expert"],
                        default="untrained")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    run_rollout(args.model, args.task, args.seed, args.mode, args.render)
