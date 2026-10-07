"""Tests for orb_runtime.scheduler.scheduler."""

from __future__ import annotations

import pytest
from orb_runtime.events.bus import EventBus
from orb_runtime.scheduler.scheduler import Scheduler
from orb_types import Event, EventKind


def _sched(dt: float = 0.1) -> tuple[EventBus, Scheduler]:
    bus = EventBus()
    return bus, Scheduler(bus, dt=dt)


# ─── Constructor & properties ────────────────────────────────────────────


def test_scheduler_starts_at_zero() -> None:
    _, sched = _sched()
    assert sched.now == 0.0
    assert sched.step == 0
    assert sched.dt == 0.1


# ─── Tick ────────────────────────────────────────────────────────────────


def test_tick_advances_clock() -> None:
    _, sched = _sched()
    sched.tick()
    assert sched.now == pytest.approx(0.1)
    assert sched.step == 1


def test_tick_publishes_scheduler_tick_event() -> None:
    bus, sched = _sched()
    events: list[Event] = []
    bus.subscribe(events.append, kind=EventKind.SCHEDULER_TICK)
    sched.tick()
    assert len(events) == 1
    assert events[0].source == "scheduler"
    assert events[0].payload["t"] == pytest.approx(0.1)
    assert events[0].payload["step"] == 1


# ─── schedule_every ──────────────────────────────────────────────────────


def test_schedule_every_rejects_zero_period() -> None:
    _, sched = _sched()
    with pytest.raises(ValueError, match="period must be"):
        sched.schedule_every(0.0, lambda: None)


def test_schedule_every_fires_periodically() -> None:
    _, sched = _sched(dt=0.1)
    calls: list[float] = []
    sched.schedule_every(0.3, lambda: calls.append(sched.now))

    sched.run_until(0.95)  # 9 ticks (0.9 max)
    # Fires at 0.3, 0.6, 0.9
    assert len(calls) == 3
    assert calls[0] == pytest.approx(0.3)
    assert calls[1] == pytest.approx(0.6)
    assert calls[2] == pytest.approx(0.9)


def test_schedule_every_continues_until_cancelled() -> None:
    _, sched = _sched(dt=0.1)
    calls: list[float] = []
    handle = sched.schedule_every(0.2, lambda: calls.append(sched.now))

    sched.run_until(0.45)  # fires at 0.2, 0.4
    assert len(calls) == 2

    handle.cancel()
    sched.run_until(0.95)
    assert len(calls) == 2  # no more fires


# ─── schedule_once ───────────────────────────────────────────────────────


def test_schedule_once_rejects_zero_delay() -> None:
    _, sched = _sched()
    with pytest.raises(ValueError, match="delay must be"):
        sched.schedule_once(0.0, lambda: None)


def test_schedule_once_fires_once() -> None:
    _, sched = _sched(dt=0.1)
    calls: list[float] = []
    sched.schedule_once(0.35, lambda: calls.append(sched.now))
    sched.run_until(1.0)
    assert len(calls) == 1
    assert calls[0] == pytest.approx(0.4)  # first tick >= 0.35


def test_schedule_once_can_be_cancelled() -> None:
    _, sched = _sched(dt=0.1)
    calls: list[int] = []
    h = sched.schedule_once(0.5, lambda: calls.append(1))
    h.cancel()
    sched.run_until(1.0)
    assert calls == []


# ─── Cancel-all ──────────────────────────────────────────────────────────


def test_cancel_all() -> None:
    _, sched = _sched()
    sched.schedule_every(0.1, lambda: None)
    sched.schedule_once(0.2, lambda: None)
    assert len(sched.pending()) == 2
    sched.cancel_all()
    assert sched.pending() == ()


# ─── Pending ─────────────────────────────────────────────────────────────


def test_pending_reflects_active_only() -> None:
    _, sched = _sched()
    h1 = sched.schedule_every(0.1, lambda: None)
    sched.schedule_once(0.2, lambda: None)
    assert len(sched.pending()) == 2
    h1.cancel()
    assert len(sched.pending()) == 1


# ─── run_until ───────────────────────────────────────────────────────────


def test_run_until_does_not_overshoot() -> None:
    _, sched = _sched(dt=0.1)
    sched.run_until(0.25)  # ticks at 0.1, 0.2 -> next tick (0.3) would overshoot
    assert sched.now == pytest.approx(0.2)
    assert sched.now <= 0.25


def test_run_until_already_passed() -> None:
    _, sched = _sched()
    sched.tick()
    sched.run_until(0.05)  # already past
    assert sched.step == 1  # no extra tick


# ─── Callback re-registration during tick ────────────────────────────────


def test_callback_can_register_new_timer() -> None:
    _, sched = _sched(dt=0.1)
    calls: list[str] = []

    def first() -> None:
        calls.append("first")
        sched.schedule_once(0.2, lambda: calls.append("second"))

    sched.schedule_once(0.1, first)
    sched.run_until(0.5)
    assert calls == ["first", "second"]


def test_callback_can_cancel_itself() -> None:
    _, sched = _sched(dt=0.1)
    calls: list[int] = []
    holder: list[object] = []

    def cb() -> None:
        calls.append(1)
        handle = holder[0]
        assert hasattr(handle, "cancel")
        handle.cancel()

    holder.append(sched.schedule_every(0.2, cb))
    sched.run_until(1.0)
    assert calls == [1]
