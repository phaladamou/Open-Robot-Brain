"""Built-in skills for Open Robot Brain (v0.1).

Each skill is deliberately simple: it validates its arguments against the
current world and returns success or failure. No simulator is involved.
This makes the skills deterministic, fast, and easy to test, and lets the
rest of the pipeline (executor, event bus, world model) be exercised
without MuJoCo.

The skills are:

- ``navigate_to`` — go to a location or near an object
- ``reach``       — extend the arm toward an object
- ``grasp``       — close the gripper on an object
- ``lift``        — lift the object
- ``release``     — open the gripper
- ``pull``        — pull an object (used to open)
- ``push``        — push an object (used to close)
- ``inspect``     — look at an object or area
"""

from __future__ import annotations

from typing import Any

from orb_types import (
    CapabilityId,
    ObjectId,
    Predicate,
    Skill,
    SkillId,
    SkillResult,
    SkillSpec,
    WorldState,
)

from orb_brain.skills.base import BaseSkill

# ─── Shared helpers ──────────────────────────────────────────────────────


def _require_param(parameters: dict[str, Any], name: str) -> str | None:
    value = parameters.get(name)
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        return None
    return value


# ─── navigate_to ─────────────────────────────────────────────────────────


class NavigateToSkill(BaseSkill):
    """Navigate to a location or near an object."""

    _skill = Skill(
        skill_id=SkillId("navigate_to"),
        name="navigate_to",
        description="Move the base so that the target becomes reachable.",
        spec=SkillSpec(
            parameters={
                "location": {"type": "string"},
                "object_id": {"type": "string"},
            },
            required_capabilities=(CapabilityId("can_navigate"),),
            preconditions=(Predicate(name="reachable"),),
        ),
    )

    def run(self, parameters: dict[str, Any], world: WorldState) -> SkillResult:
        location = _require_param(parameters, "location")
        object_id = _require_param(parameters, "object_id")

        if location is None and object_id is None:
            return self._failure(message="navigate_to requires 'location' or 'object_id'")

        if location is not None and world.get_location(location) is None:
            # Locations are optional in v0.1 worlds; treat as soft success.
            return self._success(
                message=f"navigated to {location!r} (location not tracked in world)",
                payload={"location": location},
            )

        if object_id is not None:
            if world.get_object(ObjectId(object_id)) is None:
                return self._failure(message=f"object {object_id!r} not in world")
            return self._success(
                message=f"navigated near {object_id!r}",
                payload={"object_id": object_id},
            )

        return self._success(payload={"location": location})


# ─── reach ───────────────────────────────────────────────────────────────


class ReachSkill(BaseSkill):
    """Extend the arm toward an object."""

    _skill = Skill(
        skill_id=SkillId("reach"),
        name="reach",
        description="Extend the arm toward the target object.",
        spec=SkillSpec(
            parameters={"object_id": {"type": "string"}},
            required=("object_id",),
            required_capabilities=(CapabilityId("can_manipulate"),),
            preconditions=(Predicate(name="reachable"),),
        ),
    )

    def run(self, parameters: dict[str, Any], world: WorldState) -> SkillResult:
        object_id = _require_param(parameters, "object_id")
        if object_id is None:
            return self._failure(message="reach requires 'object_id'")
        if world.get_object(ObjectId(object_id)) is None:
            return self._failure(message=f"object {object_id!r} not in world")
        return self._success(payload={"object_id": object_id})


# ─── grasp ───────────────────────────────────────────────────────────────


class GraspSkill(BaseSkill):
    """Close the gripper on an object."""

    _skill = Skill(
        skill_id=SkillId("grasp"),
        name="grasp",
        description="Close the gripper around the target object.",
        spec=SkillSpec(
            parameters={"object_id": {"type": "string"}},
            required=("object_id",),
            required_capabilities=(CapabilityId("can_grasp"),),
            postconditions=(Predicate(name="holding"),),
        ),
    )

    def run(self, parameters: dict[str, Any], world: WorldState) -> SkillResult:
        object_id = _require_param(parameters, "object_id")
        if object_id is None:
            return self._failure(message="grasp requires 'object_id'")
        if world.get_object(ObjectId(object_id)) is None:
            return self._failure(message=f"object {object_id!r} not in world")
        return self._success(payload={"object_id": object_id, "held": True})


# ─── lift ────────────────────────────────────────────────────────────────


class LiftSkill(BaseSkill):
    """Lift a held object."""

    _skill = Skill(
        skill_id=SkillId("lift"),
        name="lift",
        description="Lift the object currently held by the gripper.",
        spec=SkillSpec(
            parameters={"object_id": {"type": "string"}},
            required=("object_id",),
            required_capabilities=(CapabilityId("can_lift"),),
            preconditions=(Predicate(name="holding"),),
        ),
    )

    def run(self, parameters: dict[str, Any], world: WorldState) -> SkillResult:
        object_id = _require_param(parameters, "object_id")
        if object_id is None:
            return self._failure(message="lift requires 'object_id'")
        if world.get_object(ObjectId(object_id)) is None:
            return self._failure(message=f"object {object_id!r} not in world")
        return self._success(payload={"object_id": object_id, "lifted": True})


# ─── release ─────────────────────────────────────────────────────────────


class ReleaseSkill(BaseSkill):
    """Open the gripper and let go of the held object."""

    _skill = Skill(
        skill_id=SkillId("release"),
        name="release",
        description="Open the gripper to release the held object.",
        spec=SkillSpec(
            parameters={"object_id": {"type": "string"}},
            required=("object_id",),
            required_capabilities=(CapabilityId("can_grasp"),),
            postconditions=(Predicate(name="released"),),
        ),
    )

    def run(self, parameters: dict[str, Any], world: WorldState) -> SkillResult:
        object_id = _require_param(parameters, "object_id")
        if object_id is None:
            return self._failure(message="release requires 'object_id'")
        # Release does not require the object to be present in the world
        # (it may already have been removed). Success is unconditional.
        return self._success(payload={"object_id": object_id, "released": True})


# ─── pull / push ─────────────────────────────────────────────────────────


class PullSkill(BaseSkill):
    """Pull an object (used for opening drawers)."""

    _skill = Skill(
        skill_id=SkillId("pull"),
        name="pull",
        description="Pull the target object along its local axis.",
        spec=SkillSpec(
            parameters={"object_id": {"type": "string"}},
            required=("object_id",),
            required_capabilities=(CapabilityId("can_manipulate"),),
        ),
    )

    def run(self, parameters: dict[str, Any], world: WorldState) -> SkillResult:
        object_id = _require_param(parameters, "object_id")
        if object_id is None:
            return self._failure(message="pull requires 'object_id'")
        if world.get_object(ObjectId(object_id)) is None:
            return self._failure(message=f"object {object_id!r} not in world")
        return self._success(payload={"object_id": object_id, "pulled": True})


class PushSkill(BaseSkill):
    """Push an object (used for closing drawers)."""

    _skill = Skill(
        skill_id=SkillId("push"),
        name="push",
        description="Push the target object along its local axis.",
        spec=SkillSpec(
            parameters={"object_id": {"type": "string"}},
            required=("object_id",),
            required_capabilities=(CapabilityId("can_manipulate"),),
        ),
    )

    def run(self, parameters: dict[str, Any], world: WorldState) -> SkillResult:
        object_id = _require_param(parameters, "object_id")
        if object_id is None:
            return self._failure(message="push requires 'object_id'")
        if world.get_object(ObjectId(object_id)) is None:
            return self._failure(message=f"object {object_id!r} not in world")
        return self._success(payload={"object_id": object_id, "pushed": True})


# ─── inspect ─────────────────────────────────────────────────────────────


class InspectSkill(BaseSkill):
    """Look at a target (object or area)."""

    _skill = Skill(
        skill_id=SkillId("inspect"),
        name="inspect",
        description="Inspect a target to update the world model.",
        spec=SkillSpec(
            parameters={"target": {"type": "string"}},
            required_capabilities=(CapabilityId("can_see"),),
        ),
    )

    def run(self, parameters: dict[str, Any], world: WorldState) -> SkillResult:
        target = _require_param(parameters, "target")
        # Inspect has no hard precondition in v0.1 — it always succeeds.
        # Real perception updates arrive via the simulator in a later
        # iteration; the world model will apply them.
        return self._success(payload={"target": target} if target else {})


__all__ = [
    "GraspSkill",
    "InspectSkill",
    "LiftSkill",
    "NavigateToSkill",
    "PullSkill",
    "PushSkill",
    "ReachSkill",
    "ReleaseSkill",
]
