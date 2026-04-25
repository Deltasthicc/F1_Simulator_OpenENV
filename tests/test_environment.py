"""
Pytest: F1StrategistEnvironment basic invariants.

TODO Phase 1:
    - test_reset_returns_valid_observation
    - test_step_stay_out_returns_zero_reward
    - test_step_unknown_command_penalises
    - test_step_done_flips_done_true
    - test_episode_terminates_at_total_laps
"""
import pytest

from server.environment import F1StrategistEnvironment
from models import F1Action


@pytest.mark.skip(reason="Phase 1 stub")
def test_reset_returns_valid_observation():
    env = F1StrategistEnvironment()
    obs = env.reset()
    assert obs is not None


@pytest.mark.skip(reason="Phase 1 stub")
def test_step_unknown_command_penalises():
    env = F1StrategistEnvironment()
    env.reset()
    result = env.step(F1Action(command="ZZZZ"))
    assert result.reward == -0.02


@pytest.mark.skip(reason="Phase 1 stub")
def test_step_done_flips_done_true():
    env = F1StrategistEnvironment()
    env.reset()
    result = env.step(F1Action(command="DONE"))
    assert result.done is True
