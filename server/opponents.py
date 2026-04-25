"""
F1 Strategist — Opponents
===========================

Rule-based opponent strategies. Five cars sharing the track with ego.
Each opponent has a hidden stint plan that the ego strategist can only
discover via CHECK_OPPONENT_STRATEGY (per architecture.md §2).

Owner: Person 1.
Spec: docs/architecture.md §4, docs/physics-model.md §opponents.

TODO:
    - Phase 2: Stint, Opponent dataclasses
    - Phase 2: step_opponents(opponents, track, weather, sc_active, lap)
        - run physics for each
        - execute planned pits when lap matches stint.planned_end_lap
        - opportunistic SC pits (if SC active and not pitted yet)
        - update positions by cumulative_time_s
    - Phase 2: build_opponents_for_scenario(scenario_dict, seed) — initialise
        from scenario["opponents"] with pace_offset_s sampled from
        data/opponent_pace_calibration.json

Opponent visibility (TV-feed level, always shown):
    driver_number, team, position, last_lap_time_s, gap_s, current_compound, stint_age

Hidden until CHECK_OPPONENT_STRATEGY:
    planned_strategy[next].planned_end_lap, planned_strategy[next].compound
"""
from dataclasses import dataclass, field


@dataclass
class Stint:
    compound: str
    planned_end_lap: int


@dataclass
class Opponent:
    driver_number: int
    team: str
    pace_offset_s: float
    aggression: float
    planned_strategy: list[Stint] = field(default_factory=list)
    current_compound: str = ""
    current_tyre_age: int = 0
    current_position: int = 0
    fuel_remaining_kg: float = 0.0
    cumulative_time_s: float = 0.0


def step_opponents(opponents: list[Opponent], **ctx) -> None:
    """Advance each opponent one lap. Mutates in place."""
    raise NotImplementedError("Phase 2, Person 1")


def build_opponents_for_scenario(scenario: dict, seed: int) -> list[Opponent]:
    """Construct the opponent list from scenario dict + RNG seed."""
    raise NotImplementedError("Phase 2, Person 1")
