"""
F1 Strategist — Hand-Authored Scenarios
=========================================

Three families + one stretch. Each scenario dict conforms to the schema in
docs/scenarios.md. All deterministically solvable; expert solver hits ≥0.92
on each.

Owner: Person 1.
Spec: docs/scenarios.md.

TODO Phase 2:
    - DRY_STRATEGY_SPRINT (Monza, 10 laps)
    - WEATHER_ROULETTE (Spa, 12 laps)
    - LATE_SAFETY_CAR (Monaco, 12 laps)
    - CHAMPIONSHIP_DECIDER (Catalunya, 15 laps)  — stretch

Each must set: task_name, scenario_family, track_name, total_laps, max_steps,
starting_position, starting_compound, starting_fuel_kg, opponents (list),
weather_archetype, sc_archetype, issues (six categories summing to 1.0),
hidden_state, dynamic_events.
"""

DRY_STRATEGY_SPRINT: dict = {
    "task_name": "dry_strategy_sprint_monza",
    "scenario_family": "dry_strategy_sprint",
    "track_name": "Monza",
    "total_laps": 10,
    "max_steps": 14,
    # TODO Phase 2: fill from docs/scenarios.md §Family-1
}

WEATHER_ROULETTE: dict = {
    "task_name": "weather_roulette_spa",
    "scenario_family": "weather_roulette",
    "track_name": "Spa",
    "total_laps": 12,
    "max_steps": 16,
    # TODO Phase 2: fill from docs/scenarios.md §Family-2
}

LATE_SAFETY_CAR: dict = {
    "task_name": "late_safety_car_monaco",
    "scenario_family": "late_safety_car",
    "track_name": "Monaco",
    "total_laps": 12,
    "max_steps": 16,
    # TODO Phase 2: fill from docs/scenarios.md §Family-3
}

CHAMPIONSHIP_DECIDER: dict = {
    "task_name": "championship_decider_catalunya",
    "scenario_family": "championship_decider",
    "track_name": "Catalunya",
    "total_laps": 15,
    "max_steps": 20,
    # TODO Phase 2: fill from docs/scenarios.md §Stretch
}

SCENARIOS: dict[str, dict] = {
    "dry_strategy_sprint": DRY_STRATEGY_SPRINT,
    "weather_roulette":    WEATHER_ROULETTE,
    "late_safety_car":     LATE_SAFETY_CAR,
    "championship_decider": CHAMPIONSHIP_DECIDER,
}
