"""Baseline inference runner for F1 Strategist."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable

from models import F1Action
from server.environment import F1StrategistEnvironment
from server.scenarios import SCENARIOS


SYSTEM_PROMPT = """You are an F1 race strategist. Respond with exactly one command.

Commands:
PIT_NOW <soft|medium|hard|inter|wet>
STAY_OUT
RECOMMEND_PIT <next_lap>
SET_MODE <push|race|conserve|fuel_save|tyre_save>
DRS_PERMISSION <on|off>
DEFEND_POSITION
ATTACK_AHEAD
HOLD_GAP <driver_number>
LET_BY <driver_number>
INSPECT_TYRE_DEGRADATION
CHECK_OPPONENT_STRATEGY <driver_number>
REQUEST_FORECAST
ASSESS_UNDERCUT_WINDOW
INSPECT_FUEL_MARGIN
RADIO_DRIVER "<message>"
DRAFT_PIT_WALL "<message>"
BRIEF_MEDIA "<message>"
REQUEST_INFO <opponents|weather|tyres|fuel|pit_window|standings|audit>
ESCALATE_TO_PRINCIPAL
DONE
"""

VALID_VERBS = {
    "PIT_NOW",
    "STAY_OUT",
    "RECOMMEND_PIT",
    "SET_MODE",
    "DRS_PERMISSION",
    "DEFEND_POSITION",
    "ATTACK_AHEAD",
    "HOLD_GAP",
    "LET_BY",
    "INSPECT_TYRE_DEGRADATION",
    "CHECK_OPPONENT_STRATEGY",
    "REQUEST_FORECAST",
    "ASSESS_UNDERCUT_WINDOW",
    "INSPECT_FUEL_MARGIN",
    "RADIO_DRIVER",
    "DRAFT_PIT_WALL",
    "BRIEF_MEDIA",
    "REQUEST_INFO",
    "ESCALATE_TO_PRINCIPAL",
    "DONE",
}


def format_obs(obs) -> str:
    """Turn an F1Observation into a compact prompt string."""
    opponents = ", ".join(
        f"#{o['driver_number']} P{o['position']} {o['current_compound']} gap={o['gap_s']}"
        for o in obs.opponents[:6]
    )
    forecast = (
        "; ".join(
            f"L{f['lap']} rain {f['lower']:.2f}-{f['upper']:.2f}" for f in obs.weather_forecast[:5]
        )
        or "hidden"
    )
    alerts = "; ".join(
        a.get("message", a.get("desc", "")) for a in obs.pit_window_alerts + obs.cascade_alerts
    )
    return (
        f"Lap {obs.current_lap}/{obs.total_laps}, phase={obs.race_phase}, status={obs.race_status}\n"
        f"Ego: P{obs.ego_position}, {obs.ego_tyre_compound} age={obs.ego_tyre_age_laps}, "
        f"health={obs.ego_tyre_health_pct:.1f}%, fuel={obs.ego_fuel_remaining_kg:.2f}kg, "
        f"mode={obs.ego_drive_mode}, last_lap={obs.ego_last_lap_time_s:.3f}, "
        f"gap_ahead={obs.ego_gap_ahead_s}, gap_behind={obs.ego_gap_behind_s}\n"
        f"Weather: {obs.weather_current}; forecast={forecast}\n"
        f"Opponents: {opponents or 'none'}\n"
        f"Alerts: {alerts or 'none'}\n"
        f"Memory hints: {' | '.join(obs.memory_hints) or 'none'}\n"
        f"Pending issues: {obs.pending_issues_count}/{obs.total_issues_count}\n"
        "Return one command only."
    )


def parse_action(response_text: str) -> F1Action:
    """Extract the first valid command-looking line from model output."""
    text = (response_text or "").strip()
    text = re.sub(r"</?think>", "", text, flags=re.IGNORECASE).strip()
    candidates = []
    for line in text.splitlines():
        line = line.strip().strip("`").strip()
        if not line:
            continue
        candidates.append(line)
    if not candidates:
        candidates = [text]
    for candidate in candidates:
        upper = candidate.split(None, 1)[0].upper() if candidate else ""
        if upper in VALID_VERBS:
            return F1Action(command=candidate)
    match = re.search(
        r"\b(" + "|".join(sorted(VALID_VERBS, key=len, reverse=True)) + r")\b(.*)", text, re.I
    )
    if match:
        return F1Action(command=(match.group(1).upper() + match.group(2)).strip())
    return F1Action(command="STAY_OUT")


def run_inference(
    model: str,
    task: str,
    n_episodes: int = 1,
    verbose: bool = False,
    seed: int = 0,
    save: str | None = None,
) -> list[float]:
    """Run model/heuristic policy locally and return final scores."""
    generator = _build_generator(model)
    scores: list[float] = []
    save_path = Path(save) if save else None
    if save_path:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text("", encoding="utf-8")

    for ep in range(n_episodes):
        env = F1StrategistEnvironment()
        obs = env.reset(task=task, seed=seed + ep)
        history = [{"role": "system", "content": SYSTEM_PROMPT}]
        trace = [{"action": "RESET", "observation": obs.model_dump()}]
        while not obs.done:
            prompt = format_obs(obs)
            history.append({"role": "user", "content": prompt})
            response = generator(history, obs, task)
            action = parse_action(response)
            history.append({"role": "assistant", "content": action.command})
            if verbose:
                print(f"L{obs.current_lap:02d} -> {action.command}")
            obs = env.step(action)
            trace.append({"action": action.command, "observation": obs.model_dump()})
        score = float(obs.multi_objective_scores.get("weighted_final", obs.score))
        scores.append(score)
        print(f"Episode {ep}: score={score:.3f}")
        if save_path:
            with save_path.open("a", encoding="utf-8") as f:
                for row in trace:
                    f.write(json.dumps(row) + "\n")
    return scores


def _build_generator(model: str):
    lowered = model.lower()
    if lowered in {"heuristic", "expert", "scripted"} or Path(model).exists():
        return _heuristic_generator
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
    except ImportError as exc:
        raise SystemExit(
            "Transformers inference dependencies are not installed. "
            "Install `pip install -e .[inference]`, or use `--model heuristic`."
        ) from exc

    tokenizer = AutoTokenizer.from_pretrained(model, trust_remote_code=True)
    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
    lm = AutoModelForCausalLM.from_pretrained(
        model, torch_dtype=dtype, device_map="auto", trust_remote_code=True
    )

    def generate(history, obs, task):
        if hasattr(tokenizer, "apply_chat_template"):
            text = tokenizer.apply_chat_template(
                history, tokenize=False, add_generation_prompt=True
            )
        else:
            text = "\n".join(f"{m['role']}: {m['content']}" for m in history) + "\nassistant:"
        inputs = tokenizer(text, return_tensors="pt").to(lm.device)
        with torch.no_grad():
            out = lm.generate(**inputs, max_new_tokens=96, do_sample=False)
        return tokenizer.decode(out[0][inputs["input_ids"].shape[-1] :], skip_special_tokens=True)

    return generate


def _heuristic_generator(history, obs, task) -> str:
    family = SCENARIOS.get(task, {}).get("scenario_family", task)
    lap = obs.current_lap
    assistant_text = _assistant_text(history)
    if family == "weather_roulette":
        if "REQUEST_FORECAST" not in assistant_text:
            return "REQUEST_FORECAST"
        if lap < 6:
            return "STAY_OUT"
        if (
            obs.ego_tyre_compound != "inter"
            and lap >= 7
            and "Box now for inters" not in assistant_text
        ):
            return 'RADIO_DRIVER "Box now for inters."'
        if obs.ego_tyre_compound != "inter":
            return "PIT_NOW inter"
        return "SET_MODE push" if lap < obs.total_laps - 1 else "DONE"
    if family == "late_safety_car":
        if "HOLD_GAP" not in assistant_text and lap < 7:
            return "HOLD_GAP 4"
        if (
            obs.race_status in {"sc", "vsc"}
            and obs.ego_tyre_compound != "hard"
            and "Safety car" not in assistant_text
        ):
            return 'RADIO_DRIVER "Safety car, boxing this lap."'
        if obs.race_status in {"sc", "vsc"} and obs.ego_tyre_compound != "hard":
            return "PIT_NOW hard"
        return "DONE" if lap >= obs.total_laps else "STAY_OUT"
    if family == "championship_decider":
        if "CHECK_OPPONENT_STRATEGY" not in assistant_text:
            return "CHECK_OPPONENT_STRATEGY 10"
        if "REQUEST_FORECAST" not in assistant_text:
            return "REQUEST_FORECAST"
        if lap >= 7 and obs.ego_tyre_compound == "hard":
            return "PIT_NOW medium"
        return "DONE" if lap >= obs.total_laps else "STAY_OUT"
    if "ASSESS_UNDERCUT_WINDOW" not in assistant_text:
        return "ASSESS_UNDERCUT_WINDOW"
    if lap >= 5 and obs.ego_tyre_compound != "soft":
        return "PIT_NOW soft"
    return "DONE" if lap >= obs.total_laps else "STAY_OUT"


def _history_text(history: Iterable[dict]) -> str:
    return "\n".join(str(item.get("content", "")) for item in history)


def _assistant_text(history: Iterable[dict]) -> str:
    return "\n".join(
        str(item.get("content", "")) for item in history if item.get("role") == "assistant"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="heuristic")
    parser.add_argument("--task", default="dry_strategy_sprint")
    parser.add_argument("--n-episodes", type=int, default=1)
    parser.add_argument(
        "--base-url", default=None, help="Reserved for HTTP mode; local env is used by default."
    )
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--save")
    args = parser.parse_args()
    run_inference(args.model, args.task, args.n_episodes, args.verbose, args.seed, args.save)


if __name__ == "__main__":
    main()
