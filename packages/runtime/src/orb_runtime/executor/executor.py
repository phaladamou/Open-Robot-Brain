"""Executor implementation.

See :mod:`orb_runtime.executor` for the design rationale.
"""

from __future__ import annotations

from orb_interfaces import Planner, SkillRegistry
from orb_types import (
    Event,
    EventId,
    EventKind,
    EventSeverity,
    Plan,
    SkillResult,
    SkillStatus,
    Task,
    TaskResult,
    TaskResultStatus,
    WorldState,
    new_id,
    utc_now,
)

from orb_runtime.events.bus import EventBus


class Executor:
    """Run a single :class:`Task` from goal to result.

    Parameters
    ----------
    bus:
        Event bus used to publish execution events.
    planner:
        The planner used to turn the task's goal into a plan.
    skills:
        The skill registry used to execute plan steps.

    Notes
    -----
    - Every event published during a task carries
      ``correlation_id = str(task.task_id)`` so the whole execution can be
      reconstructed from the event log.
    - A skill failure stops execution and yields a ``FAILED`` task result.
      Recovery and re-planning are v0.2+.
    - The executor never mutates the input task; it produces a
      :class:`TaskResult`.
    - ``world`` is passed by the caller. In v0.1 this defaults to a fresh
      empty world; in a later iteration it will be read from the
      ``StateStore``.
    """

    def __init__(
        self,
        bus: EventBus,
        *,
        planner: Planner,
        skills: SkillRegistry,
    ) -> None:
        self._bus = bus
        self._planner = planner
        self._skills = skills

    # ─── Public API ─────────────────────────────────────────────────────

    def execute(self, task: Task, *, world: WorldState | None = None) -> TaskResult:
        """Execute the given task and return its result.

        Parameters
        ----------
        task:
            The task to execute.
        world:
            The world state against which planning and skill execution run.
            Defaults to a fresh empty world (v0.1 placeholder until the
            executor is wired to the ``StateStore``).

        Steps:

        1. Publish ``TASK_UPDATED`` (RUNNING).
        2. Ask the planner for a plan. On failure, publish ``PLAN_FAILED``
           and return a ``NOT_PLANNED`` task result.
        3. Publish ``PLAN_CREATED``.
        4. For each step, execute the skill. On non-success, stop and
           return a ``FAILED`` task result.
        5. Return a ``SUCCEEDED`` task result with all skill results.
        """
        if world is None:
            world = WorldState(timestamp=utc_now())

        correlation_id = str(task.task_id)
        self._publish_task_updated(task, correlation_id=correlation_id)

        # ─── Plan ───────────────────────────────────────────────────────
        try:
            plan = self._planner.plan(task.goal, world)
        except Exception as exc:
            self._publish_plan_failed(task, exc, correlation_id=correlation_id)
            return TaskResult(
                task_id=task.task_id,
                status=TaskResultStatus.NOT_PLANNED,
                timestamp=utc_now(),
                message=f"planning failed: {exc}",
            )

        self._publish_plan_created(task, plan, correlation_id=correlation_id)

        # ─── Execute steps ──────────────────────────────────────────────
        skill_results: list[SkillResult] = []
        for step in plan.steps:
            result = self._skills.execute(step.skill_id, step.parameters, world)
            skill_results.append(result)
            self._publish_skill_finished(task, result, correlation_id=correlation_id)
            if result.status is not SkillStatus.SUCCEEDED:
                return TaskResult(
                    task_id=task.task_id,
                    status=TaskResultStatus.FAILED,
                    timestamp=utc_now(),
                    plan=plan,
                    skill_results=tuple(skill_results),
                    message=f"skill {step.skill_id!r} failed: {result.status}",
                )

        return TaskResult(
            task_id=task.task_id,
            status=TaskResultStatus.SUCCEEDED,
            timestamp=utc_now(),
            plan=plan,
            skill_results=tuple(skill_results),
        )

    # ─── Event helpers ──────────────────────────────────────────────────

    def _publish_task_updated(self, task: Task, *, correlation_id: str) -> None:
        self._bus.publish(
            Event(
                event_id=EventId(new_id("evt")),
                kind=EventKind.TASK_UPDATED,
                timestamp=utc_now(),
                source="executor",
                severity=EventSeverity.INFO,
                payload={"task_id": task.task_id, "status": "running"},
                correlation_id=correlation_id,
            )
        )

    def _publish_plan_created(self, task: Task, plan: Plan, *, correlation_id: str) -> None:
        self._bus.publish(
            Event(
                event_id=EventId(new_id("evt")),
                kind=EventKind.PLAN_CREATED,
                timestamp=utc_now(),
                source="executor",
                severity=EventSeverity.INFO,
                payload={"task_id": task.task_id, "n_steps": len(plan.steps)},
                correlation_id=correlation_id,
            )
        )

    def _publish_plan_failed(self, task: Task, exc: BaseException, *, correlation_id: str) -> None:
        self._bus.publish(
            Event(
                event_id=EventId(new_id("evt")),
                kind=EventKind.PLAN_FAILED,
                timestamp=utc_now(),
                source="executor",
                severity=EventSeverity.ERROR,
                payload={"task_id": task.task_id, "error": str(exc)},
                correlation_id=correlation_id,
            )
        )

    def _publish_skill_finished(
        self, task: Task, result: SkillResult, *, correlation_id: str
    ) -> None:
        self._bus.publish(
            Event(
                event_id=EventId(new_id("evt")),
                kind=EventKind.SKILL_FINISHED,
                timestamp=utc_now(),
                source="executor",
                severity=(
                    EventSeverity.INFO
                    if result.status is SkillStatus.SUCCEEDED
                    else EventSeverity.WARNING
                ),
                payload={
                    "task_id": task.task_id,
                    "skill_id": result.skill_id,
                    "status": result.status,
                },
                correlation_id=correlation_id,
            )
        )


__all__ = ["Executor"]
