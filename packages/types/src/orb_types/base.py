"""Base primitives shared by every Open Robot Brain type.

This module defines the foundation every other type builds on:

- :class:`ORBModel` — strict, immutable-by-default Pydantic base.
- :data:`Timestamp` — UTC datetime alias.
- :func:`utc_now` — timezone-aware UTC "now".

Design rules
------------
- All types are **strict** and **validated** at construction.
- All types are **immutable** by default (``frozen=True``).
- Extra fields are **forbidden** — typos raise, not silently pass.
- All datetimes are **timezone-aware** and normalized to UTC.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

# ─── Aliases ─────────────────────────────────────────────────────────────

Timestamp = datetime
"""Alias for timezone-aware UTC datetimes used across ORB types."""


# ─── Helpers ─────────────────────────────────────────────────────────────


def utc_now() -> Timestamp:
    """Return the current time as a timezone-aware UTC :class:`datetime`."""
    return datetime.now(UTC)


# ─── Base model ──────────────────────────────────────────────────────────


class ORBModel(BaseModel):
    """Base class for every Open Robot Brain type.

    Guarantees:

    - ``frozen=True``  → instances are immutable after construction
    - ``extra='forbid'`` → unknown fields raise a validation error
    - ``validate_assignment=True`` → revalidation on mutation of allowed fields
    - ``str_strip_whitespace=True`` → trims whitespace on string fields

    Every domain type in ORB must inherit from this class.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
        arbitrary_types_allowed=False,
        use_enum_values=False,
    )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dict representation."""
        return self.model_dump(mode="json")

    def to_json(self) -> str:
        """Return a JSON string representation."""
        return self.model_dump_json()


__all__ = ["ORBModel", "Timestamp", "utc_now"]
