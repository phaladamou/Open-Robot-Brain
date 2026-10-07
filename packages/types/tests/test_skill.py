"""Tests for orb_types.skill."""

from __future__ import annotations

import pytest
from orb_types.action import ActionResult, ActionStatus
from orb_types.base import utc_now
from orb_types.ids import ActionId, CapabilityId, SkillId
from orb_types.skill import Predicate, Skill, SkillResult, SkillSpec, SkillStatus
from pydantic import ValidationError as PydanticValidationError

# ─── Predicate ───────────────────────────────────────────────────────────


def test_predicate_minimal() -> None:
    p = Predicate(name="reachable")
    assert p.name == "reachable"
    assert p.args == {}


def test_predicate_with_args() -> None:
    p = Predicate(name="holding", args={"object_id": "cup_01"})
    assert p.args["object_id"] == "cup_01"


def test_predicate_rejects_empty_name() -> None:
    with pytest.raises(PydanticValidationError):
        Predicate(name="")


# ─── SkillSpec ───────────────────────────────────────────────────────────


def test_skill_spec_default() -> None:
    s = SkillSpec()
    assert s.required == ()
    assert s.preconditions == ()
    assert s.postconditions == ()
    assert s.required_capabilities == ()


def test_skill_spec_full() -> None:
    s = SkillSpec(
        parameters={"object_id": {"type": "string"}},
        required=("object_id",),
        preconditions=(Predicate(name="reachable", args={"object_id": "cup_01"}),),
        postconditions=(Predicate(name="holding"),),
        required_capabilities=(CapabilityId("can_grasp"),),
    )
    assert "object_id" in s.required
    assert len(s.preconditions) == 1
    assert s.required_capabilities[0] == "can_grasp"


# ─── Skill ───────────────────────────────────────────────────────────────


def test_skill_minimal() -> None:
    s = Skill(skill_id=SkillId("pick"), name="pick")
    assert s.name == "pick"
    assert s.spec.required == ()


def test_skill_pick() -> None:
    s = Skill(
        skill_id=SkillId("pick"),
        name="pick",
        description="Pick an object from a surface.",
        spec=SkillSpec(
            parameters={"object_id": {"type": "string"}},
            required=("object_id",),
            preconditions=(Predicate(name="reachable"),),
            postconditions=(Predicate(name="holding"),),
            required_capabilities=(CapabilityId("can_grasp"),),
        ),
    )
    assert s.skill_id == "pick"
    assert s.spec.required_capabilities[0] == "can_grasp"


def test_skill_frozen() -> None:
    s = Skill(skill_id=SkillId("pick"), name="pick")
    with pytest.raises(PydanticValidationError):
        s.name = "place"  # type: ignore[misc]


# ─── SkillResult ─────────────────────────────────────────────────────────


def test_skill_result_minimal() -> None:
    r = SkillResult(
        skill_id=SkillId("pick"),
        status=SkillStatus.SUCCEEDED,
        timestamp=utc_now(),
    )
    assert r.status == SkillStatus.SUCCEEDED
    assert r.action_results == ()
    assert r.message is None


def test_skill_result_aggregates_actions() -> None:
    a = ActionResult(
        action_id=ActionId("act_01"),
        status=ActionStatus.SUCCEEDED,
        timestamp=utc_now(),
    )
    r = SkillResult(
        skill_id=SkillId("pick"),
        status=SkillStatus.SUCCEEDED,
        timestamp=utc_now(),
        action_results=(a,),
        payload={"grasped": True},
    )
    assert len(r.action_results) == 1
    assert r.payload["grasped"] is True


def test_skill_result_is_terminal() -> None:
    r = SkillResult(
        skill_id=SkillId("pick"),
        status=SkillStatus.RUNNING,
        timestamp=utc_now(),
    )
    assert not r.is_terminal()

    r2 = r.model_copy(update={"status": SkillStatus.SUCCEEDED})
    assert r2.is_terminal()

    r3 = r.model_copy(update={"status": SkillStatus.RECOVERED})
    assert r3.is_terminal()


def test_skill_status_serializable() -> None:
    r = SkillResult(
        skill_id=SkillId("pick"),
        status=SkillStatus.SUCCEEDED,
        timestamp=utc_now(),
    )
    assert r.to_dict()["status"] == "succeeded"
