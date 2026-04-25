"""Pytest: six-dimension scorer is pure and deterministic."""

from server import scoring


def _kwargs():
    return {
        "scenario_family": "dry_strategy_sprint",
        "success_criteria": {
            "target_position": 4,
            "optimal_pit_window": [4, 7],
            "target_n_pits": 1,
            "required_compound": "soft",
            "required_inspections": ["ASSESS_UNDERCUT_WINDOW"],
            "required_comms": ["pit"],
            "fuel_margin_kg": 0.5,
        },
        "starting_position": 4,
        "finishing_position": 3,
        "pit_decisions": [{"lap": 6, "compound": "soft", "under_sc": False}],
        "inspection_calls": {"ASSESS_UNDERCUT_WINDOW": [3], "INSPECT_FUEL_MARGIN": [9]},
        "final_tyre_health": 0.70,
        "compound_rule_satisfied": True,
        "stints": [{"compound": "medium"}, {"compound": "soft"}],
        "track_character": "power",
        "final_fuel_kg": 1.0,
        "dnf_due_to_fuel": False,
        "radio_calls_made": [{"message": "pit this lap"}],
        "pit_wall_calls": [],
        "n_pit_stops": 1,
        "invalid_actions": 0,
        "harmful_actions": 0,
        "total_laps": 10,
        "steps_used": 12,
        "action_verbs": ["ASSESS_UNDERCUT_WINDOW", "PIT_NOW"],
    }


def test_weighted_final_clamped():
    perfect = scoring.compute_multi_objective_scores(**_kwargs())
    assert perfect["weighted_final"] <= 0.99
    bad = _kwargs()
    bad.update(
        {
            "finishing_position": 10,
            "pit_decisions": [],
            "compound_rule_satisfied": False,
            "final_fuel_kg": -1.0,
            "dnf_due_to_fuel": True,
            "radio_calls_made": [],
            "n_pit_stops": 0,
            "invalid_actions": 8,
            "harmful_actions": 3,
        }
    )
    poor = scoring.compute_multi_objective_scores(**bad)
    assert poor["weighted_final"] >= 0.01


def test_pure_function_no_side_effects():
    a = scoring.compute_multi_objective_scores(**_kwargs())
    b = scoring.compute_multi_objective_scores(**_kwargs())
    assert a == b
