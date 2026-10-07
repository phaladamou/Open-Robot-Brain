"""Tests for orb_types.task_result."""

from __future__ import annotations

import pytest
from orb_types import (
    GoalId,
    Plan,
    PlanId,
    PlanStep,
    SkillId,
    SkillResult,
    SkillStatus,
    TaskId,
    TaskResult,
    TaskResultStatus,
    utc_now,
)
from pydantic import ValidationError as PydanticValidationError


def test_task_result_minimal() -> None:
    r = TaskResult(
        task_id=TaskId("task_01"),
        status=TaskResultStatus.SUCCEEDED,
        timestamp=utc_now(),
    )
    assert r.status == TaskResultStatus.SUCCEEDED
    assert r.plan is None
    assert r.skill_results == ()
    assert r.message is None


def test_task_result_with_plan_and_skills() -> None:
    plan = Plan(
        plan_id=PlanId("plan_01"),
        goal_id=GoalId("goal_01"),
        steps=(PlanStep(step_id="s1", skill_id=SkillId("pick")),),
        created_at=utc_now(),
    )
    sk = SkillResult(
        skill_id=SkillId("pick"),
        status=SkillStatus.SUCCEEDED,
        timestamp=utc_now(),
    )
    r = TaskResult(
        task_id=TaskId("task_01"),
        status=TaskResultStatus.SUCCEEDED,
        timestamp=utc_now(),
        plan=plan,
        skill_results=(sk,),
    )
    assert r.plan is not None
    assert r.plan.plan_id == "plan_01"
    assert len(r.skill_results) == 1


def test_task_result_not_planned() -> None:
    r = TaskResult(
        task_id=TaskId("task_01"),
        status=TaskResultStatus.NOT_PLANNED,
        timestamp=utc_now(),
        message="planner failed",
    )
    assert r.status == TaskResultStatus.NOT_PLANNED
    assert r.message == "planner failed"


def test_task_result_frozen() -> None:
    r = TaskResult(
        task_id=TaskId("task_01"),
        status=TaskResultStatus.SUCCEEDED,
        timestamp=utc_now(),
    )
    with pytest.raises(PydanticValidationError):
        r.status = TaskResultStatus.FAILED  # type: ignore[misc]


def test_task_result_status_serializable() -> None:
    r = TaskResult(
        task_id=TaskId("task_01"),
        status=TaskResultStatus.NOT_PLANNED,
        timestamp=utc_now(),
    )
    assert r.to_dict()["status"] == "not_planned"
