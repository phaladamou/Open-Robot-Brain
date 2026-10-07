"""Tests for orb_apps_simulator.cli."""

from __future__ import annotations

import pytest
from orb_apps_simulator.cli import main


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
