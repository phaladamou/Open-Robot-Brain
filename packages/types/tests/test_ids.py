"""Tests for orb_types.ids."""

from __future__ import annotations

import pytest
from orb_types.ids import new_id


def test_new_id_returns_prefixed_string() -> None:
    value = new_id("obj")
    assert value.startswith("obj_")
    assert len(value) == len("obj_") + 8


def test_new_id_unique() -> None:
    a = new_id("obj")
    b = new_id("obj")
    assert a != b


def test_new_id_rejects_invalid_prefix() -> None:
    with pytest.raises(ValueError):
        new_id("Obj")  # uppercase
    with pytest.raises(ValueError):
        new_id("1obj")  # starts with digit
    with pytest.raises(ValueError):
        new_id("")  # empty
