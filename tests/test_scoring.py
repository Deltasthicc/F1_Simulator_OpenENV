"""
Pytest: six-dimension scorer is pure and deterministic.

TODO Phase 2:
    - test_zero_issue_case
    - test_perfect_case
    - test_dnf_case
    - test_each_dimension_in_isolation
    - test_weighted_final_clamped_to_001_099
"""
import pytest

from server import scoring


@pytest.mark.skip(reason="Phase 2 stub")
def test_weighted_final_clamped():
    # All dims at 1.0 → weighted_final == 0.99 (clamped)
    # All dims at 0.0 → weighted_final == 0.01 (clamped)
    pass


@pytest.mark.skip(reason="Phase 2 stub")
def test_pure_function_no_side_effects():
    # Calling scoring twice with the same args returns the same dict
    pass
