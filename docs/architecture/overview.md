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
