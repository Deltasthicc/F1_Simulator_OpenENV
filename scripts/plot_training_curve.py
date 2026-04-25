"""Plot loss and reward curves from trainer_state.json."""

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", default="./grpo_v1")
    parser.add_argument("--output", default="results/training_loss_curve.png")
    args = parser.parse_args()
    state_path = _find_state(Path(args.run_dir))
    state = json.loads(state_path.read_text(encoding="utf-8"))
    rows = [r for r in state.get("log_history", []) if "step" in r]
    if not rows:
        raise SystemExit(f"No plottable log_history rows in {state_path}")
    steps = [r["step"] for r in rows]
    losses = [r.get("loss") for r in rows]
    rewards = [r.get("reward", r.get("rewards/mean")) for r in rows]

    fig, ax1 = plt.subplots(figsize=(9, 4.8))
    if any(v is not None for v in losses):
        ax1.plot(
            steps,
            [v if v is not None else float("nan") for v in losses],
            color="#c1121f",
            label="loss",
        )
    ax1.set_xlabel("step")
    ax1.set_ylabel("loss", color="#c1121f")
    ax2 = ax1.twinx()
    if any(v is not None for v in rewards):
        ax2.plot(
            steps,
            [v if v is not None else float("nan") for v in rewards],
            color="#0077b6",
            label="reward",
        )
    ax2.set_ylabel("reward", color="#0077b6")
    ax1.set_title(f"Training curve: {Path(args.run_dir).name}")
    fig.tight_layout()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=160)
    plt.close(fig)
    print(f"wrote {output} from {state_path}")


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
