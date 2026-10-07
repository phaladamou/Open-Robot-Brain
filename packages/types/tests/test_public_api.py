"""Verify the public API of orb_types."""

from __future__ import annotations

import orb_types


def test_public_api_exports_expected_names() -> None:
    expected = {
        # base
        "ORBModel",
        "Timestamp",
        "utc_now",
        # ids
        "ActionId",
        "AgentId",
        "CapabilityId",
        "EventId",
        "GoalId",
        "MemoryId",
        "ObjectId",
        "ObservationId",
        "PlanId",
        "RobotId",
        "SkillId",
        "TaskId",
        "WorldModelId",
        "new_id",
        # errors
        "CapabilityError",
        "ConfigurationError",
        "ExecutionError",
        "NotFoundError",
        "ORBError",
        "PlanningError",
        "PreconditionError",
        "SafetyError",
        "ValidationError",
        "VerificationError",
    }
    assert expected.issubset(set(orb_types.__all__))
    for name in expected:
        assert hasattr(orb_types, name), f"missing export: {name}"
