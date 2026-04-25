"""
F1 Strategist — Baseline Inference Runner
==========================================

Runs an LLM as the strategist against the env. Used for:
    - smoke-testing the env with an off-the-shelf model (Qwen3-0.6B)
    - comparing trained vs untrained policies (called from evaluate.py)
    - recording rollouts for the visualiser

Owner: Person 2 (Tanish).
Spec: docs/person2-tasks.md §1.4.

TODO Phase 2:
    - SYSTEM_PROMPT (the strategist persona + action grammar)
    - format_obs(obs) → str (turns the observation into a chat-friendly summary)
    - parse_action(response_text) → F1Action (extracts a command from the LLM output)
    - run_inference(model, task, n_episodes, verbose) — main entry
    - argparse: --model, --task, --n-episodes, --base-url, --seed, --verbose, --save

CLI:
    python inference.py --model Qwen/Qwen3-0.6B --task dry_strategy_sprint
    python inference.py --model Deltasthic/f1-strategist-qwen3-4b-grpo --task weather_roulette --n-episodes 5
"""
import argparse


SYSTEM_PROMPT = """You are an F1 race strategist. Each lap, you see the race state
(position, tyres, fuel, weather, opponents) and issue ONE strategic command.

Available commands:
- PIT_NOW <soft|medium|hard|inter|wet>
- STAY_OUT
- RECOMMEND_PIT <next_lap>
- SET_MODE <push|race|conserve|fuel_save|tyre_save>
- DRS_PERMISSION <on|off>
- DEFEND_POSITION
- ATTACK_AHEAD
- HOLD_GAP <driver_number>
- LET_BY <driver_number>
- INSPECT_TYRE_DEGRADATION
- CHECK_OPPONENT_STRATEGY <driver_number>
- REQUEST_FORECAST
- ASSESS_UNDERCUT_WINDOW
- INSPECT_FUEL_MARGIN
- RADIO_DRIVER "<message>"
- DRAFT_PIT_WALL "<message>"
- BRIEF_MEDIA "<message>"
- REQUEST_INFO <opponents|weather|tyres|fuel|pit_window|standings|audit>
- ESCALATE_TO_PRINCIPAL
- DONE

Goals: finish high, manage tyres, manage fuel, time pit stops well, send
required radio comms. Investigate hidden state via INSPECT_* before
committing to big decisions.
"""


def format_obs(obs) -> str:
    """Turn an F1Observation into a compact prompt-friendly string."""
    raise NotImplementedError("Phase 2, Person 2")


def parse_action(response_text: str):
    """Extract an F1Action from the LLM's response text."""
    raise NotImplementedError("Phase 2, Person 2")


def run_inference(model: str, task: str, n_episodes: int = 1, verbose: bool = False):
    raise NotImplementedError("Phase 2, Person 2")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--task", default="dry_strategy_sprint")
    parser.add_argument("--n-episodes", type=int, default=1)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--save", help="Save rollout JSONL here")
    args = parser.parse_args()
    run_inference(args.model, args.task, args.n_episodes, args.verbose)


if __name__ == "__main__":
    main()
