"""Synchronous event bus for Open Robot Brain.

Design
------
- **Synchronous**: handlers are invoked in the order of subscription, on the
  caller's thread. This is deliberate — v0.1 of ORB must be deterministic
  for simulation and benchmarks.
- **Typed subscriptions**: a handler may subscribe to a specific
  :class:`EventKind`, or to all events (``kind=None``).
- **Error isolation**: a handler that raises does not stop the dispatch; the
  error is captured and re-raised *after* all handlers have run, so no
  subscriber silently blocks another.
- **Immutable events**: :class:`Event` is frozen at the type layer. The bus
  never mutates events.

Non-goals (v0.1)
----------------
- No async.
- No priorities.
- No persistent log (see :class:`EventLog` for in-memory only).
"""

from __future__ import annotations

import contextlib
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from orb_types import Event, EventKind

if TYPE_CHECKING:
    pass

Handler = Callable[[Event], None]
"""A function that consumes an :class:`Event`."""


@dataclass(slots=True)
class Subscription:
    """Handle returned by :meth:`EventBus.subscribe`.

    Call :meth:`unsubscribe` on the bus with this handle to remove the
    subscription.
    """

    handler: Handler
    kind: EventKind | None
    _active: bool = field(default=True)

    @property
    def active(self) -> bool:
        """Whether this subscription is still active."""
        return self._active


class EventBus:
    """Synchronous publish/subscribe hub for :class:`Event` objects.

    Example
    -------
    >>> bus = EventBus()
    >>> def on_event(e): print(e.kind)
    >>> sub = bus.subscribe(on_event)
    >>> bus.publish(event)
    """

    def __init__(self) -> None:
        self._subs: list[Subscription] = []

    # ─── Subscription management ────────────────────────────────────────

    def subscribe(
        self,
        handler: Handler,
        *,
        kind: EventKind | None = None,
    ) -> Subscription:
        """Register a handler.

        Parameters
        ----------
        handler:
            Function invoked with each matching event.
        kind:
            If provided, only events of this kind are delivered. If ``None``,
            the handler receives every event.

        Returns
        -------
        Subscription
            Handle for later unsubscription.
        """
        sub = Subscription(handler=handler, kind=kind)
        self._subs.append(sub)
        return sub

    def unsubscribe(self, sub: Subscription) -> None:
        """Deactivate the given subscription.

        Safe to call multiple times; safe to call with a subscription that
        was already removed.
        """
        sub._active = False
        with contextlib.suppress(ValueError):
            self._subs.remove(sub)

    def clear(self) -> None:
        """Deactivate and remove every subscription."""
        for sub in self._subs:
            sub._active = False
        self._subs.clear()

    # ─── Introspection ──────────────────────────────────────────────────

    def subscriber_count(self, *, kind: EventKind | None = None) -> int:
        """Return the number of active subscriptions.

        Without arguments, counts **all** active subscriptions.
        With ``kind=<X>``, counts only subscriptions registered for that
        exact kind. To count catch-all subscriptions (those registered
        with ``kind=None``), call :meth:`subscriber_count_all_kinds`.
        """
        if kind is None:
            return sum(1 for s in self._subs if s.active)
        return sum(1 for s in self._subs if s.active and s.kind == kind)

    def subscriber_count_catch_all(self) -> int:
        """Return the number of active catch-all subscriptions (kind=None)."""
        return sum(1 for s in self._subs if s.active and s.kind is None)

    # ─── Publishing ─────────────────────────────────────────────────────

    def publish(self, event: Event) -> None:
        """Dispatch an event to all matching subscribers.

        Handlers are invoked in subscription order. A handler that raises
        does not prevent other handlers from running; the first exception
        is re-raised after every handler has been invoked.
        """
        first_error: BaseException | None = None

        # Iterate over a snapshot: subscribers may unsubscribe during dispatch.
        for sub in tuple(self._subs):
            if not sub.active:
                continue
            if sub.kind is not None and sub.kind != event.kind:
                continue
            try:
                sub.handler(event)
            except BaseException as exc:
                if first_error is None:
                    first_error = exc

        if first_error is not None:
            raise first_error


__all__ = ["EventBus", "Handler", "Subscription"]
