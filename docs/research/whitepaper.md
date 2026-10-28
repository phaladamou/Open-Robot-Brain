# One Brain. Many Bodies.

> **Status: skeleton.** Each section below lists its sources — the files,
> tests, and numbers the final prose must cite. No claim in the finished
> whitepaper may lack a source from this list.

## 1. Thesis

Robots are bottlenecked by coupling: models, controllers, and skills are
built per-body, so every new robot rebuilds the intelligence stack. ORB
claims the stack splits cleanly — an intelligence layer that reasons
about *objects, goals, skills, capabilities, constraints* and an
embodiment layer that owns the body — and that the split is enforceable
in code, not just asserted in prose.

Sources: `README.md` (Vision, Core Idea), `docs/architecture/principles.md`
§2–§3, `docs/architecture/overview.md` (Core Separation).

## 2. Architecture

How the split is built: layered packages (`types` → `interfaces` →
`runtime`/`brain`/`embodiment`/`simulation` → `apps`), cross-layer
contracts as Protocols/Pydantic models only, the synchronous event bus
as the single async channel, simulation as a first-class backend
(mock default, MuJoCo optional). Include the v0.2 pipeline diagram.

Sources: `README.md` (Architecture, v0.2 Highlights), `packages/*/pyproject.toml`
(dependency directions), `packages/runtime/src/orb_runtime/events/bus.py`,
`packages/simulation/README.md`, `AGENTS.md` (stack, non-negotiables).

## 3. Cross-Embodiment Results

Protocol: same instruction (`pick the red cube`), same pipeline, three
bodies differing by capability set. Report the plan table
(full arm: 4 steps; short arm: 5 steps with approach/dock legs; weak
arm: explicit `missing capability 'can_lift'` refusal), the
reasoner-vs-planner responsibility split, and benchmark numbers
(success rate vs. expected status, mean/p95 durations).

Sources: `packages/embodiment/src/orb_embodiment/adapters/profiles.py`,
`packages/brain/src/orb_brain/planning/htn.py` (`_rule_pick_short_arm`),
`packages/brain/src/orb_brain/reasoning/reasoner.py`,
`packages/simulation/src/orb_simulation/scenarios.py`,
`packages/simulation/src/orb_simulation/benchmarks.py`,
`uv run python -m orb_apps_simulator --benchmark` output,
`docs/architecture/overview.md` (Cross-Embodiment section).

Scale of evidence: 452 tests, 7 scenarios, `mypy --strict` (111 files),
`ruff` clean, CI green on Python 3.11/3.12, `import-linter` + AST
boundary test enforcing brain isolation.

## 4. Limitations & Next Steps

Honest bounds: v0.1 bodies differ by capability set, not geometry;
skills are kinematic, not dynamic; no learning loop yet; no physical
robot. Roadmap: cross-embodiment skill transfer (v0.3), learning loop
(v0.4), first physical adapter (v1.0).

Sources: `README.md` (Roadmap, Non-Goals, Research Directions),
`CHANGELOG.md` (Unreleased as the working list).
