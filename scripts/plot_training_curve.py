"""
Plot training loss + reward curves from a TRL run directory.

Owner: Person 2.

Reads:
    <run-dir>/trainer_state.json       — per-step metrics
    <run-dir>/checkpoint-*/trainer_state.json  — alternative location

Outputs:
    results/training_loss_curve.png

CLI:
    python scripts/plot_training_curve.py --run-dir ./grpo_v1
    python scripts/plot_training_curve.py --run-dir ./grpo_v1_stage3 --output results/training_loss_curve.png
"""
import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", default="./grpo_v1")
    parser.add_argument("--output", default="results/training_loss_curve.png")
    args = parser.parse_args()
    # TODO Phase 3:
    #   1. Find trainer_state.json (top-level or in latest checkpoint-*)
    #   2. Extract log_history → list of {step, loss, reward, ...}
    #   3. Plot loss + reward on twin axes
    #   4. Save to args.output
    print("plot_training_curve.py — TODO Phase 3, Person 2")


if __name__ == "__main__":
    main()
