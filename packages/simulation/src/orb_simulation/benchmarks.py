"""Reproducible scenario benchmarks.

A benchmark answers "did the system get better or worse?" with numbers
instead of impressions. :func:`benchmark` runs each scenario ``n_runs``
times and reports, per scenario, the fraction of runs reaching the
scenario's expected status plus mean/p95 durations in milliseconds.

Two determinism notes, stated honestly:

- Outcomes (``success_rate``) are deterministic for a deterministic
  pipeline: same code, same seeds, same expectations, same rate.
- Durations are *measured* wall time: exact across runs on one machine
  only up to noise. Track them as trends (JSON diffs), not as exact
  assertions.

The scenario runner is injected (``run``) rather than imported: the
reference runner lives in the app layer, and simulation must not
depend on apps. The CLI wires ``run_scenario``; tests inject stubs.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence

from orb_types import RunResult

from orb_simulation.scenarios import get_scenario

#: Runs one scenario end to end and returns its result.
RunnerFn = Callable[[str], RunResult]

#: Per-scenario stats: success_rate, mean_duration_ms, p95_duration_ms.
BenchmarkStats = dict[str, float]

#: Full report: scenario name → stats. JSON-serializable by construction.
BenchmarkReport = dict[str, BenchmarkStats]


def _percentile(sorted_values: Sequence[float], pct: float) -> float:
    """Nearest-rank percentile of pre-sorted non-empty values."""
    rank = math.ceil(pct / 100.0 * len(sorted_values))
    index = max(0, min(rank - 1, len(sorted_values) - 1))
    return sorted_values[index]


def benchmark(
    scenarios: Sequence[str],
    n_runs: int,
    *,
    run: RunnerFn,
) -> BenchmarkReport:
    """Run scenarios repeatedly and report per-scenario stats.

    Parameters
    ----------
    scenarios:
        Scenario names to evaluate (see :mod:`orb_simulation.scenarios`).
    n_runs:
        Runs per scenario. Must be ``>= 1``.
    run:
        Scenario runner (e.g. the simulator app's ``run_scenario``).

    Returns
    -------
    BenchmarkReport
        ``{scenario: {"success_rate": ..., "mean_duration_ms": ...,
        "p95_duration_ms": ...}}``. A run counts as successful when its
        status matches the scenario's ``expected_status`` metadata
        (default ``"succeeded"``), so scenarios that pass *by refusing*
        (e.g. missing capability) report 1.0 instead of 0.0.

    Raises
    ------
    ValueError
        If ``n_runs < 1``.
    KeyError
        If a scenario name is unknown.
    """
    if n_runs < 1:
        msg = f"n_runs must be >= 1, got {n_runs!r}"
        raise ValueError(msg)

    report: BenchmarkReport = {}
    for name in scenarios:
        expected = get_scenario(name).metadata.get("expected_status", "succeeded")
        ok = 0
        durations_ms: list[float] = []
        for _ in range(n_runs):
            result = run(name)
            durations_ms.append(result.duration_s * 1000.0)
            if result.status.value == expected:
                ok += 1
        durations_ms.sort()
        report[name] = {
            "success_rate": ok / n_runs,
            "mean_duration_ms": sum(durations_ms) / n_runs,
            "p95_duration_ms": _percentile(durations_ms, 95),
        }
    return report


__all__ = ["BenchmarkReport", "BenchmarkStats", "RunnerFn", "benchmark"]
