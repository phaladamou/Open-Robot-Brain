"""Simulator protocol.

A simulator owns a virtual world and a virtual robot. It exposes:

- a lifecycle (``reset``, ``step``),
- the current robot state,
- a way to send a joint-space command.

Implementations live in ``simulation/`` (``MockSimulator``,
``MujocoAdapter``, …).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from orb_types import RobotState


@runtime_checkable
class Simulator(Protocol):
    """Protocol for a simulator (mock, MuJoCo, Isaac, …)."""

    def reset(self) -> None:
        """Reset the simulation to its initial state."""
        ...

    def step(self, dt: float) -> None:
        """Advance the simulation by ``dt`` seconds.

        ``dt`` must be strictly positive.
        """
        ...

    def state(self) -> RobotState:
        """Return the current robot state."""
        ...

    def set_joint_targets(self, targets: dict[str, float]) -> None:
        """Send a joint-space position target.

        Implementations interpolate toward the target over subsequent
        ``step`` calls. Unknown joint names are ignored in v0.1.
        """
        ...


__all__ = ["Simulator"]
