"""Tests for orb_types.reasoning."""

from __future__ import annotations

import pytest
from orb_types import GoalId, ReasoningResult


def test_reasoning_result_ok() -> None:
    r = ReasoningResult(goal_id=GoalId("goal_01"), ok=True)
    assert r.ok
    assert r.errors == ()
    assert r.warnings == ()
    assert r.is_ok()


def test_reasoning_result_with_errors() -> None:
    r = ReasoningResult(
        goal_id=GoalId("goal_01"),
        ok=False,
        errors=("target missing",),
        warnings=("low confidence",),
    )
    assert not r.ok
    assert not r.is_ok()
    assert r.errors == ("target missing",)
    assert r.warnings == ("low confidence",)


def test_reasoning_result_ok_but_with_errors_is_not_ok() -> None:
    # Defensive: even if caller sets ok=True with errors, is_ok() is False.
    r = ReasoningResult(goal_id=GoalId("goal_01"), ok=True, errors=("x",))
    assert not r.is_ok()


def test_reasoning_result_frozen() -> None:
    import pydantic

    r = ReasoningResult(goal_id=GoalId("goal_01"), ok=True)
    with pytest.raises(pydantic.ValidationError):
        r.ok = False  # type: ignore[misc]
