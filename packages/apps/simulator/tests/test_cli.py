"""Tests for orb_apps_simulator.cli."""

from __future__ import annotations

import json

import pytest
from orb_apps_simulator.cli import main
from orb_simulation import SCENARIOS


def test_cli_list(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["--list"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "pick_red_cube" in out
    assert "open_drawer" in out


def test_cli_default_scenario(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main([])
    assert rc == 0
    out = capsys.readouterr().out
    assert "pick_red_cube" in out


def test_cli_specific_scenario(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["pick_blue_cube"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "pick_blue_cube" in out


def test_cli_benchmark_prints_pure_json(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["--benchmark"])
    assert rc == 0
    captured = capsys.readouterr()
    report = json.loads(captured.out)
    assert set(report) == set(SCENARIOS)
    for stats in report.values():
        assert set(stats) == {"success_rate", "mean_duration_ms", "p95_duration_ms"}
    assert "run.finished" in captured.err


def test_cli_benchmark_all_scenarios_reach_expectations(
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main(["--benchmark"])
    assert rc == 0
    report = json.loads(capsys.readouterr().out)
    for name, stats in report.items():
        assert stats["success_rate"] == 1.0, f"scenario {name} regressed"
        assert stats["mean_duration_ms"] >= 0.0
        assert stats["p95_duration_ms"] >= 0.0
