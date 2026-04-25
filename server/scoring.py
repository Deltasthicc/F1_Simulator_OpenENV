"""
F1 Strategist — Six-Dimension Scoring
=======================================

Pure-Python deterministic scorer. No LLM, no random, no side effects.
Direct port of OpsTwin's scoring.py shape with race-relevant signals.

Owner: Person 2 (Tanish) — fills the bodies. Person 1 imports and calls.
Spec: docs/reward-model.md.

TODO Phase 2:
    - compute_race_result
    - compute_strategic_decisions
    - compute_tyre_management
    - compute_fuel_management
    - compute_comms_quality
    - compute_operational_efficiency
    - compute_multi_objective_scores (weighted final, clamped to [0.01, 0.99])

Weights:
    race_result: 0.35, strategic_decisions: 0.20,
    tyre_management: 0.15, fuel_management: 0.10,
    comms_quality: 0.10, operational_efficiency: 0.10
"""

WEIGHTS = {
    "race_result": 0.35,
    "strategic_decisions": 0.20,
    "tyre_management": 0.15,
    "fuel_management": 0.10,
    "comms_quality": 0.10,
    "operational_efficiency": 0.10,
}


def compute_race_result(
    starting_position: int,
    finishing_position: int,
    target_position: int,
    rival_finishing_position: int | None = None,
) -> float:
    raise NotImplementedError("Phase 2, Person 2")


def compute_strategic_decisions(
    pit_decisions: list,
    optimal_pit_window: tuple[int, int],
    inspection_calls: dict,
    forecast_called_before_pit: bool,
    undercut_assessed_before_pit: bool,
) -> float:
    raise NotImplementedError("Phase 2, Person 2")


def compute_tyre_management(
    final_tyre_health: float,
    compound_rule_satisfied: bool,
    stints: list,
    track_character: str,
) -> float:
    raise NotImplementedError("Phase 2, Person 2")


def compute_fuel_management(
    final_fuel_kg: float,
    target_margin_kg: float,
    dnf_due_to_fuel: bool,
    inspect_fuel_called: bool,
) -> float:
    raise NotImplementedError("Phase 2, Person 2")


def compute_comms_quality(
    triggered_comms_events: list,
    radio_calls_made: list,
    pit_wall_calls: list,
) -> float:
    raise NotImplementedError("Phase 2, Person 2")


def compute_operational_efficiency(
    n_pit_stops: int,
    target_n_pits: int,
    invalid_actions: int,
    harmful_actions: int,
    total_laps: int,
    steps_used: int,
) -> float:
    raise NotImplementedError("Phase 2, Person 2")


def compute_multi_objective_scores(**kwargs) -> dict:
    """Wrapper that calls all six functions, applies WEIGHTS, returns dict.

    Required kwargs: see individual function signatures above. Caller (the
    environment) extracts these from its audit trail and ego state.
    """
    raise NotImplementedError("Phase 2, Person 2")
