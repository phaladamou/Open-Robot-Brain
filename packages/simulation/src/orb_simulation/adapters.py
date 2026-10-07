"""MuJoCo adapter (optional, stub).

This module only loads MuJoCo if the ``mujoco`` extra is installed.
Without it, :class:`MujocoAdapter` raises an informative error on
construction, and the rest of ORB keeps working with
:class:`~orb_simulation.MockSimulator`.

Usage::

    uv sync --extra mujoco
"""

from __future__ import annotations

from orb_types import RobotId, RobotState, utc_now


class MujocoAdapter:
    """A MuJoCo-backed simulator (stub).

    Parameters
    ----------
    model_path:
        Path to a MuJoCo MJCF file.
    robot_id:
        Identifier for the simulated robot.

    Raises
    ------
    ImportError
        If MuJoCo is not installed.
    """

    def __init__(
        self,
        model_path: str,
        *,
        robot_id: RobotId | None = None,
    ) -> None:
        try:
            import mujoco  # noqa: F401
        except ImportError as exc:  # pragma: no cover
            msg = (
                "MuJoCo is not installed. Install the optional extra with `uv sync --extra mujoco`."
            )
            raise ImportError(msg) from exc

        self._model_path = model_path
        self._robot_id = RobotId(robot_id) if robot_id is not None else RobotId("mujoco")
        # Real MuJoCo wiring happens in a later iteration. This class is
        # a placeholder that documents the interface.
        msg = (
            "MujocoAdapter is a stub in v0.1. Real MuJoCo integration "
            "lands in v0.2 — MockSimulator is used until then."
        )
        raise NotImplementedError(msg)

    def reset(self) -> None:  # pragma: no cover
        raise NotImplementedError

    def step(self, dt: float) -> None:  # pragma: no cover
        raise NotImplementedError

    def state(self) -> RobotState:  # pragma: no cover
        return RobotState(robot_id=self._robot_id, timestamp=utc_now())

    def set_joint_targets(self, targets: dict[str, float]) -> None:  # pragma: no cover
        raise NotImplementedError


__all__ = ["MujocoAdapter"]
