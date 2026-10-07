"""Tests for orb_types.base."""

from __future__ import annotations

from datetime import UTC

import pytest
from orb_types.base import ORBModel, utc_now
from pydantic import ValidationError as PydanticValidationError


class _Sample(ORBModel):
    name: str
    count: int = 0


def test_orbmodel_constructs() -> None:
    s = _Sample(name="hello")
    assert s.name == "hello"
    assert s.count == 0


def test_orbmodel_is_frozen() -> None:
    s = _Sample(name="hello")
    with pytest.raises(PydanticValidationError):
        s.name = "other"  # type: ignore[misc]


def test_orbmodel_forbids_extra_fields() -> None:
    with pytest.raises(PydanticValidationError):
        _Sample(name="hello", unknown=1)  # type: ignore[call-arg]


def test_orbmodel_strips_whitespace() -> None:
    s = _Sample(name="  hello  ")
    assert s.name == "hello"


def test_orbmodel_to_dict_and_json() -> None:
    s = _Sample(name="hello", count=3)
    d = s.to_dict()
    assert d == {"name": "hello", "count": 3}
    j = s.to_json()
    assert '"name":"hello"' in j.replace(" ", "")


def test_utc_now_is_timezone_aware() -> None:
    now = utc_now()
    assert now.tzinfo is not None
    assert now.tzinfo == UTC
