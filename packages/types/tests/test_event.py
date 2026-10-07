"""Tests for orb_types.event."""

from __future__ import annotations

import pytest
from orb_types.base import utc_now
from orb_types.event import Event, EventKind, EventSeverity
from orb_types.ids import EventId
from pydantic import ValidationError as PydanticValidationError

# ─── Event ───────────────────────────────────────────────────────────────


def test_event_minimal() -> None:
    e = Event(
        event_id=EventId("evt_01"),
        kind=EventKind.RUNTIME_STARTED,
        timestamp=utc_now(),
    )
    assert e.kind == EventKind.RUNTIME_STARTED
    assert e.source == "runtime"
    assert e.severity == EventSeverity.INFO
    assert e.payload == {}
    assert e.correlation_id is None


def test_event_with_payload_and_correlation() -> None:
    e = Event(
        event_id=EventId("evt_02"),
        kind=EventKind.ACTION_DISPATCHED,
        timestamp=utc_now(),
        source="executor",
        severity=EventSeverity.DEBUG,
        payload={"action_name": "grasp", "object_id": "cup_01"},
        correlation_id="task_abc123",
    )
    assert e.source == "executor"
    assert e.severity == EventSeverity.DEBUG
    assert e.payload["action_name"] == "grasp"
    assert e.correlation_id == "task_abc123"


def test_event_custom() -> None:
    e = Event(
        event_id=EventId("evt_03"),
        kind=EventKind.CUSTOM,
        timestamp=utc_now(),
        payload={"kind_label": "my.custom.event", "value": 42},
    )
    assert e.kind == EventKind.CUSTOM
    assert e.payload["kind_label"] == "my.custom.event"


def test_event_rejects_empty_source() -> None:
    with pytest.raises(PydanticValidationError):
        Event(
            event_id=EventId("evt_04"),
            kind=EventKind.RUNTIME_STARTED,
            timestamp=utc_now(),
            source="",
        )


def test_event_frozen() -> None:
    e = Event(
        event_id=EventId("evt_05"),
        kind=EventKind.RUNTIME_STARTED,
        timestamp=utc_now(),
    )
    with pytest.raises(PydanticValidationError):
        e.severity = EventSeverity.ERROR  # type: ignore[misc]


def test_event_serializable() -> None:
    e = Event(
        event_id=EventId("evt_06"),
        kind=EventKind.SAFETY_VIOLATION,
        timestamp=utc_now(),
        severity=EventSeverity.CRITICAL,
    )
    d = e.to_dict()
    assert d["kind"] == "safety.violation"
    assert d["severity"] == "critical"


def test_event_kind_namespaced_values() -> None:
    # Ensure namespaced event kinds keep their dot-form in serialization.
    assert EventKind.ACTION_DISPATCHED.value == "action.dispatched"
    assert EventKind.WORLD_UPDATED.value == "world.updated"
