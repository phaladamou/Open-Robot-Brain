"""Tests for orb_types.world_state."""

from __future__ import annotations

import pytest
from orb_types.base import utc_now
from orb_types.geometry import Pose, Vec3
from orb_types.ids import AgentId, ObjectId, RobotId
from orb_types.world_state import Agent, Location, Object, Surface, WorldState
from pydantic import ValidationError as PydanticValidationError

# ─── Object ──────────────────────────────────────────────────────────────


def test_object_minimal() -> None:
    o = Object(object_id=ObjectId("cup_01"), type="cup")
    assert o.object_id == "cup_01"
    assert o.confidence == 1.0
    assert o.attributes == {}


def test_object_with_attributes() -> None:
    o = Object(
        object_id=ObjectId("cup_01"),
        type="cup",
        pose=Pose(position=Vec3(x=1.0, y=2.0, z=0.5)),
        attributes={"color": "red"},
        confidence=0.94,
    )
    assert o.attributes["color"] == "red"
    assert o.pose.position.x == 1.0
    assert o.confidence == 0.94


def test_object_rejects_bad_confidence() -> None:
    with pytest.raises(PydanticValidationError):
        Object(object_id=ObjectId("cup_01"), type="cup", confidence=1.5)


def test_object_rejects_empty_type() -> None:
    with pytest.raises(PydanticValidationError):
        Object(object_id=ObjectId("cup_01"), type="")


# ─── Agent ───────────────────────────────────────────────────────────────


def test_agent_robot() -> None:
    a = Agent(agent_id=AgentId("r2d2"), kind="robot", robot_id=RobotId("r2d2"))
    assert a.kind == "robot"
    assert a.robot_id == "r2d2"


def test_agent_human_no_robot_id() -> None:
    a = Agent(agent_id=AgentId("alice"), kind="human")
    assert a.robot_id is None


# ─── Location / Surface ──────────────────────────────────────────────────


def test_location() -> None:
    loc = Location(name="kitchen")
    assert loc.name == "kitchen"


def test_surface() -> None:
    s = Surface(name="table_01", size=(1.2, 0.8, 0.02))
    assert s.size == (1.2, 0.8, 0.02)


# ─── WorldState ──────────────────────────────────────────────────────────


def test_world_state_empty() -> None:
    ws = WorldState(timestamp=utc_now())
    assert ws.version == 0
    assert ws.objects == ()
    assert ws.agents == ()


def test_world_state_with_objects() -> None:
    cup = Object(object_id=ObjectId("cup_01"), type="cup")
    ws = WorldState(timestamp=utc_now(), objects=(cup,))
    assert len(ws.objects) == 1
    assert ws.get_object(ObjectId("cup_01")) is cup


def test_world_state_get_object_missing() -> None:
    ws = WorldState(timestamp=utc_now())
    assert ws.get_object(ObjectId("cup_01")) is None


def test_world_state_get_agent() -> None:
    a = Agent(agent_id=AgentId("r2d2"), kind="robot")
    ws = WorldState(timestamp=utc_now(), agents=(a,))
    assert ws.get_agent(AgentId("r2d2")) is a
    assert ws.get_agent(AgentId("c3po")) is None


def test_world_state_get_location() -> None:
    ws = WorldState(timestamp=utc_now(), locations=(Location(name="kitchen"),))
    assert ws.get_location("kitchen") is not None
    assert ws.get_location("garage") is None


def test_world_state_frozen() -> None:
    ws = WorldState(timestamp=utc_now())
    with pytest.raises(PydanticValidationError):
        ws.version = 1  # type: ignore[misc]


def test_world_state_with_version() -> None:
    ws = WorldState(timestamp=utc_now(), version=0)
    ws2 = ws.with_version(1)
    assert ws.version == 0
    assert ws2.version == 1
    assert ws is not ws2
