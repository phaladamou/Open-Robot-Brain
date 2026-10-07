"""World model for Open Robot Brain.

The world model maintains the brain's **belief about the world**. It:

- subscribes to the event bus,
- consumes :class:`Observation` objects,
- updates the :class:`WorldState` held by the :class:`StateStore`.

It is the **bridge** between perception and cognition: raw observations
become structured, shared world state.

Design (v0.1)
-------------
- Only ``Observation`` objects are consumed, and only a small set of
  ``ObservationKind`` values are handled. Others are ignored with a
  debug log entry.
- Updates are *replace-and-merge*: incoming objects replace existing ones
  with the same ``object_id``; new objects are appended.
- Observations below ``confidence_threshold`` are dropped.
- No temporal reasoning, no prediction, no uncertainty propagation in
  v0.1. These are v0.2+ concerns.
"""

from orb_brain.world_model.model import WorldModel

__all__ = ["WorldModel"]
