"""Executor for Open Robot Brain.

The executor orchestrates a single task end to end:

1. ask the planner for a plan,
2. dispatch each step to the skill registry,
3. aggregate results into a :class:`TaskResult`.

It is intentionally **simple in v0.1**: no re-planning, no recovery,
no parallel steps. Those are v0.2+ concerns and will be added by
evolving this component — the interface is designed to accommodate
them.
"""

from orb_runtime.executor.executor import Executor

__all__ = ["Executor"]
