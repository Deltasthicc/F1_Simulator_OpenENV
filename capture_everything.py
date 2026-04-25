"""Generate SFT chat data from expert trajectories."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from baselines.expert_solver import ExpertSolver
from inference import SYSTEM_PROMPT, format_obs
from server.environment import F1StrategistEnvironment
from server.generator import generate
from server.scenarios import SCENARIOS


def main(args) -> None:
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True) if output.parent != Path(".") else None
    n = 0
    with output.open("w", encoding="utf-8") as f:
        for task in args.tasks:
            for seed in range(args.n_seeds):
                scenario = generate(task, seed) if args.procedural else SCENARIOS[task]
                env = F1StrategistEnvironment()
                obs = env.reset(seed=seed, options={"scenario": scenario})
                for action in ExpertSolver().solve(scenario, env):
                    row = {
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": format_obs(obs)},
                            {"role": "assistant", "content": action.command},
                        ],
                        "task": scenario["scenario_family"],
                        "seed": seed,
                        "lap": obs.current_lap,
                    }
                    f.write(json.dumps(row) + "\n")
                    n += 1
                    obs = env.step(action)
                    if obs.done:
                        break
    print(f"wrote {n} SFT turns to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tasks",
        nargs="+",
        default=[
            "dry_strategy_sprint",
            "weather_roulette",
            "late_safety_car",
            "championship_decider",
        ],
    )
    parser.add_argument("--n-seeds", type=int, default=100)
    parser.add_argument("--output", default="sft_dataset_v1.jsonl")
    parser.add_argument(
        "--procedural",
        action="store_true",
        help="Use server.generator variants instead of templates.",
    )
    main(parser.parse_args())
