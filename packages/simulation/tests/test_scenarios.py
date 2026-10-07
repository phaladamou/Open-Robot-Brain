"""Tests for orb_simulation.scenarios."""

from __future__ import annotations

import pytest
from orb_simulation.scenarios import SCENARIOS, get_scenario


def test_scenarios_are_non_empty() -> None:
    assert len(SCENARIOS) >= 4


def test_scenarios_sorted() -> None:
    assert list(SCENARIOS) == sorted(SCENARIOS)


def test_get_known_scenario() -> None:
    s = get_scenario("pick_red_cube")
    assert s.name == "pick_red_cube"
    assert s.instruction == "pick the red cube"


def test_get_unknown_scenario_raises() -> None:
    with pytest.raises(KeyError, match="unknown scenario"):
        get_scenario("teleport_to_mars")


@pytest.mark.parametrize("name", SCENARIOS)
def test_every_scenario_builds(name: str) -> None:
    s = get_scenario(name)
    assert s.name == name
    assert s.instruction
    assert s.robot_id is not None


@pytest.mark.parametrize("name", SCENARIOS)
def test_every_scenario_is_deterministic(name: str) -> None:
    s1 = get_scenario(name)
    s2 = get_scenario(name)
    assert s1.name == s2.name
    assert s1.instruction == s2.instruction
    assert [o.object_id for o in s1.world.objects] == [o.object_id for o in s2.world.objects]


# ─── Specific scenarios ─────────────────────────────────────────────────


def test_pick_blue_cube_has_blue_cube() -> None:
    s = get_scenario("pick_blue_cube")
    obj = s.world.objects[0]
    assert obj.attributes["color"] == "blue"


def test_open_drawer_scenario_has_drawer() -> None:
    s = get_scenario("open_drawer")
    ids = {o.object_id for o in s.world.objects}
    assert "drawer_01" in ids


def test_pick_cube_among_many_has_three_cubes() -> None:
    s = get_scenario("pick_cube_among_many")
    assert len(s.world.objects) == 3
