"""Tests for orb_runtime.events.bus."""

from __future__ import annotations

import pytest
from orb_runtime.events.bus import EventBus
from orb_types import Event, EventId, EventKind, EventSeverity, utc_now


def _event(kind: EventKind = EventKind.RUNTIME_STARTED) -> Event:
    return Event(event_id=EventId("evt_test"), kind=kind, timestamp=utc_now())


# ─── Subscription ────────────────────────────────────────────────────────


def test_subscribe_and_publish_catch_all() -> None:
    bus = EventBus()
    received: list[Event] = []
    bus.subscribe(received.append)
    e = _event()
    bus.publish(e)
    assert received == [e]


def test_subscribe_specific_kind() -> None:
    bus = EventBus()
    received: list[Event] = []
    bus.subscribe(received.append, kind=EventKind.ACTION_DISPATCHED)
    bus.publish(_event(EventKind.RUNTIME_STARTED))
    bus.publish(_event(EventKind.ACTION_DISPATCHED))
    assert len(received) == 1
    assert received[0].kind == EventKind.ACTION_DISPATCHED


def test_multiple_subscribers_in_order() -> None:
    bus = EventBus()
    calls: list[str] = []
    bus.subscribe(lambda _e: calls.append("a"))
    bus.subscribe(lambda _e: calls.append("b"))
    bus.subscribe(lambda _e: calls.append("c"))
    bus.publish(_event())
    assert calls == ["a", "b", "c"]


def test_unsubscribe() -> None:
    bus = EventBus()
    received: list[Event] = []
    sub = bus.subscribe(received.append)
    bus.publish(_event())
    bus.unsubscribe(sub)
    bus.publish(_event())
    assert len(received) == 1
    assert not sub.active


def test_unsubscribe_idempotent() -> None:
    bus = EventBus()
    sub = bus.subscribe(lambda _e: None)
    bus.unsubscribe(sub)
    bus.unsubscribe(sub)  # must not raise


def test_clear() -> None:
    bus = EventBus()
    bus.subscribe(lambda _e: None)
    bus.subscribe(lambda _e: None)
    assert bus.subscriber_count() == 2
    bus.clear()
    assert bus.subscriber_count() == 0


def test_subscriber_count_by_kind() -> None:
    bus = EventBus()
    bus.subscribe(lambda _e: None)  # catch-all
    bus.subscribe(lambda _e: None, kind=EventKind.ACTION_DISPATCHED)
    assert bus.subscriber_count() == 2  # all
    assert bus.subscriber_count(kind=EventKind.ACTION_DISPATCHED) == 1
    assert bus.subscriber_count(kind=EventKind.RUNTIME_STARTED) == 0
    assert bus.subscriber_count_catch_all() == 1


# ─── Error isolation ─────────────────────────────────────────────────────


def test_handler_error_does_not_stop_others() -> None:
    bus = EventBus()
    calls: list[str] = []

    def bad(_e: Event) -> None:
        raise RuntimeError("boom")

    bus.subscribe(bad)
    bus.subscribe(lambda _e: calls.append("after"))

    with pytest.raises(RuntimeError, match="boom"):
        bus.publish(_event())

    # The second handler still ran.
    assert calls == ["after"]


def test_first_error_is_reraised() -> None:
    bus = EventBus()

    def e1(_e: Event) -> None:
        raise ValueError("first")

    def e2(_e: Event) -> None:
        raise RuntimeError("second")

    bus.subscribe(e1)
    bus.subscribe(e2)

    with pytest.raises(ValueError, match="first"):
        bus.publish(_event())


# ─── Self-unsubscribe during dispatch ────────────────────────────────────


def test_handler_can_unsubscribe_itself() -> None:
    bus = EventBus()
    calls: list[int] = []

    def handler(_e: Event) -> None:
        calls.append(1)
        bus.unsubscribe(sub)

    sub = bus.subscribe(handler)
    bus.publish(_event())
    bus.publish(_event())
    assert calls == [1]


# ─── Severity is not a dispatch filter (only kind is) ────────────────────


def test_severity_does_not_filter() -> None:
    bus = EventBus()
    received: list[Event] = []
    bus.subscribe(received.append)
    e = Event(
        event_id=EventId("evt_x"),
        kind=EventKind.RUNTIME_STARTED,
        timestamp=utc_now(),
        severity=EventSeverity.CRITICAL,
    )
    bus.publish(e)
    assert received == [e]
