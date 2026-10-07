"""CLI for the reference simulator app."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from orb_simulation import SCENARIOS
from orb_types import RunResult, RunStatus

from orb_apps_simulator.runner import run_scenario


def _format_summary(result: RunResult) -> str:
    lines: list[str] = []
    lines.append("")
    lines.append("=" * 64)
    lines.append(f"  Scenario : {result.scenario_name}")
    lines.append(f"  Status   : {result.status}")
    lines.append(f"  Duration : {result.duration_s * 1000:.1f} ms")
    if result.goal is not None:
        lines.append(f"  Goal     : {result.goal.description!r}")
        lines.append(f"             kind={result.goal.kind}, predicate={result.goal.predicate}")
    if result.reasoning is not None:
        errs = list(result.reasoning.errors)
        lines.append(
            f"  Reason   : ok={result.reasoning.ok}" + (f", errors={errs}" if errs else "")
        )
    if result.plan is not None:
        lines.append(f"  Plan     : {len(result.plan.steps)} step(s)")
        for step in result.plan.steps:
            params = ", ".join(f"{k}={v}" for k, v in step.parameters.items())
            lines.append(f"             - {step.skill_id}({params})")
    if result.task_result is not None:
        lines.append(f"  Skills   : {len(result.task_result.skill_results)} executed")
        for sr in result.task_result.skill_results:
            lines.append(f"             - {sr.skill_id}: {sr.status}")
    if result.message:
        lines.append(f"  Message  : {result.message}")
    lines.append("=" * 64)
    lines.append("")
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="orb-simulator",
        description="Run an Open Robot Brain scenario end to end.",
    )
    p.add_argument(
        "scenario",
        nargs="?",
        default="pick_red_cube",
        help="Scenario name (default: pick_red_cube).",
    )
    p.add_argument(
        "--list",
        action="store_true",
        help="List available scenarios and exit.",
    )
    return p


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.list:
        print("Available scenarios:")
        for name in SCENARIOS:
            print(f"  - {name}")
        return 0

    result = run_scenario(args.scenario)
    print(_format_summary(result))
    return 0 if result.status is RunStatus.SUCCEEDED else 1


if __name__ == "__main__":
    sys.exit(main())
