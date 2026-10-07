"""In-memory append-only event log.

The log records every event that flows through the runtime. It is used for:

- debugging (replay what happened),
- evaluation (count events by kind/severity),
- future learning (episodic memory).

It is **not** persistent in v0.1 — persistence comes later.
"""

from __future__ import annotations

from collections.abc import Iterator

from orb_types import Event, EventKind, EventSeverity


class EventLog:
    """Append-only in-memory log of :class:`Event` objects.

    Example
    -------
    >>> log = EventLog()
    >>> log.append(event)
    >>> len(log)
    1
    """

    def __init__(self) -> None:
        self._events: list[Event] = []

    # ─── Writing ────────────────────────────────────────────────────────

    def append(self, event: Event) -> None:
        """Append an event to the log."""
        self._events.append(event)

    def clear(self) -> None:
        """Remove all events."""
        self._events.clear()

    # ─── Reading ────────────────────────────────────────────────────────

    def __len__(self) -> int:
        return len(self._events)

    def __iter__(self) -> Iterator[Event]:
        return iter(self._events)

    def all(self) -> tuple[Event, ...]:
        """Return every event as an immutable tuple."""
        return tuple(self._events)

    def by_kind(self, kind: EventKind) -> tuple[Event, ...]:
        """Return all events of the given kind."""
        return tuple(e for e in self._events if e.kind == kind)

    def by_severity(self, severity: EventSeverity) -> tuple[Event, ...]:
        """Return all events with the given severity."""
        return tuple(e for e in self._events if e.severity == severity)

    def by_correlation(self, correlation_id: str) -> tuple[Event, ...]:
        """Return all events with the given correlation ID."""
        return tuple(e for e in self._events if e.correlation_id == correlation_id)

    def last(self) -> Event | None:
        """Return the most recently appended event, or ``None``."""
        return self._events[-1] if self._events else None


__all__ = ["EventLog"]
