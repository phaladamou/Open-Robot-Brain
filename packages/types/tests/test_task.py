"""Tests for orb_types.task."""

from __future__ import annotations

import pytest
from orb_types.base import utc_now
from orb_types.goal import Goal, GoalKind
from orb_types.ids import GoalId, RobotId, TaskId
from orb_types.task import Task, TaskContext, TaskStatus
from pydantic import ValidationError as PydanticValidationError


def _make_goal() -> Goal:
    return Goal(
        goal_id=GoalId("goal_01"),
        description="Pick up the red cup",
        kind=GoalKind.MANIPULATION,
        created_at=utc_now(),
    )


# ─── TaskContext ─────────────────────────────────────────────────────────


def test_task_context_default() -> None:
    ctx = TaskContext()
    assert ctx.robot_id is None
    assert ctx.tags == ()


def test_task_context_full() -> None:
    ctx = TaskContext(robot_id=RobotId("r2d2"), location="kitchen", tags=("urgent",))
    assert ctx.robot_id == "r2d2"
    assert ctx.tags == ("urgent",)


# ─── Task ────────────────────────────────────────────────────────────────


def test_task_minimal() -> None:
    now = utc_now()
    t = Task(task_id=TaskId("task_01"), goal=_make_goal(), created_at=now, updated_at=now)
    assert t.status == TaskStatus.CREATED
    assert t.history == ()
    assert t.context.robot_id is None


def test_task_with_context() -> None:
    now = utc_now()
    t = Task(
        task_id=TaskId("task_02"),
        goal=_make_goal(),
        context=TaskContext(robot_id=RobotId("r2d2")),
        created_at=now,
        updated_at=now,
    )
    assert t.context.robot_id == "r2d2"


def test_task_is_terminal() -> None:
    now = utc_now()
    t = Task(task_id=TaskId("task_03"), goal=_make_goal(), created_at=now, updated_at=now)
    assert not t.is_terminal()

    t2 = t.with_status(TaskStatus.SUCCEEDED, now=now)
    assert t2.is_terminal()

    t3 = t.with_status(TaskStatus.RUNNING, now=now)
    assert not t3.is_terminal()


def test_task_with_status_updates_timestamp() -> None:
    now1 = utc_now()
    now2 = utc_now()
    t = Task(task_id=TaskId("task_04"), goal=_make_goal(), created_at=now1, updated_at=now1)
    t2 = t.with_status(TaskStatus.RUNNING, now=now2)
    assert t2.status == TaskStatus.RUNNING
    assert t2.updated_at == now2
    assert t.status == TaskStatus.CREATED  # original unchanged


def test_task_with_event_appends_history() -> None:
    now = utc_now()
    t = Task(task_id=TaskId("task_05"), goal=_make_goal(), created_at=now, updated_at=now)
    t2 = t.with_event({"kind": "started"}, now=now)
    t3 = t2.with_event({"kind": "grasp_failed"}, now=now)
    assert len(t.history) == 0
    assert len(t2.history) == 1
    assert len(t3.history) == 2
    assert t3.history[1]["kind"] == "grasp_failed"


def test_task_frozen() -> None:
    now = utc_now()
    t = Task(task_id=TaskId("task_06"), goal=_make_goal(), created_at=now, updated_at=now)
    with pytest.raises(PydanticValidationError):
        t.status = TaskStatus.RUNNING  # type: ignore[misc]


def test_task_status_serializable() -> None:
    now = utc_now()
    t = Task(task_id=TaskId("task_07"), goal=_make_goal(), created_at=now, updated_at=now)
    assert t.to_dict()["status"] == "created"
