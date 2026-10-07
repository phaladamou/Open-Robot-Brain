"""Tick-based scheduler.

See :mod:`orb_runtime.scheduler` for the design rationale.

The scheduler owns:

- a :class:`Clock`,
- a set of periodic timers,
- a set of one-shot timers,
- a reference to the :class:`EventBus` for tick events.

It exposes :meth:`tick` (one step) and :meth:`run_until` (loop until a
deadline). It intentionally does **not** expose ``run_forever`` — the
application decides when to stop.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from orb_types import Event, EventId, EventKind, EventSeverity, new_id

from orb_runtime.events.bus import EventBus
from orb_runtime.scheduler.clock import Clock

TimerCallback = Callable[[], None]
"""A function invoked when a timer fires."""


@dataclass(slots=True)
class TimerHandle:
    """Handle to a scheduled timer.

    Call :meth:`cancel` to stop it. Safe to call multiple times.
    """

    _callback: TimerCallback
    _period: float
    _next_fire: float
    _one_shot: bool
    _active: bool = True
    _label: str | None = None

    @property
    def active(self) -> bool:
        """Whether this timer is still scheduled."""
        return self._active

    @property
    def period(self) -> float:
        """Period in seconds (``0.0`` for one-shot timers)."""
        return self._period

    def cancel(self) -> None:
        """Deactivate the timer. Idempotent."""
        self._active = False


class Scheduler:
    """Tick-based scheduler with periodic and one-shot timers.

    Parameters
    ----------
    bus:
        Event bus for ``SCHEDULER_TICK`` events.
    dt:
        Fixed time step in seconds. Must be strictly positive.

    Example
    -------
    >>> bus = EventBus()
    >>> sched = Scheduler(bus, dt=0.1)
    >>> calls = []
    >>> sched.schedule_every(0.3, lambda: calls.append(1))
    >>> sched.run_until(0.31)
    >>> len(calls)
    1
    """

    def __init__(self, bus: EventBus, *, dt: float) -> None:
        self._bus = bus
        self._clock = Clock(dt)
        self._timers: list[TimerHandle] = []

    # ─── Properties ─────────────────────────────────────────────────────

    @property
    def clock(self) -> Clock:
        """The scheduler's clock."""
        return self._clock

    @property
    def now(self) -> float:
        """Current simulation time, in seconds."""
        return self._clock.now()

    @property
    def dt(self) -> float:
        """Fixed time step, in seconds."""
        return self._clock.dt

    @property
    def step(self) -> int:
        """Number of ticks so far."""
        return self._clock.step

    # ─── Timer registration ─────────────────────────────────────────────

    def schedule_every(
        self,
        period: float,
        callback: TimerCallback,
        *,
        label: str | None = None,
    ) -> TimerHandle:
        """Schedule a periodic timer.

        The first fire happens at ``now + period``. Must be strictly
        positive.
        """
        if period <= 0.0:
            msg = f"period must be > 0, got {period!r}"
            raise ValueError(msg)
        handle = TimerHandle(
            _callback=callback,
            _period=float(period),
            _next_fire=self.now + float(period),
            _one_shot=False,
            _label=label,
        )
        self._timers.append(handle)
        return handle

    def schedule_once(
        self,
        delay: float,
        callback: TimerCallback,
        *,
        label: str | None = None,
    ) -> TimerHandle:
        """Schedule a one-shot timer.

        The callback fires once, at ``now + delay``. ``delay`` must be
        strictly positive.
        """
        if delay <= 0.0:
            msg = f"delay must be > 0, got {delay!r}"
            raise ValueError(msg)
        handle = TimerHandle(
            _callback=callback,
            _period=0.0,
            _next_fire=self.now + float(delay),
            _one_shot=True,
            _label=label,
        )
        self._timers.append(handle)
        return handle

    def pending(self) -> tuple[TimerHandle, ...]:
        """Return all active timers, in registration order."""
        return tuple(t for t in self._timers if t._active)

    def cancel_all(self) -> None:
        """Deactivate every timer and clear the schedule."""
        for t in self._timers:
            t._active = False
        self._timers.clear()

    # ─── Stepping ───────────────────────────────────────────────────────

    def tick(self) -> None:
        """Advance the clock by ``dt`` and fire any due timers.

        The scheduler:

        1. advances the clock,
        2. publishes ``SCHEDULER_TICK`` on the bus,
        3. fires all timers whose ``next_fire <= now``, in registration
           order. Periodic timers are rescheduled; one-shot timers are
           deactivated.
        """
        self._clock.advance()
        now = self.now

        self._bus.publish(
            Event(
                event_id=EventId(new_id("evt")),
                kind=EventKind.SCHEDULER_TICK,
                timestamp=self._now_timestamp(),
                source="scheduler",
                severity=EventSeverity.DEBUG,
                payload={"t": now, "step": self.step},
            )
        )

        # Snapshot: callbacks may register or cancel timers.
        for handle in tuple(self._timers):
            if not handle._active:
                continue
            if handle._next_fire <= now:
                self._invoke(handle, now)

    def run_until(self, deadline: float) -> None:
        """Run ticks without overshooting ``deadline``.

        A tick is only executed if it lands at or before ``deadline``.
        After this call, ``now <= deadline`` is guaranteed and ``now``
        is a multiple of ``dt``.

        Useful for bounded runs and benchmarks where overshoot would
        invalidate measurements. If ``deadline`` is already passed or
        would require a partial tick, returns immediately.
        """
        while self.now + self.dt <= deadline + 1e-12:
            self.tick()

    # ─── Internal ───────────────────────────────────────────────────────

    def _invoke(self, handle: TimerHandle, now: float) -> None:
        if handle._one_shot:
            handle._active = False
        else:
            # Reschedule: keep period, advance next_fire past now.
            handle._next_fire += handle._period
            # Guard against long handler delays: if we're already far past,
            # skip missed periods to avoid pile-up.
            if handle._next_fire <= now:
                handle._next_fire = now + handle._period
        handle._callback()

    def _now_timestamp(self) -> Any:
        # The scheduler uses simulated time, not wall time.
        # Timestamps on tick events use the real UTC now (see orb_types.utc_now)
        # because Event requires a Timestamp. Simulated time is in the payload.
        from orb_types import utc_now

        return utc_now()


__all__ = ["Scheduler", "TimerCallback", "TimerHandle"]
