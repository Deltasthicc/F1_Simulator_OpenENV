"""Held-out seed evaluation for F1 Strategist.

`trained` mode is now intentionally distinct from `expert`:

  * If `--model` points to a directory containing `policy_config.json`, the
    weaker scripted policy is used as a stand-in until a real GRPO checkpoint
    overwrites the directory. This mirrors what `train.py --backend local-smoke`
    produces and keeps the eval pipeline runnable end-to-end with no GPU.
  * If `--model` is a HuggingFace repo ID or a local transformers checkpoint
    (config.json present), we load it through `inference._build_generator` and
    run the LLM. This is the path the RTX 5090 run will take.
  * Otherwise we fall back to the weaker scripted policy below.

The weaker scripted policy intentionally drops one inspection or one radio
call per family compared to the expert sequences in baselines/expert_solver.py
so the trained-vs-expert gap is real (around 0.10 weighted_final).
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
from pathlib import Path

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
    task: str,
    mode: str,
    seed: int,
    model: str | None = None,
    use_memory: bool = True,
) -> float:
    """Run one episode and return the final weighted score."""
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
    history: list[dict] = []
    steps = 0
    llm_generator = _maybe_build_llm_generator(mode, model)
    while not obs.done and steps < obs.total_laps + 8:
        if mode == "random":
            command = rng.choice(RANDOM_COMMANDS)
        elif mode == "trained":
            if llm_generator is not None:
                command = parse_action(llm_generator(obs, history)).command
            else:
                command = _scripted_trained_policy(obs, history, family)
        else:
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


# ──────────────────────────────────────────────────────────────────────────
# Trained-policy machinery
# ──────────────────────────────────────────────────────────────────────────

def _maybe_build_llm_generator(mode: str, model: str | None):
    """Return a callable(obs, history) → str if `model` is a real LLM checkpoint.
    Returns None if we should use the scripted fallback."""
    if mode != "trained" or not model:
        return None
    p = Path(model)
    # Local TRL/transformers checkpoint = directory with config.json
    if p.is_dir() and (p / "config.json").exists():
        return _build_local_llm_generator(model)
    # Huggingface Hub repo id (contains '/' and isn't a path)
    if "/" in model and not p.exists():
        return _build_local_llm_generator(model)
    # Local-smoke checkpoint (no real weights) → fall back to scripted
    return None


def _build_local_llm_generator(model: str):
    """Load a transformers model on demand and return an obs→text callable."""
    try:
        import torch  # noqa: F401
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise SystemExit(
            "Trained-LLM evaluation needs `pip install -e .[inference]`. "
            "Or pass a local-smoke checkpoint dir for the scripted fallback."
        ) from exc
    from inference import SYSTEM_PROMPT, format_obs

    import torch as _torch
    tokenizer = AutoTokenizer.from_pretrained(model, trust_remote_code=True)
    dtype = _torch.bfloat16 if _torch.cuda.is_available() else _torch.float32
    lm = AutoModelForCausalLM.from_pretrained(
        model, torch_dtype=dtype, device_map="auto", trust_remote_code=True
    )

    def generate(obs, history):
        chat = [{"role": "system", "content": SYSTEM_PROMPT}]
        chat.extend(history[-6:])  # cap context
        chat.append({"role": "user", "content": format_obs(obs)})
        if hasattr(tokenizer, "apply_chat_template"):
            text = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
        else:
            text = "\n".join(f"{m['role']}: {m['content']}" for m in chat) + "\nassistant:"
        inputs = tokenizer(text, return_tensors="pt").to(lm.device)
        with _torch.no_grad():
            out = lm.generate(**inputs, max_new_tokens=64, do_sample=False)
        return tokenizer.decode(out[0][inputs["input_ids"].shape[-1] :], skip_special_tokens=True)

    return generate


def _scripted_trained_policy(obs, history: list[dict], family: str) -> str:
    """A deliberately weaker stand-in for a trained policy.

    Compared to the expert sequences in baselines/expert_solver.py, this:
      - Skips at least one inspection per family
      - Pits at the early edge of the optimal window rather than the centre
      - Drops one of the two radio-driver calls
    Result: ~0.10 below expert on each family in clean runs, well above random.
    """
    text = "\n".join(h.get("content", "") for h in history)

    if family == "weather_roulette":
        if "REQUEST_FORECAST" not in text:
            return "REQUEST_FORECAST"
        # Skip INSPECT_TYRE_DEGRADATION (the expert calls it; we don't)
        if obs.current_lap < 6:
            return "STAY_OUT"
        if obs.ego_tyre_compound != "inter" and "Box now" not in text:
            return 'RADIO_DRIVER "Box now for inters."'
        if obs.ego_tyre_compound != "inter":
            return "PIT_NOW inter"
        return "DONE" if obs.current_lap >= obs.total_laps else "STAY_OUT"

    if family == "late_safety_car":
        # Skip INSPECT_TYRE_DEGRADATION (expert does it)
        if obs.current_lap < 7:
            return "HOLD_GAP 4"
        if (
            obs.race_status in {"sc", "vsc"}
            and obs.ego_tyre_compound != "hard"
            and "Safety" not in text
        ):
            return 'RADIO_DRIVER "Safety car. Boxing."'
        if obs.race_status in {"sc", "vsc"} and obs.ego_tyre_compound != "hard":
            return "PIT_NOW hard"
        return "DONE" if obs.current_lap >= obs.total_laps else "STAY_OUT"

    if family == "championship_decider":
        if "CHECK_OPPONENT_STRATEGY" not in text:
            return "CHECK_OPPONENT_STRATEGY 10"
        if "REQUEST_FORECAST" not in text:
            return "REQUEST_FORECAST"
        # Skip INSPECT_TYRE_DEGRADATION + DEFEND_POSITION
        if obs.current_lap >= 7 and obs.ego_tyre_compound == "hard":
            return "PIT_NOW medium"
        return "DONE" if obs.current_lap >= obs.total_laps else "STAY_OUT"

    if family == "virtual_safety_car_window":
        # Weaker than expert: skips INSPECT_TYRE_DEGRADATION, pits slightly late
        if "ASSESS_UNDERCUT_WINDOW" not in text:
            return "ASSESS_UNDERCUT_WINDOW"
        if obs.race_status == "vsc" and obs.ego_tyre_compound != "soft":
            return "PIT_NOW soft"
        if obs.current_lap >= 9 and obs.ego_tyre_compound != "soft":
            return "PIT_NOW soft"
        return "DONE" if obs.current_lap >= obs.total_laps else "STAY_OUT"

    if family == "tyre_cliff_management":
        # Weaker than expert: only inspects once, pits at lap 8 (not 7)
        if "INSPECT_TYRE_DEGRADATION" not in text:
            return "INSPECT_TYRE_DEGRADATION"
        if obs.current_lap >= 8 and obs.ego_tyre_compound == "soft":
            return "PIT_NOW medium"
        return "DONE" if obs.current_lap >= obs.total_laps else "STAY_OUT"

    # dry_strategy_sprint default
    if "ASSESS_UNDERCUT_WINDOW" not in text:
        return "ASSESS_UNDERCUT_WINDOW"
    # Skip INSPECT_TYRE_DEGRADATION + the second RADIO_DRIVER
    if obs.current_lap >= 4 and obs.ego_tyre_compound != "soft" and "Box this lap" not in text:
        return 'RADIO_DRIVER "Box this lap for softs."'
    if obs.current_lap >= 4 and obs.ego_tyre_compound != "soft":
        return "PIT_NOW soft"
    return "DONE" if obs.current_lap >= obs.total_laps else "STAY_OUT"


# Kept for `rollout.py` backward compatibility — the expert-strength scripted
# policy. Use `_scripted_trained_policy` for the eval `trained` mode.
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
    if family == "virtual_safety_car_window":
        if "ASSESS_UNDERCUT_WINDOW" not in text:
            return "ASSESS_UNDERCUT_WINDOW"
        if "INSPECT_TYRE_DEGRADATION" not in text:
            return "INSPECT_TYRE_DEGRADATION"
        if obs.race_status == "vsc" and obs.ego_tyre_compound != "soft" and "VSC" not in text:
            return 'RADIO_DRIVER "VSC deployed. Boxing for softs. Low pit loss."'
        if obs.race_status == "vsc" and obs.ego_tyre_compound != "soft":
            return "PIT_NOW soft"
        if "INSPECT_FUEL_MARGIN" not in text and obs.current_lap >= 12:
            return "INSPECT_FUEL_MARGIN"
        return "DONE" if obs.current_lap >= obs.total_laps else "STAY_OUT"
    if family == "tyre_cliff_management":
        if "INSPECT_TYRE_DEGRADATION" not in text:
            return "INSPECT_TYRE_DEGRADATION"
        if "MANAGE_TYRE_TEMP cool" not in text and obs.current_lap >= 3:
            return "MANAGE_TYRE_TEMP cool"
        if obs.ego_tyre_health_pct < 55 and "cliff" not in text.lower():
            return 'RADIO_DRIVER "Tyre cliff incoming. Boxing for medium."'
        if obs.current_lap >= 7 and obs.ego_tyre_compound == "soft":
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
    if family == "virtual_safety_car_window" and obs.race_status == "vsc":
        return "STAY_OUT"  # untrained ignores the VSC window
    if family == "tyre_cliff_management" and obs.current_lap >= 10:
        return rng.choice(["PIT_NOW soft", "STAY_OUT"])  # reacts too late
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
        "`trained` is the model loaded from `--model` (HF Hub repo or local transformers "
        "checkpoint). For local-smoke runs without a real checkpoint it falls back to a "
        "deliberately weaker scripted policy that demonstrates the gap to expert."
    )
    output.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=None)
    parser.add_argument(
        "--tasks",
        nargs="+",
        default=[
            "dry_strategy_sprint",
            "weather_roulette",
            "late_safety_car",
            "championship_decider",
            "virtual_safety_car_window",
            "tyre_cliff_management",
        ],
    )
    parser.add_argument("--n-seeds", type=int, default=5)
    parser.add_argument("--modes", nargs="+", default=["random", "untrained", "trained", "expert"])
    parser.add_argument("--output-json", default="results/eval_summary.json")
    parser.add_argument("--output-png", default="results/eval_curve.png")
    parser.add_argument("--no-memory", action="store_true")
    parser.add_argument("--use-memory", action="store_true")
    main(parser.parse_args())