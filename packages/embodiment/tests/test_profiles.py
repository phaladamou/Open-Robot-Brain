"""Tests for orb_embodiment.adapters.profiles."""

from __future__ import annotations

from orb_embodiment import (
    FULL_ARM_CAPABILITIES,
    SHORT_ARM_CAPABILITIES,
    WEAK_ARM_CAPABILITIES,
    FakeRobot,
)


def test_full_arm_has_all_manipulation_capabilities() -> None:
    for name in ("can_grasp", "can_lift", "can_reach_far"):
        assert name in FULL_ARM_CAPABILITIES


def test_short_arm_lacks_only_long_reach() -> None:
    assert "can_reach_far" not in SHORT_ARM_CAPABILITIES
    assert "can_grasp" in SHORT_ARM_CAPABILITIES
    assert "can_lift" in SHORT_ARM_CAPABILITIES
    assert set(SHORT_ARM_CAPABILITIES) == set(FULL_ARM_CAPABILITIES) - {"can_reach_far"}


def test_weak_arm_lacks_only_lift() -> None:
    assert "can_lift" not in WEAK_ARM_CAPABILITIES
    assert "can_grasp" in WEAK_ARM_CAPABILITIES
    assert set(WEAK_ARM_CAPABILITIES) == set(FULL_ARM_CAPABILITIES) - {"can_lift"}


def test_fake_robot_exposes_profile_capabilities() -> None:
    short = FakeRobot(capabilities=SHORT_ARM_CAPABILITIES)
    assert not short.capabilities().has("can_reach_far")
    assert short.capabilities().has("can_lift")
    weak = FakeRobot(capabilities=WEAK_ARM_CAPABILITIES)
    assert not weak.capabilities().has("can_lift")
    assert weak.capabilities().has("can_grasp")
