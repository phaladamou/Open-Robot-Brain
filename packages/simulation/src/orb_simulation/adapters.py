"""MuJoCo-backed simulator (real dynamics).

:class:`MujocoAdapter` exists because the mock simulator cannot answer
questions about contact, inertia, or servo tracking: it interpolates
kinematically toward targets. When an experiment needs real physics —
controller validation, failure-mode analysis, sim-to-real preparation —
this adapter steps a MuJoCo model and reports its true generalized
positions and velocities.

MuJoCo stays an **optional** dependency: it is imported lazily so the
rest of ORB (and CI without the extra) keeps working with
:class:`~orb_simulation.MockSimulator`.

Usage::

    uv sync --extra mujoco
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

from orb_types import (
    ConfigurationError,
    JointState,
    NotFoundError,
    RobotId,
    RobotState,
    utc_now,
)

if TYPE_CHECKING:  # pragma: no cover
    from mujoco import MjData, MjModel


class _JointAddrs(NamedTuple):
    """MuJoCo addresses of one 1-DoF joint."""

    qpos_adr: int
    dof_adr: int
    actuator_id: int


class MujocoAdapter:
    """A MuJoCo-backed simulator.

    The adapter owns a ``MjModel``/``MjData`` pair loaded from an MJCF
    file. Joint targets are written to the model's position actuators
    (``data.ctrl``) and realized by stepping the simulation; state is
    read back from generalized coordinates.

    Parameters
    ----------
    model_path:
        Path to a MuJoCo MJCF file. Every joint must be 1-DoF
        (hinge or slide) with a matching position actuator of the
        same name.
    robot_id:
        Identifier for the simulated robot.

    Raises
    ------
    NotFoundError
        If ``model_path`` does not point to a file.
    ImportError
        If MuJoCo is not installed.
    ConfigurationError
        If the MJCF cannot be parsed, a joint is unnamed, a joint is
        not 1-DoF, or a joint has no matching actuator.

    Example
    -------
    >>> sim = MujocoAdapter("packages/simulation/robots/arm_6dof.xml")
    >>> sim.set_joint_targets({"j1": 0.5})
    >>> sim.step(0.1)
    >>> sim.state().get_joint("j1").position > 0.0  # type: ignore[union-attr]
    True
    """

    def __init__(
        self,
        model_path: str | os.PathLike[str],
        *,
        robot_id: RobotId | None = None,
    ) -> None:
        path = Path(model_path)
        if not path.is_file():
            raise NotFoundError(
                f"MuJoCo model file not found: {path}",
                model_path=str(path),
            )

        try:
            import mujoco
        except ImportError as exc:
            msg = (
                "MuJoCo is not installed. Install the optional extra with `uv sync --extra mujoco`."
            )
            raise ImportError(msg) from exc

        try:
            model = mujoco.MjModel.from_xml_path(str(path))
        except ValueError as exc:
            raise ConfigurationError(
                f"Could not parse MuJoCo model: {path}",
                model_path=str(path),
            ) from exc

        self._mujoco = mujoco
        self._model: MjModel = model
        self._data: MjData = mujoco.MjData(model)
        self._model_path = path
        self._robot_id = RobotId(robot_id) if robot_id is not None else RobotId("mujoco")
        self._joints = self._index_joints()

    # ─── Introspection ──────────────────────────────────────────────────

    def _index_joints(self) -> dict[str, _JointAddrs]:
        """Map each joint name to its MuJoCo addresses.

        Raises
        ------
        ConfigurationError
            If a joint is unnamed, not 1-DoF, or lacks an actuator.
        """
        mujoco = self._mujoco
        joints: dict[str, _JointAddrs] = {}
        for joint_id in range(self._model.njnt):
            name = mujoco.mj_id2name(self._model, mujoco.mjtObj.mjOBJ_JOINT, joint_id)
            if name is None:
                raise ConfigurationError(
                    f"Joint {joint_id} has no name; named joints are required",
                    model_path=str(self._model_path),
                    joint_id=joint_id,
                )
            joint_type = int(self._model.jnt_type[joint_id])
            one_dof = (mujoco.mjtJoint.mjJNT_HINGE, mujoco.mjtJoint.mjJNT_SLIDE)
            if joint_type not in one_dof:
                raise ConfigurationError(
                    f"Joint {name!r} is not 1-DoF; only hinge/slide joints are supported",
                    model_path=str(self._model_path),
                    joint=name,
                )
            view = self._model.joint(name)
            actuator_id = mujoco.mj_name2id(self._model, mujoco.mjtObj.mjOBJ_ACTUATOR, name)
            if actuator_id < 0:
                raise ConfigurationError(
                    f"Joint {name!r} has no matching actuator; each joint needs one",
                    model_path=str(self._model_path),
                    joint=name,
                )
            joints[name] = _JointAddrs(
                qpos_adr=int(view.qposadr[0]),
                dof_adr=int(view.dofadr[0]),
                actuator_id=int(actuator_id),
            )
        return joints

    # ─── Lifecycle ──────────────────────────────────────────────────────

    def reset(self) -> None:
        """Reset to initial state (zero positions, velocities, commands)."""
        self._mujoco.mj_resetData(self._model, self._data)
        self._data.ctrl[:] = 0.0

    def step(self, dt: float) -> None:
        """Advance the simulation by ``dt`` seconds.

        ``dt`` is quantized to a whole number of model timesteps
        (at least one step is always taken).
        """
        if dt <= 0.0:
            msg = f"dt must be > 0, got {dt!r}"
            raise ValueError(msg)

        timestep = float(self._model.opt.timestep)
        n_steps = max(1, round(dt / timestep))
        for _ in range(n_steps):
            self._mujoco.mj_step(self._model, self._data)

    # ─── Commands ───────────────────────────────────────────────────────

    def set_joint_targets(self, targets: dict[str, float]) -> None:
        """Set position targets for the given joints.

        Unknown joint names are silently ignored (v0.1).
        """
        for name, value in targets.items():
            addrs = self._joints.get(name)
            if addrs is not None:
                self._data.ctrl[addrs.actuator_id] = float(value)

    # ─── State ──────────────────────────────────────────────────────────

    def state(self) -> RobotState:
        """Return the current robot state."""
        qpos = self._data.qpos
        qvel = self._data.qvel
        effort = self._data.qfrc_actuator
        joints = tuple(
            JointState(
                name=name,
                position=float(qpos[addrs.qpos_adr]),
                velocity=float(qvel[addrs.dof_adr]),
                effort=float(effort[addrs.dof_adr]),
            )
            for name, addrs in self._joints.items()
        )
        return RobotState(
            robot_id=self._robot_id,
            timestamp=utc_now(),
            joints=joints,
        )

    # ─── Introspection ──────────────────────────────────────────────────

    @property
    def joint_names(self) -> tuple[str, ...]:
        """The joint names exposed by this simulator, in model order."""
        return tuple(self._joints)

    @property
    def robot_id(self) -> RobotId:
        """The robot identifier."""
        return self._robot_id


__all__ = ["MujocoAdapter"]
