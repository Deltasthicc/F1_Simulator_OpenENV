"""Deterministic six-dimension scorer for F1 strategist episodes."""

WEIGHTS = {
    "race_result": 0.35,
    "strategic_decisions": 0.20,
    "tyre_management": 0.15,
    "fuel_management": 0.10,
    "comms_quality": 0.10,
    "operational_efficiency": 0.10,
}

DRY_COMPOUNDS = {"soft", "medium", "hard"}


def compute_race_result(
    starting_position: int,
    finishing_position: int,
    target_position: int,
    rival_finishing_position: int | None = None,
) -> float:
    if finishing_position <= 0:
        return 0.0
    score = 1.0 if finishing_position <= target_position else 0.0
    if not score and finishing_position <= starting_position:
        score = 0.55
    if not score and finishing_position == target_position + 1:
        score = 0.35
    if rival_finishing_position is not None:
        score = (
            min(score, 0.65) if finishing_position > rival_finishing_position else max(score, 0.95)
        )
    return _clamp01(score)


def compute_strategic_decisions(
    pit_decisions: list,
    optimal_pit_window: tuple[int, int],
    inspection_calls: dict,
    forecast_called_before_pit: bool,
    undercut_assessed_before_pit: bool,
) -> float:
    if not pit_decisions:
        return 0.0
    lo, hi = optimal_pit_window
    in_window = any(lo <= int(p.get("lap", 0)) <= hi for p in pit_decisions)
    if not in_window:
        return 0.25
    precondition = (
        forecast_called_before_pit or undercut_assessed_before_pit or bool(inspection_calls)
    )
    return 1.0 if precondition else 0.65


def compute_tyre_management(
    final_tyre_health: float,
    compound_rule_satisfied: bool,
    stints: list,
    track_character: str,
) -> float:
    health_floor = 0.30 if track_character == "street" else 0.40
    health_score = (
        1.0 if final_tyre_health >= health_floor else max(0.0, final_tyre_health / health_floor)
    )
    compound_score = 1.0 if compound_rule_satisfied else 0.0
    return _clamp01(0.55 * compound_score + 0.45 * health_score)


def compute_fuel_management(
    final_fuel_kg: float,
    target_margin_kg: float,
    dnf_due_to_fuel: bool,
    inspect_fuel_called: bool,
) -> float:
    if dnf_due_to_fuel or final_fuel_kg < 0:
        return 0.0
    margin_score = min(1.0, final_fuel_kg / max(0.1, target_margin_kg))
    return _clamp01(0.85 * margin_score + (0.15 if inspect_fuel_called else 0.0))


def compute_comms_quality(
    triggered_comms_events: list,
    radio_calls_made: list,
    pit_wall_calls: list,
) -> float:
    required = [str(x).lower() for x in triggered_comms_events if x]
    if not required:
        return 1.0
    text = " ".join(
        str(call.get("message", call)).lower() for call in radio_calls_made + pit_wall_calls
    )
    hits = sum(1 for needle in required if needle in text)
    if hits == 0 and radio_calls_made:
        hits = 1
    return _clamp01(hits / len(required))


def compute_operational_efficiency(
    n_pit_stops: int,
    target_n_pits: int,
    invalid_actions: int,
    harmful_actions: int,
    total_laps: int,
    steps_used: int,
) -> float:
    pit_score = (
        1.0
        if n_pit_stops == target_n_pits
        else max(0.0, 1.0 - 0.45 * abs(n_pit_stops - target_n_pits))
    )
    penalty = 0.12 * invalid_actions + 0.18 * harmful_actions
    if steps_used > total_laps + 8:
        penalty += min(0.20, 0.02 * (steps_used - total_laps - 8))
    return _clamp01(pit_score - penalty)


def compute_multi_objective_scores(**kwargs) -> dict:
    """Compute all dimensions and a weighted final score clamped to [0.01, 0.99]."""
    pit_decisions = kwargs.get("pit_decisions", [])
    inspection_calls = kwargs.get("inspection_calls", {})
    scenario_family = kwargs.get("scenario_family", "")
    criteria = kwargs.get("success_criteria", {}) or {}
    optimal_window = tuple(
        criteria.get("optimal_pit_window", kwargs.get("optimal_pit_window", (1, 999)))
    )
    required_compound = criteria.get("required_compound")
    required_actions = set(criteria.get("required_actions", []))
    action_verbs = set(kwargs.get("action_verbs", []))

    first_pit_lap = min((int(p.get("lap", 999)) for p in pit_decisions), default=999)
    forecast_before = any(
        lap <= first_pit_lap for lap in inspection_calls.get("REQUEST_FORECAST", [])
    )
    undercut_before = any(
        lap <= first_pit_lap for lap in inspection_calls.get("ASSESS_UNDERCUT_WINDOW", [])
    )

    race = compute_race_result(
        kwargs.get("starting_position", 99),
        kwargs.get("finishing_position", 99),
        criteria.get("target_position", kwargs.get("target_position", 99)),
        kwargs.get("rival_finishing_position"),
    )

    strategic = compute_strategic_decisions(
        pit_decisions,
        optimal_window,
        inspection_calls,
        forecast_before,
        undercut_before,
    )
    strategic = _scenario_strategy_adjustment(
        scenario_family,
        strategic,
        pit_decisions,
        optimal_window,
        required_compound,
        forecast_before,
        undercut_before,
        required_actions,
        action_verbs,
    )
    if strategic >= 0.85:
        race = max(race, 0.90)

    tyre = compute_tyre_management(
        kwargs.get("final_tyre_health", 0.0),
        kwargs.get("compound_rule_satisfied", False),
        kwargs.get("stints", []),
        kwargs.get("track_character", "balanced"),
    )
    if required_compound and not any(
        stint.get("compound") == required_compound for stint in kwargs.get("stints", [])
    ):
        tyre = min(tyre, 0.20)
    fuel = compute_fuel_management(
        kwargs.get("final_fuel_kg", 0.0),
        criteria.get("fuel_margin_kg", kwargs.get("target_margin_kg", 0.5)),
        kwargs.get("dnf_due_to_fuel", False),
        bool(inspection_calls.get("INSPECT_FUEL_MARGIN")),
    )
    comms = compute_comms_quality(
        criteria.get("required_comms", kwargs.get("triggered_comms_events", [])),
        kwargs.get("radio_calls_made", []),
        kwargs.get("pit_wall_calls", []),
    )
    ops = compute_operational_efficiency(
        kwargs.get("n_pit_stops", 0),
        criteria.get("target_n_pits", kwargs.get("target_n_pits", 1)),
        kwargs.get("invalid_actions", 0),
        kwargs.get("harmful_actions", 0),
        kwargs.get("total_laps", 0),
        kwargs.get("steps_used", 0),
    )

    dims = {
        "race_result": _clamp01(race),
        "strategic_decisions": _clamp01(strategic),
        "tyre_management": _clamp01(tyre),
        "fuel_management": _clamp01(fuel),
        "comms_quality": _clamp01(comms),
        "operational_efficiency": _clamp01(ops),
    }
    weighted = sum(dims[k] * WEIGHTS[k] for k in WEIGHTS)
    dims["weighted_final"] = min(0.99, max(0.01, round(weighted, 4)))
    return dims


def _scenario_strategy_adjustment(
    scenario_family: str,
    base: float,
    pit_decisions: list,
    optimal_window: tuple[int, int],
    required_compound: str | None,
    forecast_before: bool,
    undercut_before: bool,
    required_actions: set[str],
    action_verbs: set[str],
) -> float:
    lo, hi = optimal_window
    tolerance = 2 if scenario_family in {"dry_strategy_sprint", "weather_roulette"} else 0
    matching_pits = [
        p
        for p in pit_decisions
        if lo <= int(p.get("lap", 0)) <= hi + tolerance
        and (required_compound is None or p.get("compound") == required_compound)
    ]
    if scenario_family == "dry_strategy_sprint":
        return 1.0 if matching_pits and undercut_before else (0.55 if matching_pits else base)
    if scenario_family == "weather_roulette":
        return 1.0 if matching_pits and forecast_before else (0.60 if matching_pits else 0.20)
    if scenario_family == "late_safety_car":
        under_sc = any(p.get("under_sc") for p in matching_pits)
        held_gap = "HOLD_GAP" in action_verbs or not required_actions
        return 1.0 if matching_pits and under_sc and held_gap else (0.50 if matching_pits else 0.15)
    if scenario_family == "championship_decider":
        inspected = forecast_before and any(
            "CHECK_OPPONENT_STRATEGY" in k for k in action_verbs | set()
        )
        return 1.0 if matching_pits and inspected else (0.65 if matching_pits else base)
    return base


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, float(value)))
