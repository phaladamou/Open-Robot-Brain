"""FakeRobot — an in-memory robot for tests and demos.

The fake robot exposes a configurable capability set and a state that
can be updated externally. It is used to exercise the cognitive pipeline
(parsing, reasoning, planning, skills) without a simulator.
"""

from __future__ import annotations

from orb_types import (
    Capability,
    CapabilityId,
    CapabilityKind,
    CapabilitySet,
    RobotDescriptor,
    RobotId,
    RobotState,
    utc_now,
)

from orb_embodiment.abstraction.robot import BaseRobot

# ─── Default capability templates ────────────────────────────────────────

_DEFAULT_CAPABILITIES: tuple[tuple[str, CapabilityKind], ...] = (
    ("can_navigate", CapabilityKind.NAVIGATION),
    ("can_manipulate", CapabilityKind.MANIPULATION),
    ("can_grasp", CapabilityKind.MANIPULATION),
    ("can_lift", CapabilityKind.MANIPULATION),
    ("can_see", CapabilityKind.PERCEPTION),
)


class FakeRobot(BaseRobot):
    """An in-memory robot with configurable capabilities.

    Parameters
    ----------
    robot_id:
        Identifier for this robot. Defaults to ``"fake"``.
    name:
        Human-readable name. Defaults to ``"Fake Robot"``.
    capabilities:
        Optional capability names to expose. If ``None``, a default set
        (navigate, manipulate, grasp, lift, see) is used.
    kind:
        Optional coarse kind (``"arm"``, ``"mobile"``, ``"humanoid"``).
    """

    def __init__(
        self,
        *,
        robot_id: RobotId | None = None,
        name: str = "Fake Robot",
        capabilities: tuple[str, ...] | None = None,
        kind: str | None = None,
    ) -> None:
        rid = RobotId(robot_id) if robot_id is not None else RobotId("fake")
        caps = self._build_capabilities(capabilities)
        self._descriptor = RobotDescriptor(
            robot_id=rid,
            name=name,
            capabilities=caps,
            kind=kind,
        )
        self._state = RobotState(robot_id=rid, timestamp=utc_now())

    # ─── BaseRobot ──────────────────────────────────────────────────────

    @property
    def descriptor(self) -> RobotDescriptor:
        return self._descriptor

    def initial_state(self) -> RobotState:
        return RobotState(robot_id=self._descriptor.robot_id, timestamp=utc_now())

    def state(self) -> RobotState:
        return self._state

    # ─── Test helpers ───────────────────────────────────────────────────

    def set_state(self, state: RobotState) -> None:
        """Replace the current state (for tests and demos)."""
        self._state = state

    # ─── Internal ───────────────────────────────────────────────────────

    @staticmethod
    def _build_capabilities(
        capabilities: tuple[str, ...] | None,
    ) -> CapabilitySet:
        if capabilities is None:
            specs = _DEFAULT_CAPABILITIES
        else:
            specs = tuple((name, CapabilityKind.OTHER) for name in capabilities)
        caps = tuple(
            Capability(
                capability_id=CapabilityId(name),
                name=name.removeprefix("can_"),
                kind=kind,
            )
            for name, kind in specs
        )
        return CapabilitySet(capabilities=caps)


__all__ = ["FakeRobot"]
