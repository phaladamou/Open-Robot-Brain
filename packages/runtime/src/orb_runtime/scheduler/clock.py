"""Deterministic simulation clock.

The clock is a **pure counter** in seconds. It never reads wall time.
Callers advance it explicitly via :meth:`Clock.advance`.
"""

from __future__ import annotations


class Clock:
    """A monotonic, simulation-friendly clock.

    Parameters
    ----------
    dt:
        Fixed time step in seconds. Must be strictly positive.

    Example
    -------
    >>> clock = Clock(dt=0.02)
    >>> clock.now()
    0.0
    >>> clock.advance()
    >>> round(clock.now(), 2)
    0.02
    """

    def __init__(self, dt: float) -> None:
        if dt <= 0.0:
            msg = f"dt must be > 0, got {dt!r}"
            raise ValueError(msg)
        self._dt = float(dt)
        self._t = 0.0
        self._step = 0

    # ─── Properties ─────────────────────────────────────────────────────

    @property
    def dt(self) -> float:
        """Fixed time step in seconds."""
        return self._dt

    @property
    def step(self) -> int:
        """Number of advances since creation."""
        return self._step

    # ─── Reading ────────────────────────────────────────────────────────

    def now(self) -> float:
        """Current simulation time, in seconds."""
        return self._t

    # ─── Advancing ──────────────────────────────────────────────────────

    def advance(self) -> float:
        """Advance the clock by one ``dt`` and return the new time."""
        self._t += self._dt
        self._step += 1
        return self._t

    def advance_by(self, duration: float) -> float:
        """Advance the clock by ``duration`` seconds (not necessarily ``dt``).

        The clock's ``step`` counter still increments by 1. This is used
        internally for large jumps in tests.
        """
        if duration < 0.0:
            msg = f"cannot advance by negative duration {duration!r}"
            raise ValueError(msg)
        self._t += duration
        self._step += 1
        return self._t

    def reset(self) -> None:
        """Reset time to 0 and step counter to 0."""
        self._t = 0.0
        self._step = 0


__all__ = ["Clock"]
