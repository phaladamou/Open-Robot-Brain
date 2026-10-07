"""Tests for orb_types.action."""

from __future__ import annotations

import pytest
from orb_types.action import Action, ActionResult, ActionSpec, ActionStatus
from orb_types.base import utc_now
from orb_types.ids import ActionId, SkillId
from pydantic import ValidationError as PydanticValidationError

# ─── Action ──────────────────────────────────────────────────────────────


def test_action_minimal() -> None:
    a = Action(action_id=ActionId("act_01"), name="grasp", timestamp=utc_now())
    assert a.name == "grasp"
    assert a.parameters == {}
    assert a.status == ActionStatus.PENDING
    assert a.skill_id is None


def test_action_with_parameters() -> None:
    a = Action(
        action_id=ActionId("act_02"),
        name="grasp",
        parameters={"object_id": "cup_01", "approach": "top"},
        skill_id=SkillId("pick"),
        timestamp=utc_now(),
    )
    assert a.parameters["object_id"] == "cup_01"
    assert a.skill_id == "pick"


def test_action_rejects_empty_name() -> None:
    with pytest.raises(PydanticValidationError):
        Action(action_id=ActionId("act_03"), name="", timestamp=utc_now())


def test_action_is_terminal() -> None:
    a = Action(action_id=ActionId("act_04"), name="grasp", timestamp=utc_now())
    assert not a.is_terminal()

    a2 = a.model_copy(update={"status": ActionStatus.SUCCEEDED})
    assert a2.is_terminal()

    a3 = a.model_copy(update={"status": ActionStatus.RUNNING})
    assert not a3.is_terminal()


def test_action_frozen() -> None:
    a = Action(action_id=ActionId("act_05"), name="grasp", timestamp=utc_now())
    with pytest.raises(PydanticValidationError):
        a.status = ActionStatus.RUNNING  # type: ignore[misc]


def test_action_status_serializable() -> None:
    a = Action(action_id=ActionId("act_06"), name="grasp", timestamp=utc_now())
    assert a.to_dict()["status"] == "pending"


# ─── ActionSpec ──────────────────────────────────────────────────────────


def test_action_spec() -> None:
    spec = ActionSpec(
        name="grasp",
        description="Close the gripper around a target object.",
        parameters={"object_id": {"type": "string"}},
        required=("object_id",),
    )
    assert spec.name == "grasp"
    assert "object_id" in spec.required


# ─── ActionResult ────────────────────────────────────────────────────────


def test_action_result_success() -> None:
    r = ActionResult(
        action_id=ActionId("act_07"),
        status=ActionStatus.SUCCEEDED,
        timestamp=utc_now(),
    )
    assert r.status == ActionStatus.SUCCEEDED
    assert r.message is None
    assert r.payload == {}


def test_action_result_failure() -> None:
    r = ActionResult(
        action_id=ActionId("act_08"),
        status=ActionStatus.FAILED,
        timestamp=utc_now(),
        message="object not reachable",
        payload={"distance": 1.5},
    )
    assert r.message == "object not reachable"
    assert r.payload["distance"] == 1.5
