"""
F1 Strategist — Physics
=========================

Pure-Python lap-time, tyre-wear, and fuel-burn model. Calibrated against the
Kaggle Formula 1 dataset (1950–2024) and OpenF1 stint statistics.

Owner: Person 1.
Spec: docs/physics-model.md.

TODO:
    - Phase 1 v0: compute_lap_time_v0 with constant base + mode + fuel
    - Phase 2 v1: full equation including tyre wear, dirty air, weather
    - Phase 2: step_tyre — per-lap health decrement
    - Phase 2: step_fuel — per-lap fuel burn
    - Phase 2: compute_dirty_air_factor(gap_to_car_ahead_s)
    - Phase 2: compute_weather_penalty(weather_state, compound, track_character)
    - Phase 2: load TYRE_BASELINE, MODE_TABLE, TRACK_TYRE_MULTIPLIER from data/

Constants:
    TYRE_BASELINE   — pace_delta_s, wear_rate, wear_penalty_s_per_unit per compound
    MODE_TABLE      — pace_delta_s, tyre_mult, fuel_mult per drive mode
    TRACK_TYRE_MULTIPLIER — multiplier per track_character bucket
    FUEL_BURN_PER_LAP     — kg/lap per track
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from server.track import Track
    from server.weather import WeatherState


def compute_lap_time(
    track: "Track",
    compound: str,
    tyre_health: float,
    fuel_kg: float,
    drive_mode: str,
    dirty_air_factor: float,
    weather: "WeatherState",
    noise_seed: int,
) -> float:
    """Full lap-time function. See docs/physics-model.md §lap-time-function-(full)."""
    raise NotImplementedError("Phase 2, Person 1")


def step_tyre(
    compound: str,
    current_health: float,
    drive_mode: str,
    track_character: str,
    base_temp_c: float,
) -> float:
    """Return the new tyre health after one lap."""
    raise NotImplementedError("Phase 2, Person 1")


def step_fuel(
    track_name: str,
    drive_mode: str,
    current_fuel_kg: float,
    noise_seed: int,
) -> float:
    """Return the new fuel level (kg) after one lap."""
    raise NotImplementedError("Phase 2, Person 1")


def compute_dirty_air_factor(gap_to_car_ahead_s: float) -> float:
    """0.0 (clear) to 1.0 (full DRS-train dirty air)."""
    if gap_to_car_ahead_s > 1.5:
        return 0.0
    elif gap_to_car_ahead_s > 0.6:
        return (1.5 - gap_to_car_ahead_s) / 0.9
    return 1.0
