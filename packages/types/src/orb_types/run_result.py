"""RunResult — the outcome of running a scenario end to end."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from orb_types.base import ORBModel
from orb_types.goal import Goal
from orb_types.plan import Plan
from orb_types.reasoning import ReasoningResult
from orb_types.task_result import TaskResult


class RunStatus(StrEnum):
    SUCCEEDED = "succeeded"
    PARSE_FAILED = "parse_failed"
    REASONING_FAILED = "reasoning_failed"
    EXECUTION_FAILED = "execution_failed"


class RunResult(ORBModel):
    scenario_name: str
    status: RunStatus
    duration_s: float = Field(ge=0.0)
    goal: Goal | None = None
    reasoning: ReasoningResult | None = None
    plan: Plan | None = None
    task_result: TaskResult | None = None
    message: str | None = None


__all__ = ["RunResult", "RunStatus"]
