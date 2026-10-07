"""Tests for orb_apps_simulator.runner."""

from __future__ import annotations

import pytest
from orb_apps_simulator import run_scenario
from orb_simulation import SCENARIOS
from orb_types import RunStatus


@pytest.mark.parametrize("name", SCENARIOS)
def test_every_scenario_runs_and_succeeds(name: str) -> None:
    result = run_scenario(name)
    assert result.scenario_name == name
    assert result.status is RunStatus.SUCCEEDED, (
        f"scenario {name} failed: status={result.status}, message={result.message}"
    )


def test_run_result_has_goal_reasoning_plan() -> None:
    result = run_scenario("pick_red_cube")
    assert result.goal is not None
    assert result.reasoning is not None
    assert result.reasoning.ok
    assert result.plan is not None
    assert len(result.plan.steps) == 4


def test_run_result_has_task_result() -> None:
    result = run_scenario("pick_red_cube")
    assert result.task_result is not None
    assert result.task_result.status.value == "succeeded"
    assert len(result.task_result.skill_results) == 4


def test_duration_is_positive() -> None:
    result = run_scenario("pick_red_cube")
    assert result.duration_s > 0.0


def test_unknown_scenario_raises() -> None:
    with pytest.raises(KeyError, match="unknown scenario"):
        run_scenario("does_not_exist")


def test_open_drawer_scenario_runs() -> None:
    result = run_scenario("open_drawer")
    assert result.status is RunStatus.SUCCEEDED
    assert result.plan is not None
    assert [s.skill_id for s in result.plan.steps] == ["navigate_to", "reach", "pull"]


def test_pick_cube_among_many_resolves_blue() -> None:
    result = run_scenario("pick_cube_among_many")
    assert result.status is RunStatus.SUCCEEDED
    assert result.plan is not None
    assert result.plan.steps[0].parameters.get("object_id") == "cube_blue"


def test_run_is_deterministic() -> None:
    r1 = run_scenario("pick_red_cube")
    r2 = run_scenario("pick_red_cube")
    assert r1.status == r2.status
    assert r1.goal is not None and r2.goal is not None
    assert r1.goal.description == r2.goal.description
