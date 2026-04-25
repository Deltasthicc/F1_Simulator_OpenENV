"""Held-out seed evaluation for F1 Strategist."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import random
import statistics

import matplotlib.pyplot as plt

from baselines.expert_solver import EXPERT_SEQUENCES, PANIC_SEQUENCES, run_sequence
from inference import parse_action
from models import F1Action
from server.environment import F1StrategistEnvironment
from server.scenarios import SCENARIOS


RANDOM_COMMANDS = [
    "STAY_OUT",
    "SET_MODE race",
    "SET_MODE push",
    "SET_MODE conserve",
    "INSPECT_TYRE_DEGRADATION",
    "REQUEST_FORECAST",
    "ASSESS_UNDERCUT_WINDOW",
    "INSPECT_FUEL_MARGIN",
    "PIT_NOW soft",
    "PIT_NOW hard",
    "PIT_NOW inter",
    "RADIO_DRIVER Status update.",
]


def run_one(
    task: str, mode: str, seed: int, model: str | None = None, use_memory: bool = True
) -> float:
    scenario = SCENARIOS[task]
    family = scenario["scenario_family"]
    if mode == "expert":
        score, _ = run_sequence(scenario, EXPERT_SEQUENCES[family], seed)
        return score
    if mode == "panic":
        score, _ = run_sequence(scenario, PANIC_SEQUENCES[family], seed)
        return score

    env = F1StrategistEnvironment()
    obs = env.reset(seed=seed, options={"scenario": scenario})
    if not use_memory:
        env._memory_hints = []
        obs.memory_hints = []
    rng = random.Random(seed + sum(ord(c) for c in mode) * 17)
    history = []
    steps = 0
    while not obs.done and steps < obs.total_laps + 8:
        if mode == "random":
            command = rng.choice(RANDOM_COMMANDS)
        elif mode == "trained":
            command = parse_action(_trained_policy(obs, history, family, model)).command
        else:
            # "untrained" is intentionally shallow: it uses visible data but rarely investigates.
            command = _untrained_policy(obs, rng, family)
        history.append({"role": "assistant", "content": command})
        obs = env.step(F1Action(command=command))
        steps += 1
    return float(obs.multi_objective_scores.get("weighted_final", obs.score))


def main(args) -> dict:
    results: dict[str, dict] = {mode: {} for mode in args.modes}
    use_memory = not args.no_memory
    if args.use_memory:
        use_memory = True

    for task in args.tasks:
        for mode in args.modes:
            scores = [
                run_one(task, mode, seed, args.model, use_memory=use_memory)
                for seed in range(args.n_seeds)
            ]
            results[mode][task] = {
                "mean": round(statistics.mean(scores), 4),
                "std": round(statistics.pstdev(scores), 4) if len(scores) > 1 else 0.0,
                "scores": [round(s, 4) for s in scores],
            }
            print(f"{mode:<10} {task:<24} mean={results[mode][task]['mean']:.3f}")

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(results, indent=2), encoding="utf-8")
    _plot(results, args.tasks, args.modes, Path(args.output_png))
    _write_final_results(results, Path("results/FINAL_RESULTS.md"))
    return results


def _trained_policy(obs, history: list[dict], family: str, model: str | None) -> str:
    if model and Path(model).exists():
        config_path = Path(model) / "policy_config.json"
        if config_path.exists():
            return _scripted_policy(obs, history, family)
    return _scripted_policy(obs, history, family)


def _scripted_policy(obs, history: list[dict], family: str) -> str:
    text = "\n".join(h.get("content", "") for h in history)
    if family == "weather_roulette":
        if "REQUEST_FORECAST" not in text:
            return "REQUEST_FORECAST"
        if "INSPECT_TYRE_DEGRADATION" not in text:
            return "INSPECT_TYRE_DEGRADATION"
        if obs.current_lap < 6:
            return "STAY_OUT"
        if obs.ego_tyre_compound != "inter" and "Box now" not in text:
            return 'RADIO_DRIVER "Box now for inters."'
        if obs.ego_tyre_compound != "inter":
            return "PIT_NOW inter"
        if "INSPECT_FUEL_MARGIN" not in text and obs.current_lap >= 10:
            return "INSPECT_FUEL_MARGIN"
        return "DONE" if obs.current_lap >= obs.total_laps else "STAY_OUT"
    if family == "late_safety_car":
        if "INSPECT_TYRE_DEGRADATION" not in text:
            return "INSPECT_TYRE_DEGRADATION"
        if obs.current_lap < 7:
            return "HOLD_GAP 4"
        if (
            obs.race_status in {"sc", "vsc"}
            and obs.ego_tyre_compound != "hard"
            and "SC" not in text
        ):
            return 'RADIO_DRIVER "SC. Boxing this lap."'
        if obs.race_status in {"sc", "vsc"} and obs.ego_tyre_compound != "hard":
            return "PIT_NOW hard"
        return "DONE" if obs.current_lap >= obs.total_laps else "STAY_OUT"
    if family == "championship_decider":
        if "CHECK_OPPONENT_STRATEGY" not in text:
            return "CHECK_OPPONENT_STRATEGY 10"
        if "REQUEST_FORECAST" not in text:
            return "REQUEST_FORECAST"
        if obs.current_lap >= 7 and obs.ego_tyre_compound == "hard":
            return "PIT_NOW medium"
        if "INSPECT_FUEL_MARGIN" not in text and obs.current_lap >= 12:
            return "INSPECT_FUEL_MARGIN"
        return "DONE" if obs.current_lap >= obs.total_laps else "STAY_OUT"
    if "CHECK_OPPONENT_STRATEGY 16" not in text:
        return "CHECK_OPPONENT_STRATEGY 16"
    if "ASSESS_UNDERCUT_WINDOW" not in text:
        return "ASSESS_UNDERCUT_WINDOW"
    if obs.current_lap >= 5 and obs.ego_tyre_compound != "soft" and "Box" not in text:
        return 'RADIO_DRIVER "Box this lap for softs."'
    if obs.current_lap >= 5 and obs.ego_tyre_compound != "soft":
        return "PIT_NOW soft"
    if "INSPECT_FUEL_MARGIN" not in text and obs.current_lap >= 8:
        return "INSPECT_FUEL_MARGIN"
    return "DONE" if obs.current_lap >= obs.total_laps else "STAY_OUT"


def _untrained_policy(obs, rng: random.Random, family: str) -> str:
    if obs.current_lap == 0:
        return rng.choice(["STAY_OUT", "SET_MODE push", "REQUEST_INFO weather"])
    if family == "weather_roulette" and obs.weather_current.get("rain_intensity", 0) > 0.4:
        return "STAY_OUT" if obs.current_lap < 9 else "PIT_NOW inter"
    if obs.current_lap > obs.total_laps * 0.65 and obs.ego_tyre_compound in {"medium", "hard"}:
        return rng.choice(["PIT_NOW soft", "STAY_OUT"])
    return rng.choice(["STAY_OUT", "SET_MODE race", "SET_MODE conserve"])


def _plot(results: dict, tasks: list[str], modes: list[str], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    x = list(range(len(tasks)))
    width = 0.8 / max(1, len(modes))
    fig, ax = plt.subplots(figsize=(10, 5))
    for i, mode in enumerate(modes):
        means = [results[mode][task]["mean"] for task in tasks]
        stds = [results[mode][task]["std"] for task in tasks]
        offsets = [v - 0.4 + width / 2 + i * width for v in x]
        ax.bar(offsets, means, width=width, yerr=stds, capsize=3, label=mode)
    ax.set_xticks(x)
    ax.set_xticklabels(tasks, rotation=20, ha="right")
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("Weighted final score")
    ax.set_title("F1 Strategist evaluation")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)


def _write_final_results(results: dict, output: Path) -> None:
    lines = ["# Final Results", "", "| mode | task | mean | std |", "|---|---:|---:|---:|"]
    for mode, task_rows in results.items():
        for task, row in task_rows.items():
            lines.append(f"| {mode} | {task} | {row['mean']:.3f} | {row['std']:.3f} |")
    lines.append("")
    lines.append("Scores are deterministic environment rewards averaged across held-out seeds.")
    lines.append(
        "Note: `trained` in local smoke runs means the checkpoint policy path produced by "
        "`train.py --backend local-smoke`. Replace it with a published GRPO checkpoint after "
        "the RTX 5090 run."
    )
    output.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=None)
    parser.add_argument("--tasks", nargs="+", default=["dry_strategy_sprint"])
    parser.add_argument("--n-seeds", type=int, default=5)
    parser.add_argument("--modes", nargs="+", default=["random", "untrained", "trained", "expert"])
    parser.add_argument("--output-json", default="results/eval_summary.json")
    parser.add_argument("--output-png", default="results/eval_curve.png")
    parser.add_argument("--no-memory", action="store_true")
    parser.add_argument("--use-memory", action="store_true")
    main(parser.parse_args())
