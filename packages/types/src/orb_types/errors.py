"""Exception hierarchy for Open Robot Brain.

All ORB-specific exceptions inherit from :class:`ORBError`. This allows
callers to catch the entire family with a single ``except ORBError``.

Categories
----------
- :class:`ORBError`               — base class for all ORB errors
- :class:`ValidationError`        — semantic validation failure
- :class:`NotFoundError`          — requested entity does not exist
- :class:`CapabilityError`        — a required capability is missing
- :class:`PreconditionError`      — a skill precondition is not met
- :class:`VerificationError`      — an action or skill failed verification
- :class:`PlanningError`          — planner could not produce a valid plan
- :class:`ExecutionError`         — runtime execution failure
- :class:`SafetyError`            — safety layer rejected an intent
- :class:`ConfigurationError`     — invalid configuration
"""

from __future__ import annotations

from typing import Any


class ORBError(Exception):
    """Base exception for every Open Robot Brain error.

    Parameters
    ----------
    message:
        Human-readable message.
    context:
        Optional structured context (IDs, values, reasons).
    """

    def __init__(self, message: str, /, **context: Any) -> None:
        super().__init__(message)
        self.message = message
        self.context: dict[str, Any] = dict(context)

    def __str__(self) -> str:
        if not self.context:
            return self.message
        ctx = ", ".join(f"{k}={v!r}" for k, v in self.context.items())
        return f"{self.message} ({ctx})"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(message={self.message!r}, context={self.context!r})"


# ─── Category errors ─────────────────────────────────────────────────────


class ValidationError(ORBError):
    """A value or structure failed semantic validation."""


class NotFoundError(ORBError):
    """A requested entity could not be found."""


class CapabilityError(ORBError):
    """The current embodiment lacks a required capability."""


class PreconditionError(ORBError):
    """A skill or action precondition is not satisfied."""


class VerificationError(ORBError):
    """A skill or action failed its verification step."""


class PlanningError(ORBError):
    """The planner could not produce a valid plan for the given goal."""


class ExecutionError(ORBError):
    """The runtime failed to execute a plan, skill, or action."""


class SafetyError(ORBError):
    """The safety layer rejected an intent before physical execution."""


class ConfigurationError(ORBError):
    """The system was given an invalid configuration."""


__all__ = [
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
]
