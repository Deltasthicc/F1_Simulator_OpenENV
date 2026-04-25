"""
Diff two evaluate.py JSON outputs to produce an ablation comparison.

Owner: Person 2.

Used for the postmortem ablation in Phase 4: compare base trained vs memory-
augmented on the same tasks/seeds.

CLI:
    python scripts/diff_ablation.py \\
        results/ablation_no_memory.json \\
        results/ablation_with_memory.json \\
        --output results/ablation.md
"""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("base", help="Baseline JSON")
    parser.add_argument("variant", help="Variant JSON")
    parser.add_argument("--output", default="results/ablation.md")
    args = parser.parse_args()
    # TODO Phase 4:
    #   load both JSONs, compute mean delta per task, write a markdown table
    print("diff_ablation.py — TODO Phase 4, Person 2")


if __name__ == "__main__":
    main()
