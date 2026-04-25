"""
Per-scenario solvability smoke test.

For each scenario family + the stretch:
    - run the expert solver, assert final score ≥ 0.85
    - run a deliberately-bad scripted policy, assert score ≤ 0.40

If this passes, scenarios are well-formed and the reward signal is
discriminative (≥0.45 spread).

CLI:
    python tests/smoke_all_scenarios.py
"""
import sys


SCENARIOS_TO_TEST = [
    "dry_strategy_sprint",
    "weather_roulette",
    "late_safety_car",
    "championship_decider",
]


def main() -> int:
    failures = 0
    for family in SCENARIOS_TO_TEST:
        # TODO Phase 2:
        # 1. env = F1StrategistEnvironment(); env.reset(options={"task": family, "seed": 42})
        # 2. expert_score = run_expert(env)
        # 3. assert expert_score >= 0.85
        # 4. env.reset(options={"task": family, "seed": 42}); panic_score = run_panic(env)
        # 5. assert panic_score <= 0.40
        pass
    print("smoke_all_scenarios stub: implement in Phase 2 (Person 2).")
    return failures


if __name__ == "__main__":
    sys.exit(main())
