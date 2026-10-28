"""Tests for orb_simulation.benchmarks."""

from __future__ import annotations

import pytest
from orb_simulation.benchmarks import RunnerFn, benchmark
from orb_types import RunResult, RunStatus


def _stub(script: list[tuple[RunStatus, float]]) -> tuple[list[str], RunnerFn]:
    """Build a (calls, run) stub cycling through (status, duration_s)."""
    calls: list[str] = []
    state = {"i": 0}

    def run(name: str) -> RunResult:
        calls.append(name)
        status, duration_s = script[state["i"] % len(script)]
        state["i"] += 1
        return RunResult(scenario_name=name, status=status, duration_s=duration_s)

    return calls, run


def test_success_rate_counts_expected_status() -> None:
    _, run = _stub(
        [
            (RunStatus.SUCCEEDED, 0.01),
            (RunStatus.SUCCEEDED, 0.02),
            (RunStatus.EXECUTION_FAILED, 0.03),
        ]
    )
    report = benchmark(["pick_red_cube"], 3, run=run)
    assert report["pick_red_cube"]["success_rate"] == pytest.approx(2.0 / 3.0)


def test_refusing_scenario_reports_full_success() -> None:
    _, run = _stub([(RunStatus.REASONING_FAILED, 0.01)])
    report = benchmark(["pick_red_cube_no_lift"], 2, run=run)
    assert report["pick_red_cube_no_lift"]["success_rate"] == 1.0


def test_mean_and_p95_durations() -> None:
    _, run = _stub(
        [
            (RunStatus.SUCCEEDED, 0.01),
            (RunStatus.SUCCEEDED, 0.02),
            (RunStatus.SUCCEEDED, 0.03),
            (RunStatus.SUCCEEDED, 0.04),
        ]
    )
    report = benchmark(["pick_red_cube"], 4, run=run)
    stats = report["pick_red_cube"]
    assert stats["mean_duration_ms"] == pytest.approx(25.0)
    assert stats["p95_duration_ms"] == pytest.approx(40.0)


def test_single_run_stats() -> None:
    _, run = _stub([(RunStatus.SUCCEEDED, 0.012)])
    report = benchmark(["pick_red_cube"], 1, run=run)
    stats = report["pick_red_cube"]
    assert stats["success_rate"] == 1.0
    assert stats["mean_duration_ms"] == pytest.approx(12.0)
    assert stats["p95_duration_ms"] == pytest.approx(12.0)


def test_empty_scenarios_returns_empty_report() -> None:
    calls, run = _stub([(RunStatus.SUCCEEDED, 0.01)])
    assert benchmark([], 3, run=run) == {}
    assert calls == []


def test_n_runs_must_be_positive() -> None:
    _, run = _stub([(RunStatus.SUCCEEDED, 0.01)])
    with pytest.raises(ValueError, match="n_runs"):
        benchmark(["pick_red_cube"], 0, run=run)
    with pytest.raises(ValueError, match="n_runs"):
        benchmark(["pick_red_cube"], -2, run=run)


def test_unknown_scenario_raises_keyerror() -> None:
    _, run = _stub([(RunStatus.SUCCEEDED, 0.01)])
    with pytest.raises(KeyError, match="unknown scenario"):
        benchmark(["teleport_to_mars"], 1, run=run)


def test_deterministic_given_deterministic_runner() -> None:
    script = [(RunStatus.SUCCEEDED, 0.01), (RunStatus.EXECUTION_FAILED, 0.05)]
    _, run = _stub(script)
    first = benchmark(["pick_red_cube", "open_drawer"], 4, run=run)
    _, run2 = _stub(script)
    second = benchmark(["pick_red_cube", "open_drawer"], 4, run=run2)
    assert first == second
