"""Tests for orb_types.scenario."""

from __future__ import annotations

import pytest
from orb_types import (
    Object,
    ObjectId,
    RobotId,
    Scenario,
    WorldState,
    utc_now,
)
from pydantic import ValidationError as PydanticValidationError


def _world() -> WorldState:
    return WorldState(
        timestamp=utc_now(),
        objects=(Object(object_id=ObjectId("cube_red"), type="cube"),),
    )


def test_scenario_minimal() -> None:
    s = Scenario(name="test", instruction="pick the red cube", world=_world())
    assert s.name == "test"
    assert s.instruction == "pick the red cube"
    assert s.robot_id is None
    assert s.metadata == {}


def test_scenario_with_metadata() -> None:
    s = Scenario(
        name="test",
        instruction="pick the red cube",
        world=_world(),
        robot_id=RobotId("mock"),
        metadata={"difficulty": "easy"},
    )
    assert s.robot_id == "mock"
    assert s.metadata["difficulty"] == "easy"


def test_scenario_rejects_empty_name() -> None:
    with pytest.raises(PydanticValidationError):
        Scenario(name="", instruction="x", world=_world())


def test_scenario_rejects_empty_instruction() -> None:
    with pytest.raises(PydanticValidationError):
        Scenario(name="x", instruction="", world=_world())


def test_scenario_frozen() -> None:
    s = Scenario(name="test", instruction="x", world=_world())
    with pytest.raises(PydanticValidationError):
        s.name = "other"  # type: ignore[misc]


def test_scenario_serializable() -> None:
    s = Scenario(name="test", instruction="pick the red cube", world=_world())
    payload = s.to_dict()
    assert payload["name"] == "test"
    assert payload["world"]["objects"][0]["object_id"] == "cube_red"
