"""World state representation for Open Robot Brain.

The world state is the **shared representation** every cognitive layer
(perception, reasoning, planning, memory) operates around.

Design
------
- ``WorldState`` is a **snapshot**: immutable, timestamped, versioned.
- Entities are typed Pydantic models with validated fields.
- Lists of entities use ``tuple`` (immutability, hashable, safe to share).
- Updates happen by **replacement**, not mutation.

This is v0.1 scope: objects, agents, locations, surfaces. Advanced fields
(relations, obstacles, uncertainty, temporal history) will be added later.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from orb_types.base import ORBModel, Timestamp
from orb_types.geometry import Pose
from orb_types.ids import AgentId, ObjectId, RobotId

# ─── Primitive entities ──────────────────────────────────────────────────

NonEmptyStr = Annotated[str, Field(min_length=1)]


class Location(ORBModel):
    """A named place in the world (e.g. ``"kitchen"``, ``"table_01"``)."""

    name: NonEmptyStr
    pose: Pose = Field(default_factory=Pose.origin)


class Surface(ORBModel):
    """A surface objects can rest on (table, shelf, floor)."""

    name: NonEmptyStr
    pose: Pose = Field(default_factory=Pose.origin)
    size: tuple[float, float, float] = (1.0, 1.0, 0.01)  # (x, y, z) in meters


class Object(ORBModel):
    """A physical object the brain can reason about.

    ``object_id`` uniquely identifies the object in the world. ``type`` and
    ``attributes`` carry semantic information (e.g. ``type="cup"``,
    ``attributes={"color": "red"}``). ``pose`` is the world-frame pose.
    """

    object_id: ObjectId
    type: NonEmptyStr
    pose: Pose = Field(default_factory=Pose.origin)
    attributes: dict[str, str] = Field(default_factory=dict)
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 1.0
    """Perception confidence in [0, 1]. ``1.0`` means ground truth (e.g. simulation)."""


class Agent(ORBModel):
    """An agent in the world — a robot, a human, or another acting entity."""

    agent_id: AgentId
    kind: NonEmptyStr  # "robot" | "human" | "other"
    pose: Pose = Field(default_factory=Pose.origin)
    robot_id: RobotId | None = None
    """If this agent is a robot, the corresponding :class:`RobotId`."""


# ─── WorldState ──────────────────────────────────────────────────────────


class WorldState(ORBModel):
    """Immutable snapshot of the world at a point in time.

    Fields
    ------
    timestamp:
        When this snapshot was produced.
    version:
        Monotonically increasing version counter. Incremented by the
        world model on each update.
    objects:
        Immutable tuple of :class:`Object`.
    agents:
        Immutable tuple of :class:`Agent`.
    locations:
        Immutable tuple of :class:`Location`.
    surfaces:
        Immutable tuple of :class:`Surface`.
    """

    timestamp: Timestamp
    version: int = Field(ge=0, default=0)
    objects: tuple[Object, ...] = ()
    agents: tuple[Agent, ...] = ()
    locations: tuple[Location, ...] = ()
    surfaces: tuple[Surface, ...] = ()

    # ─── Lookups ─────────────────────────────────────────────────────────

    def get_object(self, object_id: ObjectId) -> Object | None:
        """Return the object with the given ID, or ``None``."""
        for obj in self.objects:
            if obj.object_id == object_id:
                return obj
        return None

    def get_agent(self, agent_id: AgentId) -> Agent | None:
        """Return the agent with the given ID, or ``None``."""
        for agent in self.agents:
            if agent.agent_id == agent_id:
                return agent
        return None

    def get_location(self, name: str) -> Location | None:
        """Return the location with the given name, or ``None``."""
        for loc in self.locations:
            if loc.name == name:
                return loc
        return None

    # ─── Evolution ───────────────────────────────────────────────────────

    def with_version(self, version: int) -> WorldState:
        """Return a copy with the given version number."""
        return self.model_copy(update={"version": version})


__all__ = [
    "Agent",
    "Location",
    "NonEmptyStr",
    "Object",
    "Surface",
    "WorldState",
]
