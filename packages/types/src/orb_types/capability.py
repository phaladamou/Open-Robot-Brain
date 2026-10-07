"""Capability types for Open Robot Brain.

A **capability** is a *verb the body can perform* — a first-class,
body-agnostic description of what a robot can do. The brain reasons over
capabilities, never over motors, servos, or joints.

Design
------
- A capability has a coarse ``kind`` (manipulation, navigation, …) and a
  fine-grained ``name`` (``grasp``, ``lift``, ``navigate_to``, …).
- It carries optional ``limits`` (payload, reach, speed) as a free-form
  mapping — extensible without new types.
- ``CapabilitySet`` is the per-embodiment view: what this body can do.
- Capabilities are declared by the embodiment layer, consumed by the brain.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Any

from pydantic import Field

from orb_types.base import ORBModel
from orb_types.ids import CapabilityId

# ─── Enums ───────────────────────────────────────────────────────────────


class CapabilityKind(StrEnum):
    """Coarse category of a capability."""

    LOCOMOTION = "locomotion"  # walk, drive, balance
    NAVIGATION = "navigation"  # go to a location, path planning
    MANIPULATION = "manipulation"  # grasp, lift, place, open, close
    PERCEPTION = "perception"  # see, detect, measure
    COMMUNICATION = "communication"  # speak, signal, display
    OTHER = "other"


# ─── Capability ──────────────────────────────────────────────────────────


class Capability(ORBModel):
    """A body-agnostic description of something a robot can do.

    Fields
    ------
    capability_id:
        Stable identifier (e.g. ``can_grasp``).
    name:
        Short verb-like name (e.g. ``"grasp"``).
    kind:
        Coarse category (see :class:`CapabilityKind`).
    description:
        Human-readable description of what this capability enables.
    limits:
        Optional free-form limits (e.g. ``{"max_payload_kg": 2.0}``).
    """

    capability_id: CapabilityId
    name: Annotated[str, Field(min_length=1)]
    kind: CapabilityKind = CapabilityKind.OTHER
    description: str = ""
    limits: dict[str, Any] = Field(default_factory=dict)


# ─── CapabilitySet ───────────────────────────────────────────────────────


class CapabilitySet(ORBModel):
    """Immutable set of capabilities exposed by one embodiment.

    Provides fast lookups by ID or name. The brain uses this to decide
    whether a plan is feasible *before* dispatching it to the body.
    """

    capabilities: tuple[Capability, ...] = ()

    # ─── Lookups ─────────────────────────────────────────────────────────

    def has(self, capability_id: CapabilityId | str) -> bool:
        """Return whether the set contains the given capability ID."""
        return any(c.capability_id == capability_id for c in self.capabilities)

    def get(self, capability_id: CapabilityId | str) -> Capability | None:
        """Return the capability with the given ID, or ``None``."""
        for c in self.capabilities:
            if c.capability_id == capability_id:
                return c
        return None

    def by_name(self, name: str) -> Capability | None:
        """Return the first capability with the given name, or ``None``."""
        for c in self.capabilities:
            if c.name == name:
                return c
        return None

    def by_kind(self, kind: CapabilityKind) -> tuple[Capability, ...]:
        """Return all capabilities of the given kind."""
        return tuple(c for c in self.capabilities if c.kind == kind)

    def ids(self) -> tuple[CapabilityId, ...]:
        """Return the tuple of capability IDs."""
        return tuple(c.capability_id for c in self.capabilities)

    def names(self) -> tuple[str, ...]:
        """Return the tuple of capability names."""
        return tuple(c.name for c in self.capabilities)


__all__ = [
    "Capability",
    "CapabilityKind",
    "CapabilitySet",
]
