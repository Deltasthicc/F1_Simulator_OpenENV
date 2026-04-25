"""Hand-authored F1 strategist scenarios."""

COMMON_COMMANDS = [
    "PIT_NOW <compound>",
    "STAY_OUT",
    "SET_MODE <push|race|conserve|fuel_save|tyre_save>",
    "HOLD_GAP <driver_number>",
    "ATTACK_AHEAD",
    "DEFEND_POSITION",
    "INSPECT_TYRE_DEGRADATION",
    "CHECK_OPPONENT_STRATEGY <driver_number>",
    "REQUEST_FORECAST",
    "ASSESS_UNDERCUT_WINDOW",
    "INSPECT_FUEL_MARGIN",
    "RADIO_DRIVER <message>",
    "REQUEST_INFO <topic>",
    "DONE",
]


DRY_STRATEGY_SPRINT: dict = {
    "task_name": "dry_strategy_sprint_monza",
    "scenario_family": "dry_strategy_sprint",
    "description": "Monza sprint: cover the undercut, then attack on softs.",
    "track_name": "Monza",
    "total_laps": 10,
    "max_steps": 14,
    "max_score": 1.0,
    "seed": 11,
    "starting_position": 4,
    "starting_compound": "medium",
    "starting_fuel_kg": 95.0,
    "starting_drive_mode": "race",
    "opponents": [
        {
            "driver_number": 1,
            "team": "Red Bull",
            "starting_position": 1,
            "starting_compound": "medium",
            "pace_offset_s": -0.25,
            "aggression": 0.70,
            "planned_strategy": [{"compound": "soft", "planned_end_lap": 6}],
        },
        {
            "driver_number": 44,
            "team": "Mercedes",
            "starting_position": 3,
            "starting_compound": "medium",
            "pace_offset_s": 0.12,
            "aggression": 0.55,
            "planned_strategy": [{"compound": "soft", "planned_end_lap": 6}],
        },
        {
            "driver_number": 16,
            "team": "Ferrari",
            "starting_position": 5,
            "starting_compound": "soft",
            "pace_offset_s": 0.08,
            "aggression": 0.85,
            "planned_strategy": [{"compound": "soft", "planned_end_lap": 3}],
        },
        {
            "driver_number": 4,
            "team": "McLaren",
            "starting_position": 2,
            "starting_compound": "medium",
            "pace_offset_s": -0.05,
            "aggression": 0.60,
            "planned_strategy": [{"compound": "hard", "planned_end_lap": 7}],
        },
        {
            "driver_number": 55,
            "team": "Ferrari",
            "starting_position": 6,
            "starting_compound": "hard",
            "pace_offset_s": 0.28,
            "aggression": 0.45,
            "planned_strategy": [{"compound": "soft", "planned_end_lap": 7}],
        },
    ],
    "weather_archetype": "clear_dry",
    "weather_seed_overrides": {"air_temp_c": 28.0, "track_temp_c": 38.0},
    "sc_archetype": "none",
    "issues": {
        "race_result": [{"goal": "finish_at_least_p4", "points": 0.20}],
        "tyre_management": [
            {"constraint": "use_two_dry_compounds_and_health_gt_40", "points": 0.15}
        ],
        "fuel_management": [{"constraint": "finish_with_0_5kg_margin", "points": 0.05}],
        "strategic_decisions": [
            {
                "decision": "pit_between_laps_4_7_after_undercut_assessment",
                "valid_window": [4, 7],
                "preconditions": ["ASSESS_UNDERCUT_WINDOW"],
                "points": 0.20,
            },
            {"decision": "gain_one_position", "points": 0.20},
            {"decision": "exactly_one_stop", "points": 0.10},
        ],
        "pending_comms": [
            {"trigger": "pit_call", "audience": "driver", "required": True, "points": 0.10}
        ],
    },
    "success_criteria": {
        "target_position": 4,
        "bonus_position": 3,
        "optimal_pit_window": [4, 7],
        "target_n_pits": 1,
        "required_compound": "soft",
        "required_inspections": ["ASSESS_UNDERCUT_WINDOW"],
        "required_comms": ["pit"],
        "fuel_margin_kg": 0.5,
        "tyre_health_min": 0.40,
    },
    "hidden_state": {
        "true_tyre_curve": {
            "medium": [1.00, 0.95, 0.90, 0.85, 0.79, 0.72, 0.64, 0.56, 0.48, 0.40],
            "soft": [1.00, 0.91, 0.82, 0.73, 0.64, 0.55, 0.46, 0.38, 0.31, 0.25],
        },
        "opponent_strategies": {
            "16": [{"compound": "soft", "planned_end_lap": 3}],
            "44": [{"compound": "soft", "planned_end_lap": 6}],
        },
        "fuel_burn_actual": 1.95,
        "undercut_threshold_laps": 2,
    },
    "dynamic_events": [
        {"lap": 3, "type": "opponent_pit", "desc": "#16 pits early for the undercut."},
        {"lap": 6, "type": "pit_window", "desc": "#44 is approaching their planned stop."},
    ],
    "radio_inbox": [
        {"id": "R-001", "from": "race_engineer", "message": "P4. Tyre window opens lap 5."},
        {
            "id": "R-002",
            "from": "team_principal",
            "message": "Push for podium without burning the tyres.",
        },
    ],
    "memory_hint_tags": ["undercut", "monza", "one_stop"],
}


WEATHER_ROULETTE: dict = {
    "task_name": "weather_roulette_spa",
    "scenario_family": "weather_roulette",
    "description": "Spa rain window: time the switch to intermediates.",
    "track_name": "Spa",
    "total_laps": 12,
    "max_steps": 16,
    "max_score": 1.0,
    "seed": 22,
    "starting_position": 5,
    "starting_compound": "medium",
    "starting_fuel_kg": 100.0,
    "starting_drive_mode": "race",
    "opponents": [
        {
            "driver_number": 1,
            "team": "Red Bull",
            "starting_position": 1,
            "starting_compound": "medium",
            "pace_offset_s": -0.35,
            "aggression": 0.75,
            "planned_strategy": [{"compound": "inter", "planned_end_lap": 7}],
        },
        {
            "driver_number": 63,
            "team": "Mercedes",
            "starting_position": 4,
            "starting_compound": "medium",
            "pace_offset_s": 0.05,
            "aggression": 0.50,
            "planned_strategy": [{"compound": "medium", "planned_end_lap": 12}],
        },
        {
            "driver_number": 16,
            "team": "Ferrari",
            "starting_position": 2,
            "starting_compound": "medium",
            "pace_offset_s": -0.05,
            "aggression": 0.65,
            "planned_strategy": [{"compound": "inter", "planned_end_lap": 8}],
        },
        {
            "driver_number": 4,
            "team": "McLaren",
            "starting_position": 3,
            "starting_compound": "medium",
            "pace_offset_s": 0.00,
            "aggression": 0.55,
            "planned_strategy": [{"compound": "inter", "planned_end_lap": 7}],
        },
        {
            "driver_number": 81,
            "team": "McLaren",
            "starting_position": 6,
            "starting_compound": "hard",
            "pace_offset_s": 0.18,
            "aggression": 0.52,
            "planned_strategy": [{"compound": "inter", "planned_end_lap": 8}],
        },
    ],
    "weather_archetype": "light_rain_window",
    "weather_seed_overrides": {
        "forecast_uncertainty": 0.30,
        "per_lap": [
            {"air_temp_c": 18, "track_temp_c": 24, "rain_intensity": 0.0, "surface_state": "dry"},
            {"air_temp_c": 18, "track_temp_c": 24, "rain_intensity": 0.0, "surface_state": "dry"},
            {"air_temp_c": 18, "track_temp_c": 24, "rain_intensity": 0.0, "surface_state": "dry"},
            {"air_temp_c": 18, "track_temp_c": 24, "rain_intensity": 0.0, "surface_state": "dry"},
            {"air_temp_c": 18, "track_temp_c": 24, "rain_intensity": 0.0, "surface_state": "dry"},
            {"air_temp_c": 18, "track_temp_c": 24, "rain_intensity": 0.15, "surface_state": "damp"},
            {"air_temp_c": 18, "track_temp_c": 24, "rain_intensity": 0.45, "surface_state": "damp"},
            {"air_temp_c": 18, "track_temp_c": 24, "rain_intensity": 0.50, "surface_state": "damp"},
            {"air_temp_c": 18, "track_temp_c": 24, "rain_intensity": 0.40, "surface_state": "damp"},
            {"air_temp_c": 18, "track_temp_c": 24, "rain_intensity": 0.20, "surface_state": "damp"},
            {"air_temp_c": 18, "track_temp_c": 24, "rain_intensity": 0.18, "surface_state": "damp"},
            {"air_temp_c": 18, "track_temp_c": 24, "rain_intensity": 0.12, "surface_state": "damp"},
        ],
    },
    "sc_archetype": "none",
    "issues": {
        "race_result": [{"goal": "finish_at_least_p5", "points": 0.15}],
        "tyre_management": [{"constraint": "use_inters_if_peak_above_0_4", "points": 0.15}],
        "fuel_management": [{"constraint": "finish_with_0_5kg_margin", "points": 0.05}],
        "strategic_decisions": [
            {"decision": "pit_for_inters_near_peak", "valid_window": [6, 8], "points": 0.30},
            {"decision": "forecast_before_pit", "points": 0.15},
            {"decision": "finish_without_dnf_and_max_two_stops", "points": 0.10},
        ],
        "pending_comms": [
            {"trigger": "rain_pit", "audience": "driver", "required": True, "points": 0.10}
        ],
    },
    "success_criteria": {
        "target_position": 5,
        "bonus_position": 3,
        "optimal_pit_window": [6, 8],
        "rain_peak_lap": 7,
        "target_n_pits": 1,
        "required_compound": "inter",
        "required_inspections": ["REQUEST_FORECAST"],
        "required_comms": ["rain", "inter"],
        "fuel_margin_kg": 0.5,
        "tyre_health_min": 0.25,
    },
    "hidden_state": {
        "true_tyre_curve": {
            "medium": [1.0, 0.95, 0.90, 0.86, 0.81, 0.76, 0.70],
            "inter": [1.0, 0.93, 0.86, 0.80, 0.74, 0.68],
        },
        "opponent_strategies": {
            "1": [{"compound": "inter", "planned_end_lap": 7}],
            "63": [{"compound": "medium", "planned_end_lap": 12}],
        },
        "fuel_burn_actual": 1.95,
        "undercut_threshold_laps": 3,
    },
    "dynamic_events": [
        {
            "lap": 6,
            "type": "weather",
            "desc": "Drizzle begins around the back half of the circuit.",
        },
        {"lap": 7, "type": "weather", "desc": "Rain peak arrives. Slicks are now slow."},
    ],
    "radio_inbox": [
        {
            "id": "R-101",
            "from": "race_engineer",
            "message": "Forecast is uncertain; request updated weather before committing.",
        }
    ],
    "memory_hint_tags": ["rain", "spa", "intermediate"],
}


LATE_SAFETY_CAR: dict = {
    "task_name": "late_safety_car_monaco",
    "scenario_family": "late_safety_car",
    "description": "Monaco SC lottery: hold track position and take the cheap stop.",
    "track_name": "Monaco",
    "total_laps": 12,
    "max_steps": 16,
    "max_score": 1.0,
    "seed": 33,
    "starting_position": 3,
    "starting_compound": "medium",
    "starting_fuel_kg": 80.0,
    "starting_drive_mode": "race",
    "opponents": [
        {
            "driver_number": 4,
            "team": "McLaren",
            "starting_position": 1,
            "starting_compound": "medium",
            "pace_offset_s": -0.10,
            "aggression": 0.45,
            "planned_strategy": [{"compound": "hard", "planned_end_lap": 8}],
        },
        {
            "driver_number": 11,
            "team": "Red Bull",
            "starting_position": 2,
            "starting_compound": "medium",
            "pace_offset_s": 0.00,
            "aggression": 0.55,
            "planned_strategy": [{"compound": "hard", "planned_end_lap": 6}],
        },
        {
            "driver_number": 16,
            "team": "Ferrari",
            "starting_position": 4,
            "starting_compound": "soft",
            "pace_offset_s": 0.12,
            "aggression": 0.65,
            "planned_strategy": [{"compound": "hard", "planned_end_lap": 5}],
        },
        {
            "driver_number": 44,
            "team": "Mercedes",
            "starting_position": 5,
            "starting_compound": "hard",
            "pace_offset_s": 0.20,
            "aggression": 0.45,
            "planned_strategy": [{"compound": "soft", "planned_end_lap": 9}],
        },
        {
            "driver_number": 14,
            "team": "Aston Martin",
            "starting_position": 6,
            "starting_compound": "medium",
            "pace_offset_s": 0.28,
            "aggression": 0.40,
            "planned_strategy": [{"compound": "hard", "planned_end_lap": 7}],
        },
    ],
    "weather_archetype": "clear_dry",
    "weather_seed_overrides": {
        "air_temp_c": 24.0,
        "track_temp_c": 31.0,
        "sc_events": [{"lap": 8, "sc_type": "full_sc", "duration_laps": 3}],
    },
    "sc_archetype": "sc_window",
    "issues": {
        "race_result": [{"goal": "finish_at_least_p3", "points": 0.20}],
        "tyre_management": [{"constraint": "compound_rule_and_health_gt_30", "points": 0.15}],
        "fuel_management": [{"constraint": "finish_with_0_5kg_margin", "points": 0.05}],
        "strategic_decisions": [
            {"decision": "pit_under_sc_or_after_window", "valid_window": [8, 10], "points": 0.30},
            {"decision": "hold_gap_during_sc_window", "points": 0.05},
            {"decision": "exactly_one_stop", "points": 0.15},
        ],
        "pending_comms": [
            {"trigger": "safety_car", "audience": "driver", "required": True, "points": 0.10}
        ],
    },
    "success_criteria": {
        "target_position": 3,
        "bonus_position": 2,
        "optimal_pit_window": [8, 10],
        "target_n_pits": 1,
        "required_compound": "hard",
        "required_actions": ["HOLD_GAP"],
        "required_comms": ["sc", "safety"],
        "fuel_margin_kg": 0.5,
        "tyre_health_min": 0.30,
    },
    "hidden_state": {
        "true_tyre_curve": {
            "medium": [1.0, 0.96, 0.92, 0.88, 0.84, 0.80, 0.76, 0.72],
            "hard": [1.0, 0.98, 0.96, 0.94, 0.92],
        },
        "opponent_strategies": {
            "4": [{"compound": "hard", "planned_end_lap": 8}],
            "11": [{"compound": "hard", "planned_end_lap": 6}],
        },
        "safety_car_schedule": [{"lap": 8, "sc_type": "full_sc", "duration_laps": 3}],
        "fuel_burn_actual": 1.50,
        "undercut_threshold_laps": 4,
    },
    "dynamic_events": [
        {
            "lap": 8,
            "type": "safety_car",
            "desc": "Full safety car deployed after an incident at Portier.",
        }
    ],
    "radio_inbox": [
        {
            "id": "R-201",
            "from": "race_engineer",
            "message": "SC probability elevated from lap 7 onward.",
        }
    ],
    "memory_hint_tags": ["safety_car", "monaco", "hold_gap"],
}


CHAMPIONSHIP_DECIDER: dict = {
    "task_name": "championship_decider_catalunya",
    "scenario_family": "championship_decider",
    "description": "Catalunya title run: cover the rival and watch the rain edge.",
    "track_name": "Catalunya",
    "total_laps": 15,
    "max_steps": 20,
    "max_score": 1.0,
    "seed": 44,
    "starting_position": 3,
    "starting_compound": "hard",
    "starting_fuel_kg": 110.0,
    "starting_drive_mode": "race",
    "championship_rival": 10,
    "opponents": [
        {
            "driver_number": 44,
            "team": "Mercedes",
            "starting_position": 1,
            "starting_compound": "medium",
            "pace_offset_s": -0.25,
            "aggression": 0.65,
            "planned_strategy": [{"compound": "soft", "planned_end_lap": 8}],
        },
        {
            "driver_number": 1,
            "team": "Red Bull",
            "starting_position": 2,
            "starting_compound": "medium",
            "pace_offset_s": -0.10,
            "aggression": 0.70,
            "planned_strategy": [{"compound": "soft", "planned_end_lap": 8}],
        },
        {
            "driver_number": 10,
            "team": "Alpine",
            "starting_position": 4,
            "starting_compound": "medium",
            "pace_offset_s": 0.00,
            "aggression": 0.78,
            "planned_strategy": [{"compound": "soft", "planned_end_lap": 7}],
        },
        {
            "driver_number": 16,
            "team": "Ferrari",
            "starting_position": 5,
            "starting_compound": "hard",
            "pace_offset_s": 0.15,
            "aggression": 0.55,
            "planned_strategy": [{"compound": "medium", "planned_end_lap": 9}],
        },
        {
            "driver_number": 4,
            "team": "McLaren",
            "starting_position": 6,
            "starting_compound": "hard",
            "pace_offset_s": 0.20,
            "aggression": 0.50,
            "planned_strategy": [{"compound": "medium", "planned_end_lap": 9}],
        },
    ],
    "weather_archetype": "mixed_conditions",
    "weather_seed_overrides": {
        "forecast_uncertainty": 0.25,
        "rain_start_lap": 9,
        "rain_peak_intensity": 0.25,
    },
    "sc_archetype": "none",
    "issues": {
        "race_result": [{"goal": "finish_p3_and_ahead_of_10", "points": 0.40}],
        "tyre_management": [{"constraint": "compound_rule_and_health_gt_30", "points": 0.15}],
        "fuel_management": [{"constraint": "finish_with_0_5kg_margin", "points": 0.05}],
        "strategic_decisions": [
            {
                "decision": "cover_rival_pit_and_check_forecast",
                "valid_window": [7, 10],
                "points": 0.20,
            }
        ],
        "pending_comms": [
            {"trigger": "rival_cover", "audience": "driver", "required": True, "points": 0.15}
        ],
        "operational_efficiency": [{"constraint": "max_two_stops_no_dnf", "points": 0.05}],
    },
    "success_criteria": {
        "target_position": 3,
        "rival_driver": 10,
        "optimal_pit_window": [7, 10],
        "target_n_pits": 1,
        "required_compound": "medium",
        "required_inspections": ["REQUEST_FORECAST", "CHECK_OPPONENT_STRATEGY"],
        "required_comms": ["rival", "cover"],
        "fuel_margin_kg": 0.5,
        "tyre_health_min": 0.30,
    },
    "hidden_state": {
        "true_tyre_curve": {
            "hard": [1.0, 0.96, 0.93, 0.89, 0.85, 0.81, 0.77, 0.73, 0.69],
            "medium": [1.0, 0.94, 0.89, 0.84, 0.79, 0.74],
        },
        "opponent_strategies": {
            "10": [{"compound": "soft", "planned_end_lap": 7}],
            "44": [{"compound": "soft", "planned_end_lap": 8}],
        },
        "fuel_burn_actual": 1.75,
        "undercut_threshold_laps": 3,
    },
    "dynamic_events": [
        {"lap": 7, "type": "rival_pit", "desc": "#10 boxes for softs; cover window is open."}
    ],
    "radio_inbox": [
        {
            "id": "R-301",
            "from": "race_engineer",
            "message": "Championship rival #10 is the priority.",
        }
    ],
    "memory_hint_tags": ["rival", "championship", "catalunya"],
}


SCENARIOS: dict[str, dict] = {
    "dry_strategy_sprint": DRY_STRATEGY_SPRINT,
    "dry_strategy_sprint_monza": DRY_STRATEGY_SPRINT,
    "weather_roulette": WEATHER_ROULETTE,
    "weather_roulette_spa": WEATHER_ROULETTE,
    "late_safety_car": LATE_SAFETY_CAR,
    "late_safety_car_monaco": LATE_SAFETY_CAR,
    "championship_decider": CHAMPIONSHIP_DECIDER,
    "championship_decider_catalunya": CHAMPIONSHIP_DECIDER,
}
