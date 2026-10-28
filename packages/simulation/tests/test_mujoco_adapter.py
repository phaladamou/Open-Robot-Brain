"""Tests for orb_simulation.adapters (requires the mujoco extra)."""

from __future__ import annotations

from pathlib import Path

import pytest
from orb_interfaces import Simulator
from orb_simulation.adapters import MujocoAdapter
from orb_types import ConfigurationError

mujoco = pytest.importorskip("mujoco")

MODEL_PATH = Path(__file__).resolve().parents[1] / "robots" / "arm_6dof.xml"


def _write_model(tmp_path: Path, xml: str) -> Path:
    path = tmp_path / "model.xml"
    path.write_text(xml)
    return path


# ─── Construction & protocol ─────────────────────────────────────────────


def test_adapter_is_simulator() -> None:
    sim = MujocoAdapter(MODEL_PATH)
    assert isinstance(sim, Simulator)


def test_default_robot_id() -> None:
    sim = MujocoAdapter(MODEL_PATH)
    assert sim.robot_id == "mujoco"


def test_custom_robot_id() -> None:
    sim = MujocoAdapter(MODEL_PATH, robot_id="arm1")  # type: ignore[arg-type]
    assert sim.robot_id == "arm1"


# ─── State ───────────────────────────────────────────────────────────────


def test_state_reports_six_named_joints_in_order() -> None:
    sim = MujocoAdapter(MODEL_PATH)
    state = sim.state()
    assert sim.joint_names == ("j1", "j2", "j3", "j4", "j5", "j6")
    assert state.joint_names() == ("j1", "j2", "j3", "j4", "j5", "j6")
    assert state.robot_id == "mujoco"


def test_initial_state_all_zero() -> None:
    sim = MujocoAdapter(MODEL_PATH)
    state = sim.state()
    assert all(j.position == 0.0 for j in state.joints)
    assert all(j.velocity == 0.0 for j in state.joints)


# ─── Commands & stepping ─────────────────────────────────────────────────


def test_set_target_then_step_converges() -> None:
    sim = MujocoAdapter(MODEL_PATH)
    sim.set_joint_targets({"j1": 0.5})
    sim.step(2.0)
    joint = sim.state().get_joint("j1")
    assert joint is not None
    assert abs(joint.position - 0.5) < 0.05


def test_unknown_joint_targets_ignored() -> None:
    sim = MujocoAdapter(MODEL_PATH)
    sim.set_joint_targets({"nope": 1.0})
    sim.step(0.1)
    assert all(j.position == 0.0 for j in sim.state().joints)


def test_step_rejects_non_positive_dt() -> None:
    sim = MujocoAdapter(MODEL_PATH)
    with pytest.raises(ValueError, match="dt"):
        sim.step(0.0)
    with pytest.raises(ValueError, match="dt"):
        sim.step(-0.1)


def test_reset_zeroes_positions_velocities_and_commands() -> None:
    sim = MujocoAdapter(MODEL_PATH)
    sim.set_joint_targets({"j1": 0.5})
    sim.step(0.5)
    sim.reset()
    state = sim.state()
    assert all(j.position == 0.0 for j in state.joints)
    assert all(j.velocity == 0.0 for j in state.joints)
    # Commands are cleared too: stepping after reset holds zero.
    sim.step(0.5)
    assert all(j.position == 0.0 for j in sim.state().joints)


def test_stepping_is_deterministic() -> None:
    first = MujocoAdapter(MODEL_PATH)
    first.set_joint_targets({"j1": 0.5, "j3": -0.25})
    first.step(1.0)
    second = MujocoAdapter(MODEL_PATH)
    second.set_joint_targets({"j1": 0.5, "j3": -0.25})
    second.step(1.0)
    first_pos = [j.position for j in first.state().joints]
    second_pos = [j.position for j in second.state().joints]
    assert first_pos == second_pos


# ─── Model validation ────────────────────────────────────────────────────


def test_invalid_xml_raises_configuration_error(tmp_path: Path) -> None:
    path = _write_model(tmp_path, "<mujoco><worldbody><body></mujoco>")
    with pytest.raises(ConfigurationError, match="Could not parse"):
        MujocoAdapter(path)


def test_non_1dof_joint_rejected(tmp_path: Path) -> None:
    path = _write_model(
        tmp_path,
        """<mujoco>
  <worldbody>
    <body>
      <joint name="ball" type="ball"/>
      <geom type="sphere" size="0.05"/>
    </body>
  </worldbody>
</mujoco>
""",
    )
    with pytest.raises(ConfigurationError, match="not 1-DoF"):
        MujocoAdapter(path)


def test_joint_without_actuator_rejected(tmp_path: Path) -> None:
    path = _write_model(
        tmp_path,
        """<mujoco>
  <worldbody>
    <body>
      <joint name="j" type="hinge" axis="0 0 1"/>
      <geom type="sphere" size="0.05"/>
    </body>
  </worldbody>
</mujoco>
""",
    )
    with pytest.raises(ConfigurationError, match="no matching actuator"):
        MujocoAdapter(path)
