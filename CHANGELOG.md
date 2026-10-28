# Changelog

All notable changes to **Open Robot Brain** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

Nothing yet.

---

## [0.2.0] - 2026-10-28

452 tests · 8 packages · 7 scenarios · `ruff` + `mypy --strict` clean ·
CI blocking and green on Python 3.11/3.12.

### Added

- Real MuJoCo backend: `MujocoAdapter` drives a self-contained 6-DOF arm
  (`arm_6dof.xml`) with true dynamics (optional `mujoco` extra; mock
  simulator remains the default).
- Real perception loop: seeded `MockSensor` ticks 3 times before planning;
  `WorldModel` absorbs observations off the event bus into the `StateStore`,
  and `RunResult.observations_applied` reports the count.
- Cross-embodiment: 3 bodies, one brain — full arm (4-step pick), short arm
  (5-step pick with base docking), weak arm (explicit
  `missing capability 'can_lift'` refusal). Two new scenarios
  (`pick_red_cube_no_lift`, `pick_red_cube_short_arm`).
- Capability-aware planning: the `Planner` protocol and `Executor` accept
  body capabilities (backward compatible); pick decomposition adapts to
  missing `can_reach_far`.
- Reproducible benchmark: `benchmark()` harness plus `--benchmark` JSON CLI
  mode (success rate vs. expected status, mean/p95 durations).
- Architecture guard: `import-linter` forbidden contract
  (`orb_brain` → embodiment/simulation/apps) gates CI; an AST boundary test
  covers brain sources and tests on every local `pytest` run.
- `AGENTS.md` onboarding for agents and humans.

### Changed

- CI hardened: ruff, `mypy --strict`, `lint-imports`, and pytest are all
  blocking; `uv.lock` is tracked for reproducible resolution.
- `README.md` refreshed: v0.2 Highlights with pipeline diagram, working
  Quick Start, CI badge, XERJ Corpus Hub selection note.

---

## [0.1.0] - 2026-10-07

First runnable cognitive core: `"pick the red cube"` runs end to end in
simulation with no hardware.

### Added

- Cognitive pipeline: `GoalParser` → `Reasoner` → `HtnPlanner` → `Executor`
  → `InMemorySkillRegistry` (8 skills) → `TaskResult`.
- Reference simulator app (`python -m orb_apps_simulator`) with 5 scenarios.
- World model with event-bus subscription; runtime (`EventBus`,
  `StateStore`, `Executor`, scheduler).
- Simulation layer: `Simulator` protocol, `MockSimulator`, MuJoCo stub,
  named scenarios and environments.
- Embodiment layer: `BaseRobot` abstraction, `FakeRobot` with configurable
  capability sets.
- Shared contracts: `orb-types` (Pydantic v2) and `orb-interfaces`
  (Protocols); `orb-sdk` scaffold.
- ~390 tests, `ruff` + `mypy --strict`, GitHub Actions CI, Apache-2.0
  license, architecture docs (`principles.md`, `overview.md`).

---

[Unreleased]: https://github.com/phaladamou/Open-Robot-Brain/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/phaladamou/Open-Robot-Brain/tree/v0.2.0
[0.1.0]: https://github.com/phaladamou/Open-Robot-Brain/commit/2f03331f75f73efef0a5e555b527206e369bcfec
