"""Tests for orb_runtime.scheduler.clock."""

from __future__ import annotations

import pytest
from orb_runtime.scheduler.clock import Clock

# ─── Constructor ─────────────────────────────────────────────────────────


def test_clock_rejects_zero_dt() -> None:
    with pytest.raises(ValueError, match="dt must be"):
        Clock(dt=0.0)


def test_clock_rejects_negative_dt() -> None:
    with pytest.raises(ValueError, match="dt must be"):
        Clock(dt=-0.1)


# ─── Reading ─────────────────────────────────────────────────────────────


def test_clock_starts_at_zero() -> None:
    c = Clock(dt=0.02)
    assert c.now() == 0.0
    assert c.step == 0


def test_clock_dt_property() -> None:
    c = Clock(dt=0.05)
    assert c.dt == 0.05


# ─── Advancing ───────────────────────────────────────────────────────────


def test_advance_moves_by_dt() -> None:
    c = Clock(dt=0.1)
    t = c.advance()
    assert t == pytest.approx(0.1)
    assert c.now() == pytest.approx(0.1)
    assert c.step == 1


def test_multiple_advances() -> None:
    c = Clock(dt=0.1)
    for _ in range(5):
        c.advance()
    assert c.now() == pytest.approx(0.5)
    assert c.step == 5


def test_advance_by_custom_duration() -> None:
    c = Clock(dt=0.1)
    c.advance_by(1.5)
    assert c.now() == pytest.approx(1.5)
    assert c.step == 1


def test_advance_by_rejects_negative() -> None:
    c = Clock(dt=0.1)
    with pytest.raises(ValueError, match="negative"):
        c.advance_by(-0.1)


# ─── Reset ───────────────────────────────────────────────────────────────


def test_reset() -> None:
    c = Clock(dt=0.1)
    c.advance()
    c.advance()
    c.reset()
    assert c.now() == 0.0
    assert c.step == 0
