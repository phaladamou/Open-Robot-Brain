"""Tests for orb_types.capability."""

from __future__ import annotations

import pytest
from orb_types.capability import Capability, CapabilityKind, CapabilitySet
from orb_types.ids import CapabilityId
from pydantic import ValidationError as PydanticValidationError

# ─── Capability ──────────────────────────────────────────────────────────


def test_capability_minimal() -> None:
    c = Capability(capability_id=CapabilityId("can_grasp"), name="grasp")
    assert c.name == "grasp"
    assert c.kind == CapabilityKind.OTHER
    assert c.limits == {}


def test_capability_manipulation_with_limits() -> None:
    c = Capability(
        capability_id=CapabilityId("can_lift"),
        name="lift",
        kind=CapabilityKind.MANIPULATION,
        description="Lift an object held in the gripper.",
        limits={"max_payload_kg": 2.0},
    )
    assert c.kind == CapabilityKind.MANIPULATION
    assert c.limits["max_payload_kg"] == 2.0


def test_capability_rejects_empty_name() -> None:
    with pytest.raises(PydanticValidationError):
        Capability(capability_id=CapabilityId("can_x"), name="")


def test_capability_frozen() -> None:
    c = Capability(capability_id=CapabilityId("can_grasp"), name="grasp")
    with pytest.raises(PydanticValidationError):
        c.name = "other"  # type: ignore[misc]


# ─── CapabilitySet ───────────────────────────────────────────────────────


def _arm_set() -> CapabilitySet:
    return CapabilitySet(
        capabilities=(
            Capability(
                capability_id=CapabilityId("can_grasp"),
                name="grasp",
                kind=CapabilityKind.MANIPULATION,
            ),
            Capability(
                capability_id=CapabilityId("can_navigate"),
                name="navigate_to",
                kind=CapabilityKind.NAVIGATION,
            ),
            Capability(
                capability_id=CapabilityId("can_see"),
                name="see",
                kind=CapabilityKind.PERCEPTION,
            ),
        )
    )


def test_capability_set_empty() -> None:
    cs = CapabilitySet()
    assert cs.capabilities == ()
    assert cs.ids() == ()
    assert not cs.has(CapabilityId("can_grasp"))


def test_capability_set_has() -> None:
    cs = _arm_set()
    assert cs.has(CapabilityId("can_grasp"))
    assert cs.has("can_grasp")
    assert not cs.has(CapabilityId("can_fly"))


def test_capability_set_get() -> None:
    cs = _arm_set()
    c = cs.get(CapabilityId("can_grasp"))
    assert c is not None
    assert c.name == "grasp"
    assert cs.get(CapabilityId("can_fly")) is None


def test_capability_set_by_name() -> None:
    cs = _arm_set()
    c = cs.by_name("navigate_to")
    assert c is not None
    assert c.kind == CapabilityKind.NAVIGATION
    assert cs.by_name("missing") is None


def test_capability_set_by_kind() -> None:
    cs = _arm_set()
    manip = cs.by_kind(CapabilityKind.MANIPULATION)
    assert len(manip) == 1
    assert manip[0].name == "grasp"


def test_capability_set_ids_and_names() -> None:
    cs = _arm_set()
    assert "can_grasp" in cs.ids()
    assert "grasp" in cs.names()
