# Design Principles

These principles are **load-bearing**. Every design decision in Open Robot Brain
must be traceable to one of them.

---

## 1. Intelligence before hardware

The system must be useful in simulation before requiring physical robots.
Simulation is not a stepping stone — it is a first-class research environment.

## 2. Brain ≠ Robot

The intelligence layer must remain independent from individual robot
embodiments. brain/ never imports hardware-specific code.

## 3. Abstractions over motor commands

The brain reasons about:

objects · goals · skills · capabilities · constraints

not about:

servo_17 · motor_4 · joint_6

## 4. World model as shared state

Perception, planning, memory, and reasoning operate around a single shared
representation of the world. There is one source of truth.

## 5. Skills are reusable

Skills must be:

- composable — combine into larger behaviors
- verifiable — each has a success criterion
- recoverable — each defines failure handling
- transferable — representable independently of a body

## 6. Simulation is part of the product

Simulation is not a development convenience. It is the primary research
environment and a first-class product surface.

## 7. Safety is architectural

Safety is enforced between intention and physical execution, not as an
optional feature flag.

## 8. Hardware should be replaceable

Changing the robot must not require rebuilding the intelligence stack.
The embodiment layer absorbs hardware differences.

---

## Corollaries

- Interfaces first. Protocols and abstract interfaces are defined before
  implementations.
- No circular imports. Enforced by import-linter.
- Typed everywhere. mypy --strict on brain/, runtime/, protocols/.
- Tested behavior. No untested code in cognitive layers.
- Documented decisions. Architecture changes update docs/architecture/.

---

If a change violates a principle, the principle wins — or the principle is
formally revised in a documented decision.
