"""Basic environments for v0.1.

Each function returns a fresh :class:`~orb_types.WorldState` with a
deterministic layout. No randomness — scenarios must be reproducible.
"""

from __future__ import annotations

from orb_types import (
    Location,
    Object,
    ObjectId,
    Pose,
    Surface,
    Vec3,
    WorldState,
    utc_now,
)

# Default tabletop dimensions (meters).
_TABLE_SIZE: tuple[float, float, float] = (1.2, 0.8, 0.02)
_TABLE_POSE = Pose(position=Vec3(x=0.0, y=0.0, z=0.75))


def empty() -> WorldState:
    """Return an empty world (no objects, no surfaces)."""
    return WorldState(timestamp=utc_now())


def table_with_cube(color: str = "red", *, name: str | None = None) -> WorldState:
    """Return a world with a table and a single cube.

    Parameters
    ----------
    color:
        Cube color, stored in ``attributes["color"]``.
    name:
        Optional explicit object id. Defaults to ``"cube_<color>"``.
    """
    object_id = ObjectId(name if name is not None else f"cube_{color}")
    table = Surface(name="table", pose=_TABLE_POSE, size=_TABLE_SIZE)
    cube = Object(
        object_id=object_id,
        type="cube",
        pose=Pose(position=Vec3(x=0.0, y=0.0, z=0.76)),
        attributes={"color": color},
    )
    return WorldState(
        timestamp=utc_now(),
        objects=(cube,),
        surfaces=(table,),
    )


def table_with_cubes(*colors: str) -> WorldState:
    """Return a world with a table and one cube per color.

    Colors must be unique. Cubes are laid out in a row along the X axis.
    """
    if len(set(colors)) != len(colors):
        msg = f"duplicate colors: {colors!r}"
        raise ValueError(msg)

    table = Surface(name="table", pose=_TABLE_POSE, size=_TABLE_SIZE)
    cubes = tuple(
        Object(
            object_id=ObjectId(f"cube_{color}"),
            type="cube",
            pose=Pose(position=Vec3(x=-0.2 + 0.2 * i, y=0.0, z=0.76)),
            attributes={"color": color},
        )
        for i, color in enumerate(colors)
    )
    return WorldState(
        timestamp=utc_now(),
        objects=cubes,
        surfaces=(table,),
    )


def kitchen_simple() -> WorldState:
    """A minimal kitchen: table, drawer, two cubes, and named locations."""
    table = Surface(name="table", pose=_TABLE_POSE, size=_TABLE_SIZE)
    drawer = Object(
        object_id=ObjectId("drawer_01"),
        type="drawer",
        pose=Pose(position=Vec3(x=0.6, y=0.0, z=0.5)),
        attributes={"state": "closed"},
    )
    red_cube = Object(
        object_id=ObjectId("cube_red"),
        type="cube",
        pose=Pose(position=Vec3(x=0.0, y=-0.1, z=0.76)),
        attributes={"color": "red"},
    )
    blue_cube = Object(
        object_id=ObjectId("cube_blue"),
        type="cube",
        pose=Pose(position=Vec3(x=0.0, y=0.1, z=0.76)),
        attributes={"color": "blue"},
    )
    locations = (
        Location(name="kitchen"),
        Location(name="table_area"),
        Location(name="drawer_area"),
    )
    return WorldState(
        timestamp=utc_now(),
        objects=(red_cube, blue_cube, drawer),
        surfaces=(table,),
        locations=locations,
    )


__all__ = [
    "empty",
    "kitchen_simple",
    "table_with_cube",
    "table_with_cubes",
]
