# One Brain. Many Bodies.

**Open Robot Brain — Research Whitepaper, v0.2 (October 2026)**

*Status: living document. Every empirical claim below traces to a
listed artifact (source file, test, or reproducible command). Claims
without a traceable artifact do not belong in this paper.*

## Abstract

Robots are bottlenecked by coupling: models, controllers, and skills
are built per-body, so each new robot rebuilds the intelligence stack.
Open Robot Brain (ORB) tests the thesis that the stack splits cleanly
into an intelligence layer — reasoning about objects, goals, skills,
capabilities, and constraints — and an embodiment layer that owns the
body. This paper states the thesis (§1), describes the architecture
that enforces it (§2), and reports the v0.2 cross-embodiment results:
one unchanged brain driving three simulated bodies, producing two
distinct successful plans plus one explicit refusal (§3). We close with
honest limitations and next steps (§4).

## 1. Thesis

The dominant practice in robotics couples intelligence to hardware. A
policy, a controller, or a skill is typically designed for one robot,
one sensor configuration, or one actuator layout; porting it means
re-engineering it. The research community has attacked this coupling
from the model side (vision-language-action foundation models) and
from the middleware side (ROS 2 transport, simulators). ORB attacks it
from the architecture side, with a single falsifiable claim:

> **A cognitive layer that reasons only about capabilities — never
> about actuators — can drive multiple bodies through the same
> interface, with per-body differences absorbed below the
> intelligence layer.**

"Capabilities" here means practical predicates (`can_grasp`,
`can_lift`, `can_reach_far`, …), not hardware handles. The thesis
fails if a new body requires changes to the brain's reasoning,
planning, or skill layers rather than to capability declarations and
embodiment adapters. Non-goals are explicit: ORB is not a middleware,
not a simulator, and not a foundation model
(`README.md`: Related Work, Non-Goals). It is the missing cognitive
layer, developed simulation-first so that every claim is reproducible
without hardware (`docs/architecture/principles.md` §1, §6).

## 2. Architecture

ORB is a layered Python monorepo (uv workspace, 8 packages) with
strictly one-directional dependencies:
`types` → `interfaces` → `runtime` / `brain` / `embodiment` /
`simulation` → `apps` (`packages/*/pyproject.toml`, `AGENTS.md`).
Two rules carry the thesis into code. First, cross-layer contracts
pass only through `packages/interfaces/` (Protocols: `Planner`,
`Simulator`, `SkillRegistry`, `CapabilityProvider`) or
`packages/types/` (immutable Pydantic v2 models); implementations are
never imported across a boundary. Second, `brain/` never imports
embodiment, simulation, control, robots, or apps code — enforced
twice, by an `import-linter` forbidden contract gating CI and by an
AST boundary test (`packages/runtime/tests/test_architecture.py`)
running on every local `pytest` invocation.

The runtime substrate is deliberately boring: a synchronous,
deterministic event bus — the only async channel between components —
plus a `StateStore` holding the single shared `WorldState`
(`packages/runtime/src/orb_runtime/events/bus.py`,
`.../state/store.py`). The v0.2 pipeline, executed per scenario, is:

```text
"pick the red cube"
       │
       ▼
┌────────────┐  3 seeded ticks   ┌────────────┐
│ MockSensor │ ── observations ─▶ │ WorldModel │ ──▶ StateStore.world
└────────────┘    (event bus)    └────────────┘          │
                                                        ▼
            GoalParser → Reasoner → HtnPlanner → Executor → skills
```

Perception is real in structure: a seeded sensor (`MockSensor`,
`packages/simulation/src/orb_simulation/sensors.py`) emits noisy
`OBJECT_DETECTED` observations that the world model absorbs off the
bus, so reasoning and planning operate on perceived state rather than
scenario ground truth. Simulation is a first-class backend behind the
`Simulator` protocol — a pure-Python `MockSimulator` by default, a
real-dynamics `MujocoAdapter` (self-contained 6-DOF arm,
`packages/simulation/robots/arm_6dof.xml`) behind the optional
`mujoco` extra.

## 3. Cross-Embodiment Results

**Protocol.** One fixed instruction (`pick the red cube`), one fixed
pipeline, three bodies differing only by capability set
(`packages/embodiment/src/orb_embodiment/adapters/profiles.py`).
Each scenario declares its body via `robot_id`; the runner resolves
capabilities and forwards them to the executor and planner. Success
is defined per scenario as reaching its declared `expected_status`,
so a correct refusal counts as a pass
(`packages/simulation/src/orb_simulation/scenarios.py`,
`packages/simulation/src/orb_simulation/benchmarks.py`).

**Plans.** The same brain produces three outcomes, splitting
responsibility across two layers:

| Body | Capabilities | Outcome |
|---|---|---|
| `mock` (full arm) | reference set incl. `can_lift`, `can_reach_far` | 4 steps: navigate → reach → grasp → lift |
| `short_arm` | no `can_reach_far` | 5 steps: navigate (approach) → navigate (dock) → reach → grasp → lift |
| `weak_arm` | no `can_lift` | refused: `missing capability 'can_lift'` |

The **reasoner** judges feasibility: goals the body cannot achieve are
refused with an explicit error before planning
(`packages/brain/src/orb_brain/reasoning/reasoner.py`,
scenario `pick_red_cube_no_lift`). The **planner** adapts strategy:
goals achievable with effort get a different decomposition — the
short arm routes through base repositioning because it cannot reach
from the approach pose
(`packages/brain/src/orb_brain/planning/htn.py::_rule_pick_short_arm`,
scenario `pick_red_cube_short_arm`). Custom planner rules are never
overridden by the adaptation (guarded and tested).

**Benchmark.** `uv run python -m orb_apps_simulator --benchmark` runs
all 7 scenarios 5 times each and prints sorted, diffable JSON. At
v0.2.0, all scenarios reach their expected status on every run
(success rate 1.0). Per-run durations are single-digit milliseconds
on a standard development machine; we report them as orders of
magnitude, not records — wall time is inherently noisy, while
outcomes are bit-deterministic (fixed seeds, synchronous bus, no
unseeded randomness anywhere in the pipeline).

**Scale of evidence.** 452 tests, 7 scenarios, `mypy --strict` clean
(111 files), `ruff` clean, CI blocking and green on Python 3.11/3.12,
brain isolation enforced by contract plus test. Reproduce with:

```bash
uv sync --all-packages
uv run pytest packages -q
uv run python -m orb_apps_simulator --benchmark
```

## 4. Limitations & Next Steps

What v0.2 does **not** claim. Bodies differ by capability set, not by
geometry — per-robot morphology (arm lengths, mobile bases) arrives
with dedicated MuJoCo models. Skills are kinematic: they validate
preconditions and report success but do not yet close the loop
through real dynamics. There is no learning loop, no memory beyond
the world state, and no physical robot. The benchmark measures a
deterministic pipeline on millisecond timescales; it is a regression
instrument, not a robotics leaderboard.

The roadmap follows the thesis outward (`README.md`: Roadmap).
v0.3 targets cross-embodiment skill transfer (a skill learned on one
body executing on another); v0.4 a learning loop from demonstrations;
v1.0 the first physical adapter — the experiment the whole
architecture exists to enable: unplug the simulator, keep the brain.

## Artifact Index

Thesis & principles: `README.md`, `docs/architecture/principles.md`,
`docs/architecture/overview.md` (incl. Cross-Embodiment section).
Bodies & refusal: `adapters/profiles.py`, `reasoning/reasoner.py`,
`scenarios.py`. Adaptive planning: `planning/htn.py`,
`orb_interfaces/planner.py`, `orb_runtime/executor/executor.py`.
Perception: `orb_simulation/sensors.py`,
`orb_brain/world_model/model.py`, `orb_apps_simulator/runner.py`.
Benchmark: `orb_simulation/benchmarks.py`, `--benchmark` CLI.
Enforcement: `[tool.importlinter]` in `pyproject.toml`, `.github/workflows/ci.yml`,
`packages/runtime/tests/test_architecture.py`.
History: `CHANGELOG.md`, tag `v0.2.0`.
