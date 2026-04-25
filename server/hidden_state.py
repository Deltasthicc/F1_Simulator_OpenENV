"""
F1 Strategist — Hidden State Layer
====================================

Latent variables that drive decisions but are revealed only via inspection
actions. Direct port of OpsTwin's hidden_state.py.

Owner: Person 1.
Spec: docs/architecture.md §2.

Hidden variables per episode:
    true_tyre_curve         — actual per-lap health values per compound
    opponent_strategies     — each opponent's planned stint chain
    weather_evolution       — pre-rolled per-lap weather state
    safety_car_schedule     — pre-rolled SC events
    fuel_burn_actual        — true per-lap kg burn (may differ from displayed)
    undercut_threshold_laps — track-specific undercut viability

Inspection → revelation mapping:
    INSPECT_TYRE_DEGRADATION    → true_tyre_curve (current compound, current lap →)
    CHECK_OPPONENT_STRATEGY <n> → opponent_strategies[n].next_pit (±1 noise)
    REQUEST_FORECAST            → weather_evolution next 5 laps as ProbCones
    ASSESS_UNDERCUT_WINDOW      → undercut_threshold_laps + viability calc
    INSPECT_FUEL_MARGIN         → fuel_burn_actual vs displayed

Reward: +0.02 first time a key reveals NEW info, 0.0 on subsequent calls.
"""
from dataclasses import dataclass, field


@dataclass
class HiddenStateLayer:
    true_tyre_curve: dict = field(default_factory=dict)
    opponent_strategies: dict = field(default_factory=dict)
    weather_evolution: list = field(default_factory=list)
    safety_car_schedule: list = field(default_factory=list)
    fuel_burn_actual: float = 0.0
    undercut_threshold_laps: int = 0

    revealed: set[str] = field(default_factory=set)

    @classmethod
    def from_scenario(cls, scenario: dict) -> "HiddenStateLayer":
        """Initialise from scenario["hidden_state"] dict."""
        raise NotImplementedError("Phase 2, Person 1")

    def reveal(self, key: str, sub_key: str | None = None) -> tuple[bool, dict]:
        """Reveal a hidden variable. Returns (is_new_revelation, info_dict)."""
        full_key = f"{key}:{sub_key}" if sub_key else key
        is_new = full_key not in self.revealed
        self.revealed.add(full_key)
        # TODO Phase 2: route to the right field, return contents
        return is_new, {}
