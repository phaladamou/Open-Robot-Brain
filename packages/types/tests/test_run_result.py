"""Tests for orb_types.run_result."""

from __future__ import annotations

import pytest
from orb_types import RunResult, RunStatus
from pydantic import ValidationError as PydanticValidationError


def test_run_result_minimal() -> None:
    r = RunResult(
        scenario_name="pick_red_cube",
        status=RunStatus.SUCCEEDED,
        duration_s=0.5,
    )
    assert r.status is RunStatus.SUCCEEDED
    assert r.goal is None
    assert r.plan is None


def test_run_result_with_failure() -> None:
    r = RunResult(
        scenario_name="x",
        status=RunStatus.PARSE_FAILED,
        duration_s=0.001,
        message="could not parse",
    )
    assert r.status is RunStatus.PARSE_FAILED
    assert r.message == "could not parse"


def test_run_result_rejects_negative_duration() -> None:
    with pytest.raises(PydanticValidationError):
        RunResult(scenario_name="x", status=RunStatus.SUCCEEDED, duration_s=-1.0)


def test_run_result_frozen() -> None:
    r = RunResult(scenario_name="x", status=RunStatus.SUCCEEDED, duration_s=0.1)
    with pytest.raises(PydanticValidationError):
        r.status = RunStatus.PARSE_FAILED  # type: ignore[misc]


def test_run_result_serializable() -> None:
    r = RunResult(scenario_name="x", status=RunStatus.SUCCEEDED, duration_s=0.1)
    payload = r.to_dict()
    assert payload["scenario_name"] == "x"
    assert payload["status"] == "succeeded"
