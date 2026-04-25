"""
F1 Strategist — Environment
=============================

Core reset/step/_obs/_exec/_load loop. Direct port of OpsTwinEnvironment.

Owner: Person 1 (Shashwat).
Spec: docs/architecture.md §1, docs/build-order.md Phase 1.
Build order:
    Phase 1: skeleton with stub action handlers, returning (0.0, "stub")
    Phase 2: wire physics, opponents, weather, scenarios, hidden state
    Phase 4: wire postmortem on _done

Conventions (from CLAUDE.md):
    - copy.deepcopy(scenario) on every _load — never mutate templates
    - _audit_trail entries: {step, action, reward, resolved_count}
    - SUPPORTS_CONCURRENT_SESSIONS = True
    - LAPS_PER_STEP = 1
    - PIT_COOLDOWN_LAPS = 2
"""
from __future__ import annotations
import copy
import uuid
from datetime import datetime
from typing import Any, Optional

from openenv.core.env_server import Environment, StepResult

from models import F1Action, F1Observation, F1State


class F1StrategistEnvironment(Environment[F1Action, F1Observation, F1State]):
    """Race-strategy environment.

    See docs/architecture.md §1 for the loop spec, §6 for the observation schema,
    and §7 for the action grammar.
    """

    SUPPORTS_CONCURRENT_SESSIONS = True
    LAPS_PER_STEP = 1
    PIT_COOLDOWN_LAPS = 2

    def __init__(self) -> None:
        # Race state
        self._track = None
        self._ego_car = None
        self._opponents: list = []
        self._weather = None

        # Episode bookkeeping
        self._lap = 0
        self._total_laps = 0
        self._max_steps = 0
        self._step_count = 0
        self._done = False
        self._episode_id = ""

        # Audit and rewards
        self._audit_trail: list[dict] = []
        self._fired_events: set[str] = set()
        self._dynamic_events: list[dict] = []
        self._pending_rewards: dict = {}
        self._pit_cooldown_remaining = 0

        # Scenario context
        self._scenario: dict | None = None
        self._hidden_state = None
        self._issue_resolutions: dict = {}

        # Inspection / comms tracking
        self._inspection_calls: dict[str, list[int]] = {}
        self._pit_decisions: list = []
        self._radio_calls: list = []
        self._pit_wall_calls: list = []

        self._reset_internal()

    # ──────────────────────────────────────────────────────────────────
    # OpenEnv API
    # ──────────────────────────────────────────────────────────────────

    def reset(self, options: Optional[dict] = None) -> F1Observation:
        """Reset the environment. options may include task, seed, difficulty.

        Loads the scenario, initialises track/ego/opponents/weather/hidden_state,
        and returns the initial observation. Injects memory_hints from past
        postmortems if available.
        """
        # TODO Phase 1: pick scenario from options, load default if missing
        # TODO Phase 1: call self._load(scenario_dict)
        # TODO Phase 4: inject PostmortemMemory.retrieve(family) into obs.memory_hints
        self._reset_internal()
        return self._obs()

    def step(self, action: F1Action) -> StepResult:
        """Execute one strategic action.

        Lifecycle:
            1. _exec(action) → (immediate_reward, message)
            2. advance_lap() → run physics, run opponents, fire dynamic events
            3. finalize pending delayed rewards
            4. check _done
            5. build observation, return StepResult
        """
        if self._done:
            return StepResult(observation=self._obs(), reward=0.0, done=True)

        immediate_reward, message = self._exec(action)
        self._step_count += 1

        # Advance the simulated world by one lap
        self._advance_lap()

        # Finalize any pending delayed rewards based on newly-revealed state
        delayed_reward = self._finalize_pending_rewards()

        # Append to audit trail
        self._audit_trail.append({
            "step": self._step_count,
            "lap": self._lap,
            "action": action.command,
            "reward": immediate_reward + delayed_reward,
            "resolved_count": len([k for k, v in self._issue_resolutions.items() if v]),
        })

        # Termination check
        self._check_done()

        total_reward = immediate_reward + delayed_reward
        obs = self._obs()
        obs.reward = total_reward
        obs.done = self._done
        obs.message = message
        return StepResult(observation=obs, reward=total_reward, done=self._done)

    def state(self) -> F1State:
        """Return episode metadata."""
        return F1State(
            episode_id=self._episode_id,
            step_count=self._step_count,
            task_name=self._scenario.get("task_name", "") if self._scenario else "",
            scenario_family=self._scenario.get("scenario_family", "") if self._scenario else "",
            track_name=self._scenario.get("track_name", "") if self._scenario else "",
            total_laps=self._total_laps,
            resolved_issues=len([k for k, v in self._issue_resolutions.items() if v]),
            total_issues=len(self._issue_resolutions),
            max_steps=self._max_steps,
            seed=self._scenario.get("seed", 0) if self._scenario else 0,
        )

    # ──────────────────────────────────────────────────────────────────
    # Internal
    # ──────────────────────────────────────────────────────────────────

    def _reset_internal(self) -> None:
        """Wipe state for a fresh episode."""
        self._lap = 0
        self._step_count = 0
        self._done = False
        self._episode_id = uuid.uuid4().hex[:12]
        self._audit_trail = []
        self._fired_events = set()
        self._dynamic_events = []
        self._pending_rewards = {}
        self._pit_cooldown_remaining = 0
        self._issue_resolutions = {}
        self._inspection_calls = {}
        self._pit_decisions = []
        self._radio_calls = []
        self._pit_wall_calls = []

    def _load(self, scenario_dict: dict) -> None:
        """Load a scenario into the env. Always deep-copy the input."""
        self._scenario = copy.deepcopy(scenario_dict)
        # TODO Phase 1: track = load_track(self._scenario["track_name"])
        # TODO Phase 2: initialise opponents from self._scenario["opponents"]
        # TODO Phase 2: weather = WeatherSchedule.from_seed(seed, archetype, total_laps)
        # TODO Phase 2: hidden_state = HiddenStateLayer(self._scenario)
        # TODO Phase 2: build self._issue_resolutions from self._scenario["issues"]
        self._total_laps = self._scenario.get("total_laps", 10)
        self._max_steps = self._scenario.get("max_steps", self._total_laps + 4)

    def _exec(self, action: F1Action) -> tuple[float, str]:
        """Parse a command and route to a handler. Returns (reward, message)."""
        cmd = action.command.strip()
        if not cmd:
            return -0.02, "Empty command."

        verb, *rest = cmd.split(None, 1)
        verb = verb.upper()
        arg = rest[0] if rest else ""

        # TODO Phase 1: route to one of ~20 handler methods
        # Phase 1 stubs — every handler returns (0.0, "stub")
        handlers = {
            "PIT_NOW": self._h_pit_now,
            "STAY_OUT": self._h_stay_out,
            "RECOMMEND_PIT": self._h_recommend_pit,
            "SET_MODE": self._h_set_mode,
            "DRS_PERMISSION": self._h_drs_permission,
            "DEFEND_POSITION": self._h_defend_position,
            "ATTACK_AHEAD": self._h_attack_ahead,
            "HOLD_GAP": self._h_hold_gap,
            "LET_BY": self._h_let_by,
            "INSPECT_TYRE_DEGRADATION": self._h_inspect_tyre,
            "CHECK_OPPONENT_STRATEGY": self._h_check_opponent,
            "REQUEST_FORECAST": self._h_request_forecast,
            "ASSESS_UNDERCUT_WINDOW": self._h_assess_undercut,
            "INSPECT_FUEL_MARGIN": self._h_inspect_fuel,
            "RADIO_DRIVER": self._h_radio_driver,
            "DRAFT_PIT_WALL": self._h_draft_pit_wall,
            "BRIEF_MEDIA": self._h_brief_media,
            "REQUEST_INFO": self._h_request_info,
            "ESCALATE_TO_PRINCIPAL": self._h_escalate,
            "DONE": self._h_done,
        }

        handler = handlers.get(verb)
        if handler is None:
            return -0.02, f"Unknown command: {verb}"

        return handler(arg)

    def _advance_lap(self) -> None:
        """Run physics and opponents for one lap. Fire dynamic events."""
        self._lap += 1
        # TODO Phase 2: physics.step(self._ego_car, ...)
        # TODO Phase 2: opponents.step_opponents(self._opponents, ...)
        # TODO Phase 2: weather.advance(self._lap)
        # TODO Phase 2: fire dynamic_events scheduled for self._lap
        if self._pit_cooldown_remaining > 0:
            self._pit_cooldown_remaining -= 1

    def _finalize_pending_rewards(self) -> float:
        """Release or withhold previously-pending rewards based on revealed state."""
        # TODO Phase 2: iterate self._pending_rewards, finalize those whose
        # hidden_state_key has now been revealed, accumulate the delta
        return 0.0

    def _check_done(self) -> None:
        """Set self._done if any termination condition is met."""
        if self._lap >= self._total_laps:
            self._done = True
        if self._step_count >= self._max_steps:
            self._done = True
        # TODO Phase 2: ego_car DNF (fuel < 0 or terminal tyre failure)
        # TODO Phase 4: on _done, generate postmortem

    def _obs(self) -> F1Observation:
        """Build the filtered observation. Hidden state stays hidden."""
        # TODO Phase 1/2: populate from self._track, self._ego_car, self._opponents, self._weather
        return F1Observation(
            done=self._done,
            reward=None,
            current_lap=self._lap,
            total_laps=self._total_laps,
            race_phase=self._race_phase(),
            race_status="green",  # TODO Phase 2: derive from weather/SC schedule
            ego_position=0,
            ego_tyre_compound="",
            ego_tyre_age_laps=0,
            ego_tyre_health_pct=1.0,
            ego_fuel_remaining_kg=0.0,
            ego_drive_mode="race",
            ego_last_lap_time_s=0.0,
            opponents=[],
            weather_current={},
            weather_forecast=[],
            pit_window_alerts=[],
            cascade_alerts=[],
            uncertainty_alerts=[],
            radio_inbox=[],
            pending_issues_count=len([k for k, v in self._issue_resolutions.items() if not v]),
            resolved_issues_count=len([k for k, v in self._issue_resolutions.items() if v]),
            total_issues_count=len(self._issue_resolutions),
            message="",
            available_commands=self._available_commands(),
            multi_objective_scores={},
            score=0.0,
            hint="",
            memory_hints=[],
        )

    def _race_phase(self) -> str:
        if self._total_laps == 0:
            return "start"
        f = self._lap / self._total_laps
        if f < 0.33:
            return "start"
        elif f < 0.67:
            return "mid"
        return "end"

    def _available_commands(self) -> list[str]:
        return [
            "PIT_NOW", "STAY_OUT", "RECOMMEND_PIT",
            "SET_MODE", "DRS_PERMISSION",
            "DEFEND_POSITION", "ATTACK_AHEAD", "HOLD_GAP", "LET_BY",
            "INSPECT_TYRE_DEGRADATION", "CHECK_OPPONENT_STRATEGY",
            "REQUEST_FORECAST", "ASSESS_UNDERCUT_WINDOW", "INSPECT_FUEL_MARGIN",
            "RADIO_DRIVER", "DRAFT_PIT_WALL", "BRIEF_MEDIA",
            "REQUEST_INFO", "ESCALATE_TO_PRINCIPAL", "DONE",
        ]

    # ──────────────────────────────────────────────────────────────────
    # Action handlers (Phase 1: stubs; Phase 2: real implementations)
    # ──────────────────────────────────────────────────────────────────

    def _h_pit_now(self, arg: str) -> tuple[float, str]:
        # TODO Phase 2: validate compound, check pit_cooldown, apply pit_loss,
        # reset tyre age, change compound, append PitDecision, resolve relevant issues
        return 0.0, "stub: PIT_NOW"

    def _h_stay_out(self, arg: str) -> tuple[float, str]:
        return 0.0, "stub: STAY_OUT"

    def _h_recommend_pit(self, arg: str) -> tuple[float, str]:
        return 0.0, "stub: RECOMMEND_PIT"

    def _h_set_mode(self, arg: str) -> tuple[float, str]:
        return 0.0, "stub: SET_MODE"

    def _h_drs_permission(self, arg: str) -> tuple[float, str]:
        return 0.0, "stub: DRS_PERMISSION"

    def _h_defend_position(self, arg: str) -> tuple[float, str]:
        return 0.0, "stub: DEFEND_POSITION"

    def _h_attack_ahead(self, arg: str) -> tuple[float, str]:
        return 0.0, "stub: ATTACK_AHEAD"

    def _h_hold_gap(self, arg: str) -> tuple[float, str]:
        return 0.0, "stub: HOLD_GAP"

    def _h_let_by(self, arg: str) -> tuple[float, str]:
        return 0.0, "stub: LET_BY"

    def _h_inspect_tyre(self, arg: str) -> tuple[float, str]:
        # TODO Phase 2: hidden_state.reveal("true_tyre_curve") → +0.02 if new
        return 0.0, "stub: INSPECT_TYRE_DEGRADATION"

    def _h_check_opponent(self, arg: str) -> tuple[float, str]:
        return 0.0, "stub: CHECK_OPPONENT_STRATEGY"

    def _h_request_forecast(self, arg: str) -> tuple[float, str]:
        return 0.0, "stub: REQUEST_FORECAST"

    def _h_assess_undercut(self, arg: str) -> tuple[float, str]:
        return 0.0, "stub: ASSESS_UNDERCUT_WINDOW"

    def _h_inspect_fuel(self, arg: str) -> tuple[float, str]:
        return 0.0, "stub: INSPECT_FUEL_MARGIN"

    def _h_radio_driver(self, arg: str) -> tuple[float, str]:
        # TODO Phase 2: append to self._radio_calls, check trigger match
        return 0.0, "stub: RADIO_DRIVER"

    def _h_draft_pit_wall(self, arg: str) -> tuple[float, str]:
        return 0.0, "stub: DRAFT_PIT_WALL"

    def _h_brief_media(self, arg: str) -> tuple[float, str]:
        return 0.0, "stub: BRIEF_MEDIA"

    def _h_request_info(self, arg: str) -> tuple[float, str]:
        return 0.0, "stub: REQUEST_INFO"

    def _h_escalate(self, arg: str) -> tuple[float, str]:
        return 0.0, "stub: ESCALATE_TO_PRINCIPAL"

    def _h_done(self, arg: str) -> tuple[float, str]:
        self._done = True
        # TODO Phase 2: finalize scoring via compute_multi_objective_scores
        # TODO Phase 4: PostmortemMemory.record(...)
        return 0.0, "Episode ended."
