"""Skills layer for Open Robot Brain.

A **skill** is an executable unit of behavior. Each skill:

- describes itself declaratively (:class:`orb_types.Skill`),
- validates its parameters and preconditions,
- produces a minimal effect on the world (v0.1),
- returns a :class:`orb_types.SkillResult`.

The :class:`InMemorySkillRegistry` maps ``SkillId`` to executable skills
and provides a uniform ``execute`` entry point used by the executor.

Design
------
- Skills are **pure with respect to the caller**: they receive the world
  state by argument, they do not read global state, and they return a
  result. This keeps them deterministic and testable.
- v0.1 skills do **not** talk to a simulator; they check the world and
  return success/failure. Real actuation is wired at the embodiment
  layer in a later iteration.
- Skills never raise for expected failures. They return
  ``SkillResult(status=FAILED, ...)``. They may raise for programming
  errors (unknown parameters, malformed values).

An LLM-driven or learned skill can be plugged in behind the same
:class:`BaseSkill` interface.
"""

from orb_brain.skills.base import BaseSkill
from orb_brain.skills.builtin import (
    GraspSkill,
    InspectSkill,
    LiftSkill,
    NavigateToSkill,
    PullSkill,
    PushSkill,
    ReachSkill,
    ReleaseSkill,
)
from orb_brain.skills.registry import InMemorySkillRegistry

__all__ = [
    "BaseSkill",
    "GraspSkill",
    "InMemorySkillRegistry",
    "InspectSkill",
    "LiftSkill",
    "NavigateToSkill",
    "PullSkill",
    "PushSkill",
    "ReachSkill",
    "ReleaseSkill",
]
