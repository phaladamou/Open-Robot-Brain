"""State store implementation.

See :mod:`orb_runtime.state` for the design rationale.

Invariants
----------
- ``store.world`` always returns a :class:`WorldState` (never ``None``).
- ``store.robot`` returns ``None`` until the first robot state is set.
- Every successful ``update_*`` increments the corresponding version and
  publishes a :class:`Event` on the injected bus.
- Updates are **complete-state replacements**. Deltas are the job of the
  world model, not the store.
"""

from __future__ import annotations

from orb_types import (
    Event,
    EventId,
    EventKind,
    EventSeverity,
    RobotState,
    WorldState,
    new_id,
)

from orb_runtime.events.bus import EventBus


class StateStore:
    """The runtime's single source of truth for world and robot state.

    Parameters
    ----------
    bus:
        Event bus used to publish update events.
    initial_world:
        The initial world state. Required — there is no implicit "empty
        world" because the world's timestamp and version are meaningful.

    Example
    -------
    >>> store = StateStore(bus, initial_world=world)
    >>> store.world.version
    0
    >>> store.update_world(new_world)
    >>> store.world_version
    1
    """

    def __init__(self, bus: EventBus, *, initial_world: WorldState) -> None:
        self._bus = bus
        self._world: WorldState = initial_world
        self._robot: RobotState | None = None
        self._world_version: int = initial_world.version
        self._robot_version: int = 0

    # ─── Reads ──────────────────────────────────────────────────────────

    @property
    def world(self) -> WorldState:
        """The current world state (never ``None``)."""
        return self._world

    @property
    def robot(self) -> RobotState | None:
        """The current robot state, or ``None`` if never set."""
        return self._robot

    @property
    def world_version(self) -> int:
        """Version counter of the world state."""
        return self._world_version

    @property
    def robot_version(self) -> int:
        """Version counter of the robot state (0 until first update)."""
        return self._robot_version

    # ─── Writes ─────────────────────────────────────────────────────────

    def update_world(
        self,
        world: WorldState,
        *,
        correlation_id: str | None = None,
    ) -> None:
        """Replace the world state and publish ``WORLD_UPDATED``.

        The new world's ``version`` is overridden to ``world_version + 1``
        to keep monotonicity even if the caller passes an inconsistent
        version.
        """
        self._world_version += 1
        self._world = world.with_version(self._world_version)
        self._bus.publish(
            Event(
                event_id=EventId(new_id("evt")),
                kind=EventKind.WORLD_UPDATED,
                timestamp=self._world.timestamp,
                source="state_store",
                severity=EventSeverity.INFO,
                payload={"version": self._world_version},
                correlation_id=correlation_id,
            )
        )

    def update_robot(
        self,
        robot: RobotState,
        *,
        correlation_id: str | None = None,
    ) -> None:
        """Replace the robot state and publish ``ROBOT_UPDATED``-like event.

        .. note::
           ``EventKind`` currently has no ``ROBOT_UPDATED`` member. We
           publish a ``CUSTOM`` event with ``kind_label="robot.updated"``
           so no schema change is required. When ``EventKind`` is extended
           in a later iteration, this will migrate to a first-class kind.
        """
        self._robot_version += 1
        self._robot = robot
        self._bus.publish(
            Event(
                event_id=EventId(new_id("evt")),
                kind=EventKind.CUSTOM,
                timestamp=robot.timestamp,
                source="state_store",
                severity=EventSeverity.INFO,
                payload={
                    "kind_label": "robot.updated",
                    "version": self._robot_version,
                    "robot_id": robot.robot_id,
                },
                correlation_id=correlation_id,
            )
        )

    # ─── Reset ──────────────────────────────────────────────────────────

    def reset(self, *, world: WorldState | None = None) -> None:
        """Reset the store to a fresh state.

        If ``world`` is provided, it becomes the new world state and its
        version is adopted. Otherwise, the current world is kept and only
        the robot state is cleared.
        """
        if world is not None:
            self._world = world
            self._world_version = world.version
        self._robot = None
        self._robot_version = 0


__all__ = ["StateStore"]
