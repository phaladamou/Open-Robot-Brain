"""Capability provider protocol.

A capability provider exposes what the current embodiment can do.
The brain consumes it to decide whether a goal is feasible *before*
attempting to plan for it.

Implementations live in ``embodiment/abstraction/``.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from orb_types import CapabilitySet


@runtime_checkable
class CapabilityProvider(Protocol):
    """Protocol for anything that exposes a :class:`CapabilitySet`."""

    def capabilities(self) -> CapabilitySet:
        """Return the current set of capabilities."""
        ...


__all__ = ["CapabilityProvider"]
