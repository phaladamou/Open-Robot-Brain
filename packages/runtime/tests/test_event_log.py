"""Tests for orb_runtime.events.log."""

from __future__ import annotations

from orb_runtime.events.log import EventLog
from orb_types import Event, EventId, EventKind, EventSeverity, utc_now


def _event(
    event_id: str,
    kind: EventKind = EventKind.RUNTIME_STARTED,
    severity: EventSeverity = EventSeverity.INFO,
    correlation_id: str | None = None,
) -> Event:
    return Event(
        event_id=EventId(event_id),
        kind=kind,
        timestamp=utc_now(),
        severity=severity,
        correlation_id=correlation_id,
    )


def test_empty_log() -> None:
    log = EventLog()
    assert len(log) == 0
    assert log.all() == ()
    assert log.last() is None


def test_append_and_len() -> None:
    log = EventLog()
    log.append(_event("evt_01"))
    log.append(_event("evt_02"))
    assert len(log) == 2


def test_iter() -> None:
    log = EventLog()
    log.append(_event("evt_01"))
    log.append(_event("evt_02"))
    ids = [e.event_id for e in log]
    assert ids == ["evt_01", "evt_02"]


def test_all_returns_tuple() -> None:
    log = EventLog()
    log.append(_event("evt_01"))
    events = log.all()
    assert isinstance(events, tuple)
    assert len(events) == 1


def test_by_kind() -> None:
    log = EventLog()
    log.append(_event("evt_01", kind=EventKind.RUNTIME_STARTED))
    log.append(_event("evt_02", kind=EventKind.ACTION_DISPATCHED))
    log.append(_event("evt_03", kind=EventKind.ACTION_DISPATCHED))

    actions = log.by_kind(EventKind.ACTION_DISPATCHED)
    assert len(actions) == 2
    assert [e.event_id for e in actions] == ["evt_02", "evt_03"]


def test_by_severity() -> None:
    log = EventLog()
    log.append(_event("evt_01", severity=EventSeverity.INFO))
    log.append(_event("evt_02", severity=EventSeverity.ERROR))

    errors = log.by_severity(EventSeverity.ERROR)
    assert len(errors) == 1
    assert errors[0].event_id == "evt_02"


def test_by_correlation() -> None:
    log = EventLog()
    log.append(_event("evt_01", correlation_id="task_abc"))
    log.append(_event("evt_02", correlation_id="task_xyz"))
    log.append(_event("evt_03", correlation_id="task_abc"))

    chain = log.by_correlation("task_abc")
    assert len(chain) == 2
    assert [e.event_id for e in chain] == ["evt_01", "evt_03"]


def test_last() -> None:
    log = EventLog()
    log.append(_event("evt_01"))
    log.append(_event("evt_02"))
    assert log.last() is not None
    assert log.last().event_id == "evt_02"  # type: ignore[union-attr]


def test_clear() -> None:
    log = EventLog()
    log.append(_event("evt_01"))
    log.append(_event("evt_02"))
    log.clear()
    assert len(log) == 0
    assert log.all() == ()
