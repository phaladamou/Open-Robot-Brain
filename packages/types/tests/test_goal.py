"""Tests for orb_types.goal."""

from __future__ import annotations

import pytest
from orb_types.base import utc_now
from orb_types.goal import Goal, GoalKind, GoalStatus
from orb_types.ids import GoalId, ObjectId
from pydantic import ValidationError as PydanticValidationError

# ─── Goal ────────────────────────────────────────────────────────────────


def test_goal_minimal() -> None:
    g = Goal(goal_id=GoalId("goal_01"), description="Pick up the red cup", created_at=utc_now())
    assert g.description == "Pick up the red cup"
    assert g.kind == GoalKind.OTHER
    assert g.status == GoalStatus.PENDING
    assert g.args == {}


def test_goal_manipulation() -> None:
    g = Goal(
        goal_id=GoalId("goal_02"),
        description="Pick up the red cup",
        kind=GoalKind.MANIPULATION,
        predicate="holding",
        args={"object_id": "cup_01"},
        target_object=ObjectId("cup_01"),
        created_at=utc_now(),
    )
    assert g.kind == GoalKind.MANIPULATION
    assert g.predicate == "holding"
    assert g.target_object == "cup_01"
    assert g.args["object_id"] == "cup_01"


def test_goal_rejects_empty_description() -> None:
    with pytest.raises(PydanticValidationError):
        Goal(goal_id=GoalId("goal_03"), description="", created_at=utc_now())


def test_goal_is_terminal() -> None:
    g = Goal(goal_id=GoalId("goal_04"), description="x", created_at=utc_now())
    assert not g.is_terminal()

    g2 = g.model_copy(update={"status": GoalStatus.ACHIEVED})
    assert g2.is_terminal()

    g3 = g.model_copy(update={"status": GoalStatus.ACTIVE})
    assert not g3.is_terminal()


def test_goal_frozen() -> None:
    g = Goal(goal_id=GoalId("goal_05"), description="x", created_at=utc_now())
    with pytest.raises(PydanticValidationError):
        g.status = GoalStatus.ACTIVE  # type: ignore[misc]


def test_goal_kind_serializable() -> None:
    g = Goal(
        goal_id=GoalId("goal_06"),
        description="x",
        kind=GoalKind.NAVIGATION,
        created_at=utc_now(),
    )
    assert g.to_dict()["kind"] == "navigation"
    assert g.to_dict()["status"] == "pending"
