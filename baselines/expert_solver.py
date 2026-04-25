"""
F1 Strategist — Rule-Based Expert Solver
==========================================

Reads scenario at god-mode (full hidden state) and emits the optimal action
sequence. Used as:
    - upper-bound reference (target ≥ 0.92 on hand-authored scenarios)
    - SFT warm-start data source (capture_everything.py uses this)
    - sanity check on scenario solvability (smoke_all_scenarios.py uses this)

Owner: Person 2.
Spec: docs/person2-tasks.md §1.2.

TODO Phase 2:
    - ExpertSolver.solve(scenario, env) -> list[F1Action]
    - _solve_dry — Family 1: undercut-aware Monza one-stop
    - _solve_weather — Family 2: forecast-driven inter pit
    - _solve_sc — Family 3: hold for SC, free pit
    - _solve_championship — Stretch: defend rival + manage rain
    - --task, --seed, --save args

CLI:
    python -m baselines.expert_solver --task dry_strategy_sprint --seed 0
    python -m baselines.expert_solver --task weather_roulette --save baselines/trajectories/expert_weather_seed0.jsonl
"""
import argparse


class ExpertSolver:
    def solve(self, scenario: dict, env) -> list:
        family = scenario.get("scenario_family", "")
        if family == "dry_strategy_sprint":
            return self._solve_dry(scenario, env)
        elif family == "weather_roulette":
            return self._solve_weather(scenario, env)
        elif family == "late_safety_car":
            return self._solve_sc(scenario, env)
        elif family == "championship_decider":
            return self._solve_championship(scenario, env)
        raise ValueError(f"Unknown family: {family}")

    def _solve_dry(self, sc, env): raise NotImplementedError("Phase 2, Person 2")
    def _solve_weather(self, sc, env): raise NotImplementedError("Phase 2, Person 2")
    def _solve_sc(self, sc, env): raise NotImplementedError("Phase 2, Person 2")
    def _solve_championship(self, sc, env): raise NotImplementedError("Phase 2, Person 2")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--save", help="Save trace JSONL here")
    args = parser.parse_args()
    raise NotImplementedError("Phase 2, Person 2")


if __name__ == "__main__":
    main()
