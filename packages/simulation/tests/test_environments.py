"""Tests for orb_simulation.environments.basic."""

from __future__ import annotations

import pytest
from orb_simulation.environments import (
    empty,
    kitchen_simple,
    table_with_cube,
    table_with_cubes,
)
from orb_types import ObjectId

# ─── empty ───────────────────────────────────────────────────────────────


def test_empty_has_no_objects() -> None:
    w = empty()
    assert w.objects == ()
    assert w.surfaces == ()


# ─── table_with_cube ─────────────────────────────────────────────────────


def test_table_with_cube_default() -> None:
    w = table_with_cube()
    assert len(w.objects) == 1
    assert w.objects[0].object_id == "cube_red"
    assert w.objects[0].attributes["color"] == "red"
    assert len(w.surfaces) == 1


def test_table_with_cube_custom_color() -> None:
    w = table_with_cube(color="blue")
    assert w.objects[0].object_id == "cube_blue"


def test_table_with_cube_custom_name() -> None:
    w = table_with_cube(color="red", name="my_cube")
    assert w.objects[0].object_id == "my_cube"


# ─── table_with_cubes ────────────────────────────────────────────────────


def test_table_with_cubes_creates_one_per_color() -> None:
    w = table_with_cubes("red", "blue", "green")
    assert len(w.objects) == 3
    colors = sorted(o.attributes["color"] for o in w.objects)
    assert colors == ["blue", "green", "red"]


def test_table_with_cubes_unique_ids() -> None:
    w = table_with_cubes("red", "blue")
    ids = {o.object_id for o in w.objects}
    assert len(ids) == 2


def test_table_with_cubes_rejects_duplicates() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        table_with_cubes("red", "red")


def test_table_with_cubes_layout_is_deterministic() -> None:
    w1 = table_with_cubes("red", "blue")
    w2 = table_with_cubes("red", "blue")
    assert [o.pose.position.x for o in w1.objects] == [o.pose.position.x for o in w2.objects]


# ─── kitchen_simple ──────────────────────────────────────────────────────


def test_kitchen_has_objects() -> None:
    w = kitchen_simple()
    ids = {o.object_id for o in w.objects}
    assert ObjectId("cube_red") in ids
    assert ObjectId("cube_blue") in ids
    assert ObjectId("drawer_01") in ids


def test_kitchen_has_locations() -> None:
    w = kitchen_simple()
    names = {loc.name for loc in w.locations}
    assert "kitchen" in names
    assert "table_area" in names
    assert "drawer_area" in names


def test_kitchen_is_deterministic() -> None:
    w1 = kitchen_simple()
    w2 = kitchen_simple()
    ids1 = sorted(o.object_id for o in w1.objects)
    ids2 = sorted(o.object_id for o in w2.objects)
    assert ids1 == ids2
