# AGENTS.md — Onboarding (agents IA & humains)

## Vision

**One brain. Many bodies.** Open Robot Brain is a robot-agnostic cognitive
architecture: one intelligence layer (world, goals, skills, capabilities,
constraints) driving many robot bodies through replaceable embodiment
adapters.

## Current state (v0.2 in progress)

Done:

- v0.1 pipeline end to end: `"pick the red cube"` → GoalParser → Reasoner →
  HtnPlanner → Executor → InMemorySkillRegistry (8 skills) → SUCCEEDED.
- 5 scenarios green (`pick_red_cube`, `pick_blue_cube`,
  `pick_cube_among_many`, `open_drawer`, `place_cube_on_table`).
- ~400 tests, ruff + `mypy --strict` clean, CI blocking and green on
  Python 3.11/3.12 (`uv.lock` tracked).
- Real MuJoCo backend: `MujocoAdapter` + self-contained `arm_6dof.xml`
  (optional `mujoco` extra, tests skip without it).

In progress: perception loop (noisy `MockSensor` → bus → `WorldModel` →
`StateStore`) wired into the simulator runner.

Remaining: cross-embodiment second robot, reproducible benchmark CLI.

## Stack

uv workspace · Python 3.11+ · Pydantic v2 · ruff (lint + format) ·
`mypy --strict` · pytest · structlog · MuJoCo (optional extra only).

## Non-negotiables

1. `brain/` never imports `embodiment/`, `simulation/`, `control/`,
   `robots/`, or `apps/`. Enforced by test.
2. Cross-layer contracts go through `packages/interfaces/` (Protocols) or
   `packages/types/` (Pydantic models). Never import an implementation
   across an architectural boundary.
3. Simulation-first: zero heavy dependencies in CI; every demo runs with
   no hardware. Optional deps use `pytest.importorskip` (SKIPPED, never
   FAILED, without the extra).
4. Every new module: `mypy --strict` clean, pytest-covered, short
   numpy-style docstrings (+ README if complex). Immutable types by
   default, typed `ORBError` hierarchy, public tuples.
5. Total determinism: no sleep, no network, no unseeded randomness, no
   flakiness. A test passing once passes 1000 times.

Load-bearing docs: `docs/architecture/principles.md`,
`docs/architecture/overview.md`. If a change violates a principle, the
principle wins.

## Canonical commands

```bash
uv sync --all-packages          # default env (no heavy deps)
uv run ruff check .
uv run ruff format --check .
uv run mypy packages
uv run pytest packages -q
uv run python -m orb_apps_simulator          # demo: 5 scenarios
uv sync --all-packages --extra mujoco       # real-dynamics env
uv run pytest packages -q                   # (mujoco tests run, not skip)
```

Every commit must leave all of the above green. Conventional Commits,
one concept per commit, WHY-first messages.

## Immediate roadmap

1. **Perception loop** (current): `MockSensor` + `WorldModel` ticks in
   runner + integration tests.
2. **Cross-embodiment**: second simulated body, capability-gated
   scenarios, "same brain, different plans" doc.
3. **Benchmark**: reproducible `benchmark()` + `--benchmark` JSON CLI.
