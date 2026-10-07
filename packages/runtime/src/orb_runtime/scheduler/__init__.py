"""Scheduler for Open Robot Brain.

The scheduler is the **time engine** of the runtime. It provides:

- a deterministic, simulation-friendly **clock** (tick-based, no wall time),
- periodic and one-shot **timers**,
- a :meth:`Scheduler.tick` stepping primitive,
- a :meth:`Scheduler.run_until` driver for tests and short demos.

Design
------
- **Tick-based**: time advances by a fixed ``dt`` per tick. This is what
  makes ORB reproducible — a run is fully determined by its inputs.
- **No wall time**: the clock is a pure counter in seconds. Wall-time
  sync is a concern for the app layer, not the scheduler.
- **Sequential**: handlers are invoked in subscription order. A slow
  handler delays the tick; the scheduler does not skip or parallelize.
- **Eventful**: every tick publishes ``EventKind.SCHEDULER_TICK`` on the
  bus so other components can react without direct coupling.
"""

from orb_runtime.scheduler.clock import Clock
from orb_runtime.scheduler.scheduler import Scheduler, TimerHandle

__all__ = [
    "Clock",
    "Scheduler",
    "TimerHandle",
]
