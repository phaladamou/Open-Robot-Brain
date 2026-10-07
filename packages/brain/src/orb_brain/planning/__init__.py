"""Planning layer for Open Robot Brain.

The planner turns a :class:`Goal` into an executable :class:`Plan`.

v0.1 uses a **rule-based HTN planner**: a set of decomposition rules maps
a goal's predicate to a sequence of atomic skill steps. It is:

- deterministic,
- dependency-free,
- fully testable,
- and easy to extend (add a rule, get a new behavior).

Design
------
- The planner is a **pure function**: ``plan(goal, world) -> Plan``.
  It does not publish events; the executor does.
- Object resolution is done by the planner against the current
  :class:`WorldState`: a goal referencing a color/type is resolved to a
  concrete ``object_id`` before steps are built.
- Failure to find a rule or resolve an object raises
  :class:`~orb_types.PlanningError`.

An LLM-based planner can replace this implementation behind the same
:class:`~orb_interfaces.Planner` protocol in v0.2+.
"""

from orb_brain.planning.htn import HtnPlanner, PlanningError

__all__ = [
    "HtnPlanner",
    "PlanningError",
]
