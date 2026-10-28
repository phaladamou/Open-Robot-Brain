"""Named robot bodies for cross-embodiment work.

"One brain. Many bodies" is only a slogan until the same brain drives
more than one body. These profiles are the bodies: capability sets for
:class:`~orb_embodiment.FakeRobot` that differ the way real robots
differ — not in code, but in what they can do.

- ``FULL_ARM_CAPABILITIES``: the reference body. Long arm, can reach,
  grasp, and lift.
- ``SHORT_ARM_CAPABILITIES``: same arm with short reach. It can still
  pick, but the planner must route it through extra base repositioning
  (no ``can_reach_far``).
- ``WEAK_ARM_CAPABILITIES``: gripper without lift. Pick goals are
  infeasible for this body (no ``can_lift``) and the reasoner must
  refuse them explicitly.

v0.1 bodies differ by capability set only; geometry arrives with
per-robot MuJoCo models in a later iteration.
"""

from __future__ import annotations

FULL_ARM_CAPABILITIES: tuple[str, ...] = (
    "can_navigate",
    "can_manipulate",
    "can_grasp",
    "can_lift",
    "can_see",
    "can_reach_far",
)
"""Capabilities of the reference full arm."""

SHORT_ARM_CAPABILITIES: tuple[str, ...] = tuple(
    c for c in FULL_ARM_CAPABILITIES if c != "can_reach_far"
)
"""Full arm minus long reach: pick needs extra repositioning."""

WEAK_ARM_CAPABILITIES: tuple[str, ...] = tuple(c for c in FULL_ARM_CAPABILITIES if c != "can_lift")
"""Full arm minus lift: pick goals are infeasible."""


__all__ = [
    "FULL_ARM_CAPABILITIES",
    "SHORT_ARM_CAPABILITIES",
    "WEAK_ARM_CAPABILITIES",
]
