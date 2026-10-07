"""BaseRobot — abstract base for every embodiment.

A robot exposes:

- a **descriptor** (identity + capabilities),
- a **capability set**,
- a current **robot state**,
- an initial **robot state**.

Skills v0.1 do not call the robot directly — they operate on the world.
Real actuation is wired in the MuJoCo adapter at a later iteration.
This base class defines the contract that adapters must satisfy.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from orb_types import (
    CapabilitySet,
    RobotDescriptor,
    RobotId,
    RobotState,
)


class BaseRobot(ABC):
    """Abstract base class for robots.

    Subclasses must implement:

    - :meth:`descriptor`
    - :meth:`initial_state`
    - :meth:`state`
    """

    @property
    @abstractmethod
    def descriptor(self) -> RobotDescriptor:
        """Return the declarative description of this robot."""

    @abstractmethod
    def initial_state(self) -> RobotState:
        """Return the robot's initial state (at reset)."""

    @abstractmethod
    def state(self) -> RobotState:
        """Return the robot's current state."""

    # ─── Convenience ────────────────────────────────────────────────────

    @property
    def robot_id(self) -> RobotId:
        """Shortcut for ``descriptor.robot_id``."""
        return self.descriptor.robot_id

    @property
    def name(self) -> str:
        """Shortcut for ``descriptor.name``."""
        return self.descriptor.name

    def capabilities(self) -> CapabilitySet:
        """Shortcut for ``descriptor.capabilities``.

        This method makes :class:`BaseRobot` a structural
        :class:`~orb_interfaces.CapabilityProvider`.
        """
        return self.descriptor.capabilities


__all__ = ["BaseRobot"]
