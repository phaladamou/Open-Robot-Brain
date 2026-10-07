"""MockSimulator — pure-Python simulator with no external dependencies.

The mock simulator does **not** model dynamics. It:

- holds a set of named joints with positions and velocities,
- interpolates linearly toward commanded targets on each ``step``,
- reports the current robot state.

This is enough to exercise the full cognitive pipeline (parse → reason →
plan → execute → step) without MuJoCo. It is deterministic and fast,
which makes it ideal for CI and for benchmarking the brain itself.
"""

from __future__ import annotations

from orb_types import (
    JointState,
    RobotId,
    RobotState,
    utc_now,
)


class MockSimulator:
    """A pure-Python simulator.

    Parameters
    ----------
    robot_id:
        Identifier for the simulated robot.
    joints:
        Initial joint names. Defaults to a 6-DOF arm.
    target_speed:
        Maximum joint velocity when interpolating toward targets, in
        radians (or meters) per second. Must be strictly positive.

    Example
    -------
    >>> sim = MockSimulator(joints=("j1", "j2"))
    >>> sim.set_joint_targets({"j1": 1.0})
    >>> sim.step(0.5)
    >>> round(sim.state().get_joint("j1").position, 2)  # type: ignore[union-attr]
    0.5
    """

    DEFAULT_JOINTS: tuple[str, ...] = ("j1", "j2", "j3", "j4", "j5", "j6")

    def __init__(
        self,
        *,
        robot_id: RobotId | None = None,
        joints: tuple[str, ...] | None = None,
        target_speed: float = 1.0,
    ) -> None:
        if target_speed <= 0.0:
            msg = f"target_speed must be > 0, got {target_speed!r}"
            raise ValueError(msg)
        self._robot_id = RobotId(robot_id) if robot_id is not None else RobotId("mock")
        self._joint_names = joints if joints is not None else self.DEFAULT_JOINTS
        self._speed = float(target_speed)

        # Internal state: position + velocity per joint
        self._positions: dict[str, float] = dict.fromkeys(self._joint_names, 0.0)
        self._velocities: dict[str, float] = dict.fromkeys(self._joint_names, 0.0)
        self._targets: dict[str, float] = {}

    # ─── Lifecycle ──────────────────────────────────────────────────────

    def reset(self) -> None:
        """Reset to initial state (all joints at 0, no targets)."""
        self._positions = dict.fromkeys(self._joint_names, 0.0)
        self._velocities = dict.fromkeys(self._joint_names, 0.0)
        self._targets = {}

    def step(self, dt: float) -> None:
        """Advance the simulation by ``dt`` seconds.

        For each joint with a target, move the position toward the target
        at ``target_speed``. Velocity is reported as the effective change
        per second.
        """
        if dt <= 0.0:
            msg = f"dt must be > 0, got {dt!r}"
            raise ValueError(msg)

        max_delta = self._speed * dt
        for name, target in self._targets.items():
            current = self._positions.get(name)
            if current is None:
                continue
            delta = target - current
            if abs(delta) <= max_delta:
                new_pos = target
            else:
                new_pos = current + max_delta * (1.0 if delta > 0 else -1.0)
            self._velocities[name] = (new_pos - current) / dt
            self._positions[name] = new_pos

    # ─── Commands ───────────────────────────────────────────────────────

    def set_joint_targets(self, targets: dict[str, float]) -> None:
        """Set position targets for the given joints.

        Unknown joint names are silently ignored (v0.1).
        """
        for name, value in targets.items():
            if name in self._positions:
                self._targets[name] = float(value)

    # ─── State ──────────────────────────────────────────────────────────

    def state(self) -> RobotState:
        """Return the current robot state."""
        joints = tuple(
            JointState(
                name=name,
                position=self._positions[name],
                velocity=self._velocities[name],
            )
            for name in self._joint_names
        )
        return RobotState(
            robot_id=self._robot_id,
            timestamp=utc_now(),
            joints=joints,
        )

    # ─── Introspection ──────────────────────────────────────────────────

    @property
    def joint_names(self) -> tuple[str, ...]:
        """The joint names exposed by this simulator."""
        return self._joint_names

    @property
    def robot_id(self) -> RobotId:
        """The robot identifier."""
        return self._robot_id


__all__ = ["MockSimulator"]
