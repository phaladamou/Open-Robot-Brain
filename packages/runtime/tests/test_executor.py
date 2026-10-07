"""Tests for orb_runtime.executor.executor."""

from __future__ import annotations

from typing import Any

from orb_runtime.events.bus import EventBus
from orb_runtime.executor.executor import Executor
from orb_types import (
    Event,
    EventKind,
    Goal,
    GoalId,
    GoalKind,
    Plan,
    PlanId,
    PlanStep,
    Skill,
    SkillId,
    SkillResult,
    SkillStatus,
    Task,
    TaskId,
    TaskResultStatus,
    WorldState,
    utc_now,
)

# ─── Fakes ───────────────────────────────────────────────────────────────


class FakePlanner:
    def __init__(self, plan: Plan | None = None, *, raises: Exception | None = None) -> None:
        self._plan = plan
        self._raises = raises
        self.calls = 0

    def plan(self, goal: Goal, world: WorldState) -> Plan:
        self.calls += 1
        if self._raises is not None:
            raise self._raises
        assert self._plan is not None
        return self._plan


class FakeSkillRegistry:
    def __init__(self, results: dict[str, SkillStatus] | None = None) -> None:
        self._results = results or {}
        self._skills: dict[str, Skill] = {}
        self.executed: list[tuple[str, dict[str, Any]]] = []

    def register(self, skill_id: str) -> None:
        self._skills[skill_id] = Skill(skill_id=SkillId(skill_id), name=skill_id)

    def get(self, skill_id: SkillId) -> Skill | None:
        return self._skills.get(skill_id)

    def has(self, skill_id: SkillId) -> bool:
        return skill_id in self._skills

    def execute(
        self,
        skill_id: SkillId,
        parameters: dict[str, Any],
        world: WorldState,
    ) -> SkillResult:
        self.executed.append((skill_id, parameters))
        status = self._results.get(skill_id, SkillStatus.SUCCEEDED)
        return SkillResult(
            skill_id=skill_id,
            status=status,
            timestamp=utc_now(),
        )


def _task(goal_desc: str = "pick red cup") -> Task:
    now = utc_now()
    return Task(
        task_id=TaskId("task_01"),
        goal=Goal(
            goal_id=GoalId("goal_01"),
            description=goal_desc,
            kind=GoalKind.MANIPULATION,
            created_at=now,
        ),
        created_at=now,
        updated_at=now,
    )


def _plan(*skill_ids: str) -> Plan:
    return Plan(
        plan_id=PlanId("plan_01"),
        goal_id=GoalId("goal_01"),
        steps=tuple(
            PlanStep(step_id=f"s{i + 1}", skill_id=SkillId(sid)) for i, sid in enumerate(skill_ids)
        ),
        created_at=utc_now(),
    )


# ─── Success path ────────────────────────────────────────────────────────


def test_executor_empty_plan_succeeds() -> None:
    bus = EventBus()
    ex = Executor(bus, planner=FakePlanner(_plan()), skills=FakeSkillRegistry())
    result = ex.execute(_task())
    assert result.status is TaskResultStatus.SUCCEEDED
    assert result.plan is not None
    assert result.skill_results == ()


def test_executor_runs_steps_in_order() -> None:
    bus = EventBus()
    skills = FakeSkillRegistry()
    for sid in ("navigate_to", "pick", "navigate_to", "place"):
        skills.register(sid)
    planner = FakePlanner(_plan("navigate_to", "pick", "navigate_to", "place"))

    ex = Executor(bus, planner=planner, skills=skills)
    result = ex.execute(_task())

    assert result.status is TaskResultStatus.SUCCEEDED
    assert [s for s, _ in skills.executed] == ["navigate_to", "pick", "navigate_to", "place"]
    assert len(result.skill_results) == 4
    assert all(r.status is SkillStatus.SUCCEEDED for r in result.skill_results)


def test_executor_passes_step_parameters() -> None:
    bus = EventBus()
    skills = FakeSkillRegistry()
    skills.register("pick")
    plan = Plan(
        plan_id=PlanId("plan_01"),
        goal_id=GoalId("goal_01"),
        steps=(
            PlanStep(
                step_id="s1",
                skill_id=SkillId("pick"),
                parameters={"object_id": "cup_01"},
            ),
        ),
        created_at=utc_now(),
    )
    ex = Executor(bus, planner=FakePlanner(plan), skills=skills)
    ex.execute(_task())
    assert skills.executed == [("pick", {"object_id": "cup_01"})]


# ─── Planning failure ────────────────────────────────────────────────────


def test_executor_returns_not_planned_when_planner_raises() -> None:
    bus = EventBus()
    planner = FakePlanner(raises=RuntimeError("no plan"))
    ex = Executor(bus, planner=planner, skills=FakeSkillRegistry())
    result = ex.execute(_task())
    assert result.status is TaskResultStatus.NOT_PLANNED
    assert result.plan is None
    assert "no plan" in (result.message or "")


# ─── Skill failure ───────────────────────────────────────────────────────


def test_executor_stops_on_skill_failure() -> None:
    bus = EventBus()
    skills = FakeSkillRegistry(results={"pick": SkillStatus.FAILED})
    skills.register("navigate_to")
    skills.register("pick")
    skills.register("place")
    planner = FakePlanner(_plan("navigate_to", "pick", "place"))

    ex = Executor(bus, planner=planner, skills=skills)
    result = ex.execute(_task())

    assert result.status is TaskResultStatus.FAILED
    # Only two steps ran; the third (place) never executed.
    assert [s for s, _ in skills.executed] == ["navigate_to", "pick"]
    assert len(result.skill_results) == 2


# ─── Events & correlation ────────────────────────────────────────────────


def test_executor_publishes_events_with_task_correlation() -> None:
    bus = EventBus()
    received: list[Event] = []
    bus.subscribe(received.append)

    skills = FakeSkillRegistry()
    skills.register("pick")
    planner = FakePlanner(_plan("pick"))
    ex = Executor(bus, planner=planner, skills=skills)
    ex.execute(_task())

    kinds = [e.kind for e in received]
    assert EventKind.TASK_UPDATED in kinds
    assert EventKind.PLAN_CREATED in kinds
    assert EventKind.SKILL_FINISHED in kinds

    assert all(e.correlation_id == "task_01" for e in received)


def test_executor_publishes_plan_failed() -> None:
    bus = EventBus()
    received: list[Event] = []
    bus.subscribe(received.append, kind=EventKind.PLAN_FAILED)

    ex = Executor(bus, planner=FakePlanner(raises=RuntimeError("nope")), skills=FakeSkillRegistry())
    ex.execute(_task())

    assert len(received) == 1
    assert received[0].correlation_id == "task_01"
    assert "nope" in received[0].payload["error"]


def test_executor_publishes_skill_finished_with_warning_on_failure() -> None:
    bus = EventBus()
    received: list[Event] = []
    bus.subscribe(received.append, kind=EventKind.SKILL_FINISHED)

    skills = FakeSkillRegistry(results={"pick": SkillStatus.FAILED})
    skills.register("pick")
    planner = FakePlanner(_plan("pick"))
    ex = Executor(bus, planner=planner, skills=skills)
    ex.execute(_task())

    assert len(received) == 1
    assert received[0].payload["status"] == "failed"
