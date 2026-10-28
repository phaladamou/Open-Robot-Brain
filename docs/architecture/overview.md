# Architecture Overview

> **One brain. Many bodies.**

Open Robot Brain is a **layered cognitive architecture** that separates
**intelligence** from **embodiment**.

This document describes the why and the how of the architecture. For the
full vision, see the root README.

---

## The Core Separation

┌─────────────────────────────────────────────────────────┐
│                        BRAIN                            │
│  perception · world-model · memory · reasoning          │
│  planning · skills · decision · learning                │
│                                                         │
│  Knows:  world, goals, skills, capabilities, constraints│
│  Ignores: motors, servos, joints, hardware              │
└───────────────────────┬─────────────────────────────────┘
                        │  capabilities (abstract)
                        ▼
┌─────────────────────────────────────────────────────────┐
│                    EMBODIMENT                           │
│  abstraction · capabilities · kinematics · adapters    │
│                                                         │
│  Knows:  the robot body, its limits, its SDK            │
└───────────────────────┬─────────────────────────────────┘
                        │  concrete commands
                        ▼
┌─────────────────────────────────────────────────────────┐
│                     CONTROL                             │
│  motion · manipulation · navigation · locomotion        │
│  safety                                                 │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
                      ROBOT(S)

Rule: the brain never imports hardware-specific code.
It reasons only in terms of capabilities and skills.

---

## Layers

Layer       | Directory       | Responsibility
------------|-----------------|---------------------------------------------
Brain       | brain/          | High-level cognition — no hardware
Embodiment  | embodiment/     | Abstract capabilities → robot body
Control     | control/        | Physical execution (sim or real)
Perception  | perception/     | Modality processing (vision, depth…)
Runtime     | runtime/        | Orchestration, events, state, scheduling
Learning    | learning/       | Experience → improvement
Simulation  | simulation/     | First-class research environment
Models      | models/         | ML components (vision, language, world, policy)
Robots      | robots/         | Per-robot adapters/definitions
Protocols   | protocols/      | Stable communication contracts
Packages    | packages/       | Shared types, SDK, interfaces
Infra       | infra/          | Docker, deployment
Docs        | docs/           | Architecture, research, safety

---

## Data Flow (v0.1 target)

Goal (natural language)
    │
    ▼
[ reasoning ]  → structured intent
    │
    ▼
[ planning ]   → plan of skills
    │
    ▼
[ skills ]     → capability requests
    │
    ▼
[ embodiment ] → robot-specific actions
    │
    ▼
[ control ]    → commands
    │
    ▼
[ simulation ] → new observation
    │
    ▼
[ world-model ] → updated state
    │
    └──► loop

---

## Cross-Embodiment: Same Brain, Different Bodies, Different Plans

The brain never sees motors — it sees capabilities. That is what makes
"one brain, many bodies" executable rather than aspirational. v0.1 ships
three bodies (`orb_embodiment.adapters.profiles`), all driven by the
same pipeline:

| Body | Differs by | `pick the red cube` |
|---|---|---|
| `mock` (full arm) | reference | 4 steps: navigate → reach → grasp → lift |
| `short_arm` | no `can_reach_far` | 5 steps: navigate → navigate (dock) → reach → grasp → lift |
| `weak_arm` | no `can_lift` | refused: `missing capability 'can_lift'` |

Two layers adapt, with a clean split of responsibility:

- The **reasoner** judges feasibility: a goal the body cannot achieve
  is refused with an explicit error (`pick_red_cube_no_lift`).
- The **planner** adapts strategy: a goal the body can achieve *with
  effort* gets a different decomposition
  (`pick_red_cube_short_arm` succeeds through base repositioning).

v0.1 bodies differ by capability set only; per-robot geometry arrives
with dedicated MuJoCo models.

---

## Design Invariants

These are non-negotiable across the codebase:

1. brain/ must not import from embodiment/, control/, simulation/, robots/.
2. All cross-layer communication goes through protocols/ and packages/interfaces/.
3. protocols/ types are stable and versioned.
4. Simulation is not optional — every feature is demonstrable in sim.
5. Safety is architectural, not a feature flag.

---

## References

- Principles (./principles.md)
- Root README (../../README.md)

---

## Related Work

(to be filled as the project matures)
