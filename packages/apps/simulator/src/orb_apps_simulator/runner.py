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
    WorldModel,
)
from orb_embodiment import (
    FULL_ARM_CAPABILITIES,
    SHORT_ARM_CAPABILITIES,
    WEAK_ARM_CAPABILITIES,
    FakeRobot,
)
from orb_runtime import EventBus, Executor, StateStore
from orb_simulation import MockSensor, get_scenario
from orb_types import (
    Event,
    EventId,
    EventKind,
    Observation,
    RunResult,
    RunStatus,
    Scenario,
    Task,
    TaskId,
    new_id,
    utc_now,
)

logger = structlog.get_logger(__name__)

DEFAULT_CAPABILITIES: tuple[str, ...] = FULL_ARM_CAPABILITIES
"""Capabilities of the default reference body."""

ROBOT_CAPABILITIES: dict[str, tuple[str, ...]] = {
    "mock": FULL_ARM_CAPABILITIES,
    "short_arm": SHORT_ARM_CAPABILITIES,
    "weak_arm": WEAK_ARM_CAPABILITIES,
}
"""Body name (``Scenario.robot_id``) → capability set."""

PERCEPTION_TICKS: int = 3
"""Perception ticks before planning. Each tick re-senses the world."""

PERCEPTION_SEED: int = 7
"""Fixed sensor seed: perception is deterministic across runs."""

PERCEPTION_POSITION_NOISE_M: float = 0.001
"""Sensor pose noise half-range in meters (1 mm)."""


def _resolve_capabilities(scenario: Scenario) -> tuple[str, ...]:
    """Return the capability set for the scenario's body."""
    body = str(scenario.robot_id) if scenario.robot_id is not None else "mock"
    if body not in ROBOT_CAPABILITIES:
        msg = f"unknown robot body: {body!r} (known: {', '.join(sorted(ROBOT_CAPABILITIES))})"
        raise KeyError(msg)
    return ROBOT_CAPABILITIES[body]


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


def _publish_observation(bus: EventBus, obs: Observation) -> None:
    """Publish one observation following the v0.1 bus convention."""
    bus.publish(
        Event(
            event_id=EventId(new_id("evt")),
            kind=EventKind.OBSERVATION_CREATED,
            timestamp=utc_now(),
            source="perception",
            payload={"observation": obs},
        )
    )


def _run_perception_ticks(bus: EventBus, store: StateStore) -> int:
    """Sense the world and let the world model absorb it.

    Returns the number of observations applied, counted as the
    ``WORLD_UPDATED`` events published while the sensor ticks. The bus is
    synchronous, so every published observation is applied before this
    returns.
    """
    applied = 0

    def _count_applied(event: Event) -> None:
        nonlocal applied
        applied += 1

    sensor = MockSensor(
        position_noise=PERCEPTION_POSITION_NOISE_M,
        seed=PERCEPTION_SEED,
    )
    counter = bus.subscribe(_count_applied, kind=EventKind.WORLD_UPDATED)
    try:
        for _ in range(PERCEPTION_TICKS):
            for obs in sensor.sense(store.world):
                _publish_observation(bus, obs)
    finally:
        bus.unsubscribe(counter)
    return applied


def run_scenario(scenario_name: str) -> RunResult:
    started = time.perf_counter()

    scenario = get_scenario(scenario_name)
    bus = EventBus()
    store = StateStore(bus, initial_world=scenario.world)

    # Real perception loop: the world model stays subscribed for the whole
    # run and absorbs sensor ticks before planning. Everything here is
    # function-scoped, so no explicit stop is needed.
    model = WorldModel(bus, store)
    model.start()
    observations_applied = _run_perception_ticks(bus, store)

    robot = FakeRobot(
        robot_id=scenario.robot_id,
        name=f"Simulated {scenario.robot_id}",
        capabilities=_resolve_capabilities(scenario),
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
            observations_applied=observations_applied,
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
            observations_applied=observations_applied,
        )

    task = Task(
        task_id=TaskId(new_id("task")),
        goal=goal,
        created_at=utc_now(),
        updated_at=utc_now(),
    )
    task_result = executor.execute(task, world=store.world, capabilities=robot.capabilities())

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
        observations_applied=observations_applied,
    )


__all__ = [
    "DEFAULT_CAPABILITIES",
    "PERCEPTION_POSITION_NOISE_M",
    "PERCEPTION_SEED",
    "PERCEPTION_TICKS",
    "ROBOT_CAPABILITIES",
    "run_scenario",
]
