"""Tests for orb_types.errors."""

from __future__ import annotations

import pytest
from orb_types.errors import (
    CapabilityError,
    NotFoundError,
    ORBError,
    PlanningError,
    SafetyError,
    VerificationError,
)


def test_orb_error_message() -> None:
    err = ORBError("something failed")
    assert str(err) == "something failed"
    assert err.message == "something failed"
    assert err.context == {}


def test_orb_error_with_context() -> None:
    err = ORBError("failed", object_id="cup_01", reason="unreachable")
    assert "object_id='cup_01'" in str(err)
    assert "reason='unreachable'" in str(err)
    assert err.context == {"object_id": "cup_01", "reason": "unreachable"}


def test_orb_error_repr() -> None:
    err = ORBError("boom", x=1)
    assert "ORBError" in repr(err)
    assert "boom" in repr(err)


def test_subclasses_are_orb_errors() -> None:
    for cls in (CapabilityError, NotFoundError, PlanningError, SafetyError, VerificationError):
        assert issubclass(cls, ORBError)
        with pytest.raises(ORBError):
            raise cls("test")
