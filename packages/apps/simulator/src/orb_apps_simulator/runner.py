"""Run a scenario end to end."""

from __future__ import annotations

import time

import structlog
from orb_brain import (
    GoalParser,
    GraspSkill,
    HtnPlanner,
    InMemorySkillRegistry,
    InspectSkill,
    LiftSkill,
    NavigateToSkill,
    ParseError,
    PullSkill,
    PushSkill,
    ReachSkill,
    Reasoner,
    ReleaseSkill,
)
from orb_embodiment import FakeRobot
from orb_runtime import EventBus, Executor, StateStore
from orb_simulation import get_scenario
from orb_types import (
    RunResult,
    RunStatus,
    Task,
    TaskId,
    new_id,
    utc_now,
)

logger = structlog.get_logger(__name__)

DEFAULT_CAPABILITIES: tuple[str, ...] = (
    "can_navigate",
    "can_manipulate",
    "can_grasp",
    "can_lift",
    "can_see",
)


def _register_skills(registry: InMemorySkillRegistry) -> None:
    registry.register_many(
        NavigateToSkill(),
        ReachSkill(),
        GraspSkill(),
        LiftSkill(),
        ReleaseSkill(),
        PullSkill(),
        PushSkill(),
        InspectSkill(),
    )


def run_scenario(scenario_name: str) -> RunResult:
    started = time.perf_counter()

    scenario = get_scenario(scenario_name)
    bus = EventBus()
    store = StateStore(bus, initial_world=scenario.world)

    robot = FakeRobot(
        robot_id=scenario.robot_id,
        name=f"Simulated {scenario.robot_id}",
        capabilities=DEFAULT_CAPABILITIES,
        kind="arm",
    )

    parser = GoalParser()
    reasoner = Reasoner(robot)
    planner = HtnPlanner()
    skills = InMemorySkillRegistry(bus)
    _register_skills(skills)

    executor = Executor(bus, planner=planner, skills=skills)

    try:
        goal = parser.parse(scenario.instruction)
    except ParseError as exc:
        duration = time.perf_counter() - started
        logger.warning("run.parse_failed", scenario=scenario_name, error=str(exc))
        return RunResult(
            scenario_name=scenario_name,
            status=RunStatus.PARSE_FAILED,
            duration_s=duration,
            message=str(exc),
        )

    reasoning = reasoner.reason(goal, store.world)
    if not reasoning.ok:
        duration = time.perf_counter() - started
        logger.warning(
            "run.reasoning_failed",
            scenario=scenario_name,
            errors=list(reasoning.errors),
        )
        return RunResult(
            scenario_name=scenario_name,
            status=RunStatus.REASONING_FAILED,
            duration_s=duration,
            goal=goal,
            reasoning=reasoning,
            message="; ".join(reasoning.errors) or "reasoning rejected the goal",
        )

    task = Task(
        task_id=TaskId(new_id("task")),
        goal=goal,
        created_at=utc_now(),
        updated_at=utc_now(),
    )
    task_result = executor.execute(task, world=store.world)

    duration = time.perf_counter() - started
    status = (
        RunStatus.SUCCEEDED
        if task_result.status.value == "succeeded"
        else RunStatus.EXECUTION_FAILED
    )
    logger.info(
        "run.finished",
        scenario=scenario_name,
        status=str(status),
        duration_s=round(duration, 4),
    )
    return RunResult(
        scenario_name=scenario_name,
        status=status,
        duration_s=duration,
        goal=goal,
        reasoning=reasoning,
        plan=task_result.plan,
        task_result=task_result,
        message=task_result.message,
    )


__all__ = ["DEFAULT_CAPABILITIES", "run_scenario"]
