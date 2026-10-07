"""Tests for orb_simulation.mock."""

from __future__ import annotations

import pytest
from orb_interfaces import Simulator
from orb_simulation import MockSimulator

# ─── Construction ────────────────────────────────────────────────────────


def test_default_joints() -> None:
    sim = MockSimulator()
    assert len(sim.joint_names) == 6


def test_custom_joints() -> None:
    sim = MockSimulator(joints=("a", "b"))
    assert sim.joint_names == ("a", "b")


def test_robot_id_default() -> None:
    sim = MockSimulator()
    assert sim.robot_id == "mock"


def test_robot_id_custom() -> None:
    sim = MockSimulator(robot_id="r2d2")  # type: ignore[arg-type]
    assert sim.robot_id == "r2d2"


def test_invalid_target_speed_rejected() -> None:
    with pytest.raises(ValueError, match="target_speed"):
        MockSimulator(target_speed=0.0)


# ─── Initial state ───────────────────────────────────────────────────────


def test_initial_state_all_zero() -> None:
    sim = MockSimulator(joints=("j1", "j2"))
    s = sim.state()
    assert len(s.joints) == 2
    assert all(j.position == 0.0 for j in s.joints)
    assert all(j.velocity == 0.0 for j in s.joints)


def test_state_has_robot_id() -> None:
    sim = MockSimulator(robot_id="r2d2")  # type: ignore[arg-type]
    assert sim.state().robot_id == "r2d2"


# ─── Commands & stepping ─────────────────────────────────────────────────


def test_set_target_then_step_moves_joint() -> None:
    sim = MockSimulator(joints=("j1",), target_speed=1.0)
    sim.set_joint_targets({"j1": 1.0})
    sim.step(0.5)
    joint = sim.state().get_joint("j1")
    assert joint is not None
    assert joint.position == pytest.approx(0.5)


def test_unknown_joint_target_ignored() -> None:
    sim = MockSimulator(joints=("j1",))
    sim.set_joint_targets({"j_unknown": 1.0})
    sim.step(1.0)
    assert sim.state().get_joint("j1").position == 0.0  # type: ignore[union-attr]


def test_joint_reaches_target_after_enough_steps() -> None:
    sim = MockSimulator(joints=("j1",), target_speed=1.0)
    sim.set_joint_targets({"j1": 1.0})
    for _ in range(10):
        sim.step(0.2)
    joint = sim.state().get_joint("j1")
    assert joint is not None
    assert joint.position == pytest.approx(1.0)


def test_negative_target() -> None:
    sim = MockSimulator(joints=("j1",), target_speed=1.0)
    sim.set_joint_targets({"j1": -1.0})
    sim.step(0.5)
    joint = sim.state().get_joint("j1")
    assert joint is not None
    assert joint.position == pytest.approx(-0.5)


def test_velocity_reported() -> None:
    sim = MockSimulator(joints=("j1",), target_speed=1.0)
    sim.set_joint_targets({"j1": 1.0})
    sim.step(0.5)
    joint = sim.state().get_joint("j1")
    assert joint is not None
    assert joint.velocity == pytest.approx(1.0)


def test_invalid_dt_rejected() -> None:
    sim = MockSimulator()
    with pytest.raises(ValueError, match="dt"):
        sim.step(0.0)
    with pytest.raises(ValueError, match="dt"):
        sim.step(-1.0)


# ─── Reset ───────────────────────────────────────────────────────────────


def test_reset_clears_state() -> None:
    sim = MockSimulator(joints=("j1",))
    sim.set_joint_targets({"j1": 1.0})
    sim.step(0.5)
    sim.reset()
    joint = sim.state().get_joint("j1")
    assert joint is not None
    assert joint.position == 0.0
    assert joint.velocity == 0.0


def test_reset_clears_targets() -> None:
    sim = MockSimulator(joints=("j1",))
    sim.set_joint_targets({"j1": 1.0})
    sim.reset()
    sim.step(1.0)
    assert sim.state().get_joint("j1").position == 0.0  # type: ignore[union-attr]


# ─── Protocol compliance ─────────────────────────────────────────────────


def test_mock_simulator_is_simulator() -> None:
    sim = MockSimulator()
    assert isinstance(sim, Simulator)


# ─── MuJoCo adapter (stub) ──────────────────────────────────────────────


def test_mujoco_adapter_raises_without_mujoco() -> None:
    from orb_simulation.adapters import MujocoAdapter

    with pytest.raises((ImportError, NotImplementedError)):
        MujocoAdapter("some/path.xml")
