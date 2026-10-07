"""Tests for orb_types.plan."""

from __future__ import annotations

import pytest
from orb_types import GoalId, Plan, PlanId, PlanStatus, PlanStep, SkillId, utc_now
from pydantic import ValidationError as PydanticValidationError


def test_plan_step_minimal() -> None:
    s = PlanStep(step_id="step_1", skill_id=SkillId("pick"))
    assert s.skill_id == "pick"
    assert s.parameters == {}


def test_plan_step_with_parameters() -> None:
    s = PlanStep(
        step_id="step_1",
        skill_id=SkillId("pick"),
        parameters={"object_id": "cup_01"},
    )
    assert s.parameters["object_id"] == "cup_01"


def test_plan_step_rejects_empty_step_id() -> None:
    with pytest.raises(PydanticValidationError):
        PlanStep(step_id="", skill_id=SkillId("pick"))


def test_plan_minimal() -> None:
    p = Plan(plan_id=PlanId("plan_01"), goal_id=GoalId("goal_01"), created_at=utc_now())
    assert p.status == PlanStatus.CREATED
    assert p.steps == ()
    assert p.is_empty()


def test_plan_with_steps() -> None:
    p = Plan(
        plan_id=PlanId("plan_01"),
        goal_id=GoalId("goal_01"),
        steps=(
            PlanStep(step_id="step_1", skill_id=SkillId("navigate_to")),
            PlanStep(step_id="step_2", skill_id=SkillId("pick")),
            PlanStep(step_id="step_3", skill_id=SkillId("navigate_to")),
            PlanStep(step_id="step_4", skill_id=SkillId("place")),
        ),
        created_at=utc_now(),
    )
    assert len(p.steps) == 4
    assert not p.is_empty()
    assert p.steps[0].skill_id == "navigate_to"


def test_plan_frozen() -> None:
    p = Plan(plan_id=PlanId("plan_01"), goal_id=GoalId("goal_01"), created_at=utc_now())
    with pytest.raises(PydanticValidationError):
        p.status = PlanStatus.RUNNING  # type: ignore[misc]


def test_plan_status_serializable() -> None:
    p = Plan(plan_id=PlanId("plan_01"), goal_id=GoalId("goal_01"), created_at=utc_now())
    assert p.to_dict()["status"] == "created"
