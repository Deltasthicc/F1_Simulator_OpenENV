"""
F1 Strategist — Weather + Safety Car
=====================================

Pre-rolled per-lap weather and SC events from a seed. Ground truth lives in
WeatherSchedule.per_lap; the agent only sees current + a forecast cone via
REQUEST_FORECAST.

Owner: Person 1.
Spec: docs/architecture.md §5, docs/scenarios.md (per-family weather archetypes).

TODO:
    - Phase 2: WeatherState, WeatherSchedule, ProbCone dataclasses
    - Phase 2: from_seed(seed, archetype, n_laps) for each archetype:
        "clear_dry" | "light_rain_window" | "heavy_rain_lottery"
        | "safety_car_prone" | "mixed_conditions"
    - Phase 2: observe(current_lap, k_laps_ahead) returns probability cone
    - Phase 2: roll SC events from scenario["sc_archetype"]
"""
from dataclasses import dataclass, field


@dataclass
class WeatherState:
    air_temp_c: float = 25.0
    track_temp_c: float = 35.0
    rain_intensity: float = 0.0   # 0.0=dry, 0.3=light, 0.7=heavy
    surface_state: str = "dry"    # "dry" | "damp" | "wet"


@dataclass
class ProbCone:
    """Forecast for a future lap. Both bounds are rain_intensity values."""
    lap: int
    lower: float
    upper: float
    median: float


@dataclass
class SCEvent:
    lap: int
    sc_type: str   # "full_sc" | "vsc"
    duration_laps: int


@dataclass
class WeatherSchedule:
    per_lap: list[WeatherState] = field(default_factory=list)  # ground truth, hidden
    sc_events: list[SCEvent] = field(default_factory=list)
    forecast_uncertainty: float = 0.2

    @classmethod
    def from_seed(cls, seed: int, archetype: str, n_laps: int) -> "WeatherSchedule":
        raise NotImplementedError("Phase 2, Person 1")

    def observe(self, current_lap: int, k_laps_ahead: int = 5) -> list[ProbCone]:
        """Return forecast cone for the next k laps."""
        raise NotImplementedError("Phase 2, Person 1")

    def is_sc_active(self, lap: int) -> bool:
        for evt in self.sc_events:
            if evt.lap <= lap < evt.lap + evt.duration_laps:
                return True
        return False
