"""Environments for Open Robot Brain.

An **environment** is a builder function that returns an initial
:class:`~orb_types.WorldState`. Environments are intentionally small and
composable — they are the bricks scenarios are built from.

Conventions
-----------
- All poses are in the world frame, meters, right-handed Z-up.
- Object ids are stable and lower-case with underscores (``"cube_red"``).
- A ``table`` is a :class:`~orb_types.Surface` centred at the origin.
"""

from orb_simulation.environments.basic import (
    empty,
    kitchen_simple,
    table_with_cube,
    table_with_cubes,
)

__all__ = [
    "empty",
    "kitchen_simple",
    "table_with_cube",
    "table_with_cubes",
]
