"""Reasoning layer for Open Robot Brain.

Two responsibilities:

- **Goal parsing**: turn a natural-language instruction into a structured
  :class:`Goal`.
- **Reasoning**: judge whether a goal is well-formed, reachable, and
  feasible given the current world and the embodiment's capabilities.

Reasoning never plans. The planner does. This separation keeps each
component honest and testable.
"""

from orb_brain.reasoning.goal_parser import GoalParser, ParseError
from orb_brain.reasoning.reasoner import Reasoner

__all__ = [
    "GoalParser",
    "ParseError",
    "Reasoner",
]
