"""
F1 Strategist — Procedural Scenario Generator
==============================================

Seed-deterministic variants of each scenario family. Used to expand training
coverage beyond the four hand-authored seeds.

Owner: Person 1.
Spec: docs/build-order.md Phase 5.

TODO Phase 5:
    - generate(family, seed, difficulty="medium") -> dict
        Vary: starting_position, opponent pace_offsets, weather seed,
        SC schedule, total_laps within the family's typical range
    - validate: every generated scenario must be solvable by expert_solver
        at ≥0.85 on the same seed (run validate_generator.py to check 100 seeds)
"""
import copy
import numpy as np

from server.scenarios import SCENARIOS


def generate(family: str, seed: int, difficulty: str = "medium") -> dict:
    """Procedural variant of a hand-authored family."""
    if family not in SCENARIOS:
        raise ValueError(f"Unknown family: {family}")

    base = copy.deepcopy(SCENARIOS[family])
    rng = np.random.default_rng(seed)
    # TODO Phase 5: vary starting_position, opponent pace_offsets,
    # weather seed, SC schedule. See docs/build-order.md §Phase-5.
    base["seed"] = seed
    return base
