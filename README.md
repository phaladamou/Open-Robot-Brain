<!--
╔══════════════════════════════════════════════════════════════════╗
║                      OPEN ROBOT BRAIN                            ║
║                    One brain. Many bodies.                       ║
╚══════════════════════════════════════════════════════════════════╝
-->

<h1 align="center">Open Robot Brain</h1>

<p align="center">
  <strong>One brain. Many bodies.</strong><br/>
  <em>An open cognitive architecture that separates intelligence from embodiment.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-early%20research-orange" alt="Status"/>
  <img src="https://img.shields.io/badge/license-Apache%202.0-blue" alt="License"/>
  <img src="https://img.shields.io/badge/python-3.11+-blue" alt="Python"/>
  <img src="https://img.shields.io/badge/sim-MuJoCo%20%7C%20Isaac%20Lab-green" alt="Simulation"/>
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen" alt="PRs"/>
</p>

<p align="center">
  <a href="#vision">Vision</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#roadmap">Roadmap</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#related-work">Related Work</a> •
  <a href="#contributing">Contributing</a>
</p>

---

## Vision

> **Build one brain that can operate different robots.**

Today's robots are tightly coupled to their hardware. A model, a controller, a skill, or an application is often designed for one robot, one sensor configuration, or one actuator layout.

**Open Robot Brain** explores another architecture: a cognitive layer that understands the **world, goals, skills, capabilities, and constraints**, while an **embodiment layer** handles the body.

The fundamental architectural principle:

> **The Brain does not know the robot.  
> It knows the world, goals, capabilities, skills, and constraints.**  
> The embodiment layer knows the robot.

```text
                    HUMAN
                      │
                      ▼
                   GOAL
                      │
                      ▼
              ┌───────────────┐
              │   REASONING   │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │    PLANNER    │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │    SKILLS     │
              └───────┬───────┘
                      │
                      ▼
          ┌───────────────────────┐
          │   EMBODIMENT LAYER    │
          └───────────┬───────────┘
                      │
             ┌────────┼────────┐
             ▼        ▼        ▼
          Robot A  Robot B  Robot C
             │        │        │
             └────────┼────────┘
                      │
                      ▼
                 REAL WORLD
                      │
                      ▼
                 PERCEPTION
                      │
                      ▼
                WORLD MODEL
                      │
                      ▼
                    MEMORY
                      │
                      ▼
                  LEARNING
```

---

## Core Idea

Open Robot Brain treats robotics as a **layered intelligence problem**.

A high-level instruction such as:

```text
"Pick up the red cup."
```

should not immediately become motor commands. The system should reason about:

1. What is the cup?
2. Where is it?
3. Can it be reached?
4. Which robot is being used?
5. Can this robot grasp it?
6. Which manipulation strategy should be used?
7. What constraints exist?
8. How should success be verified?
9. What should happen if the action fails?

The resulting execution might look like:

```text
Goal
 │
 ▼
Find object
 │
 ▼
Identify red cup
 │
 ▼
Estimate position
 │
 ▼
Check capabilities
 │
 ▼
Plan approach
 │
 ▼
Reach
 │
 ▼
Grasp
 │
 ▼
Verify grasp
 │
 ▼
Update world model
 │
 ▼
Store experience
```

The same semantic task should be executable by different robots through different **embodiment adapters**.

---

## Architecture

```text
open-robot-brain/
│
├── apps/
│   ├── simulator/
│   ├── dashboard/
│   └── teleoperation/
│
├── brain/
│   ├── perception/
│   ├── world-model/
│   ├── memory/
│   ├── reasoning/
│   ├── planning/
│   ├── skills/
│   ├── decision/
│   └── learning/
│
├── embodiment/
│   ├── abstraction/
│   ├── capabilities/
│   ├── kinematics/
│   ├── calibration/
│   └── adapters/
│
├── control/
│   ├── motion/
│   ├── manipulation/
│   ├── navigation/
│   ├── locomotion/
│   └── safety/
│
├── perception/
│   ├── vision/
│   ├── depth/
│   ├── audio/
│   ├── tactile/
│   └── sensors/
│
├── runtime/
│   ├── executor/
│   ├── scheduler/
│   ├── events/
│   ├── state/
│   └── communication/
│
├── learning/
│   ├── demonstrations/
│   ├── reinforcement/
│   ├── imitation/
│   ├── skill-learning/
│   └── evaluation/
│
├── simulation/
│   ├── environments/
│   ├── robots/
│   ├── scenarios/
│   └── benchmarks/
│
├── models/
│   ├── vision/
│   ├── language/
│   ├── world/
│   └── policy/
│
├── robots/
│   ├── robot-a/
│   ├── robot-b/
│   └── robot-c/
│
├── protocols/
│   ├── messages/
│   ├── actions/
│   ├── observations/
│   └── capabilities/
│
├── packages/
│   ├── types/
│   ├── sdk/
│   └── interfaces/
│
├── infra/
│   ├── docker/
│   └── deployment/
│
└── docs/
    ├── architecture/
    ├── embodiment/
    ├── skills/
    ├── safety/
    └── research/
```

### Overview

| Layer | Role |
|---|---|
| `brain/` | High-level intelligence — perception, world model, memory, reasoning, planning, skills, decision, learning |
| `embodiment/` | Abstract capability layer — maps brain intentions to robot-specific abilities |
| `control/` | Physical execution — motion, manipulation, navigation, locomotion, safety |
| `perception/` | Sensor modality processing — vision, depth, audio, tactile, sensors |
| `runtime/` | Orchestration — executor, scheduler, events, state, communication |
| `learning/` | Experience and improvement — demos, RL, imitation, skill learning, evaluation |
| `simulation/` | First-class research environment — envs, robots, scenarios, benchmarks |
| `models/` | Vision, language, world, policy models (components, not the architecture) |
| `robots/` | Per-robot adapters (Robot A, B, C, …) |
| `protocols/` | Stable communication contracts — messages, actions, observations, capabilities |
| `packages/` | Shared types, SDK, interfaces |
| `infra/` | Docker, deployment |
| `docs/` | Architecture, embodiment, skills, safety, research |

---

## 1. Brain

The `brain/` directory contains the **high-level intelligence** of the system. It must remain as independent as possible from specific robot hardware.

### Perception

Transforms raw sensor information into meaningful observations.

```text
camera frame
    ↓
object detection
    ↓
object identity
    ↓
position
    ↓
uncertainty
```

Perception never directly controls the robot. It produces information for the world model.

### World Model

The internal representation of the environment.

```json
{
  "object": "cup_01",
  "type": "cup",
  "color": "red",
  "position": [1.2, 0.4, 0.8],
  "confidence": 0.94
}
```

Contains: objects, agents, locations, surfaces, obstacles, robot state, relationships, tasks, uncertainty, temporal information.

---

## 2. Memory

Robots need more than short-term perception. Open Robot Brain separates memory into different forms.

- **Episodic memory** — what happened.
  ```text
  At 14:32:
  robot attempted to open drawer_02.
  The first grasp failed. The second attempt succeeded.
  ```
- **Semantic memory** — what the system knows.
  ```text
  Drawer handles are usually located near the upper edge.
  ```
- **Skill memory** — how to perform tasks.
  ```text
  open_drawer(), pick_object(), place_object(), navigate_to()
  ```

Experience becomes reusable knowledge.

---

## 3. Reasoning

The reasoning layer interprets goals and world state.

```text
Goal: "Bring me the bottle."
```

Reasoning may determine: bottle exists, bottle is on table, table is reachable, robot can manipulate bottle, destination is known.

Reasoning produces **structured decisions**, not uncontrolled low-level actions.

---

## 4. Planning

Planning transforms goals into executable skills.

```text
Goal: Move the bottle to the kitchen.

Plan:
 1. Locate bottle
 2. Navigate to bottle
 3. Reach bottle
 4. Grasp bottle
 5. Navigate to kitchen
 6. Release bottle
 7. Verify placement
```

The planner works with **semantic skills**, not individual motor commands.

---

## 5. Skills

Skills are reusable units of robotic behavior.

```text
navigate_to(), reach(), grasp(), release(),
open(), close(), pick(), place(), inspect(), follow()
```

A skill defines:

```text
Skill
 ├── Preconditions
 ├── Parameters
 ├── Execution
 ├── Verification
 └── Recovery
```

Example:

```text
pick(object)

Preconditions: object detected, reachable, suitable gripper
Execution:     approach → align → grasp → lift
Verification:  object attached, expected weight, position changed
Recovery:      reposition → retry → alternate grasp → abort safely
```

---

## 6. Embodiment Layer

One of the most important parts of Open Robot Brain. The brain operates in terms of **abstract capabilities**.

```text
can_navigate, can_manipulate, can_grasp,
can_lift, can_rotate, can_speak, can_see
```

Different robots expose different capabilities:

```text
Robot A                  Robot B
Navigation   ✓           Navigation   ✓
Arm          ✓           Arm          ✓
Gripper      ✓           Gripper      ✓
Vision       ✓           Vision       ✓
Humanoid     ✗           Humanoid     ✓
```

The brain does **not** understand servos or actuators:

```text
Brain
"grasp object"
       │
       ▼
Capability system
       │
       ▼
Robot-specific adapter
       │
       ▼
Hardware
```

This is the separation between **intelligence** and **embodiment**.

---

## 7. Robot Adapters

Every supported robot provides an adapter translating between the common Open Robot Brain interface and the robot's native SDK or middleware.

```text
Open Robot Brain
       │
       ▼
Robot Interface
       │
 ┌─────┼─────┐
 ▼     ▼     ▼
Robot A Robot B Robot C
```

The goal is not to force every robot to use the same hardware, but to provide a **common intelligence interface**.

---

## 8. Control

```text
control/
├── motion/
├── manipulation/
├── navigation/
├── locomotion/
└── safety/
```

- **Motion** — trajectory generation and execution
- **Manipulation** — arm and gripper control
- **Navigation** — movement through an environment
- **Locomotion** — walking, driving, balancing
- **Safety** — physical constraints and emergency handling

---

## 9. Safety

Safety is not optional. It sits between intention and physical execution.

```text
Brain → Intent → Safety Layer → Controller → Robot

Safety Layer:
  ├── joint limits
  ├── collision checks
  ├── force limits
  ├── velocity limits
  ├── restricted zones
  └── emergency stop
```

A valid high-level plan should still be **rejected** if executing it would violate physical or safety constraints.

---

## 10. Perception

```text
perception/
├── vision/
├── depth/
├── audio/
├── tactile/
└── sensors/
```

Possible inputs: RGB cameras, depth cameras, LiDAR, microphones, force sensors, touch sensors, IMUs, joint encoders. Perception converts these signals into **observations** that update the world model.

---

## 11. Runtime

```text
runtime/
├── executor/
├── scheduler/
├── events/
├── state/
└── communication/
```

The system is designed around an **event-driven execution loop**:

```text
Sensor Event → Perception → World Model Update → Reasoning
     → Planning → Skill Execution → Control → Robot
     → New Observation → World Model Update → …
```

A continuous **perception–action loop**.

---

## 12. Learning

```text
learning/
├── demonstrations/
├── reinforcement/
├── imitation/
├── skill-learning/
└── evaluation/
```

Sources: human demonstrations, simulation, teleoperation, successful/failed executions, RL, imitation, synthetic data. The long-term goal is **reusable skills across embodiments**.

---

## 13. Skill Transfer

Suppose Robot A learns `open_drawer()`. The system should not store only raw motor trajectories. It represents the skill **semantically**:

```text
1. identify handle
2. approach handle
3. establish grasp
4. pull along drawer axis
5. verify drawer opened
```

Robot B may use a different arm, gripper, and kinematics. The embodiment layer translates the semantic skill into Robot B's capabilities.

```text
             open_drawer()
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
       Robot A              Robot B
          │                   │
     Adapter A           Adapter B
          │                   │
    Motor commands       Motor commands
```

This is the foundation for **cross-robot skill transfer**.

---

## 14. Simulation

Simulation is a **first-class component** of the project.

```text
simulation/
├── environments/
├── robots/
├── scenarios/
└── benchmarks/
```

Enables: rapid experimentation, reproducible tests, large-scale evaluation, RL, skill testing, failure analysis, multi-robot experiments.

> **The first goal is not to build a physical robot.  
> The first goal is to build a brain capable of operating robots.**

---

## 15. Models

```text
models/
├── vision/
├── language/
├── world/
└── policy/
```

- **Vision models** — understanding visual observations
- **Language models** — interpreting human instructions and reasoning about tasks
- **World models** — predicting environment dynamics and future states
- **Policy models** — producing actions or action candidates

Models are **components** of the architecture, not the architecture itself.

---

## 16. Protocols

```text
protocols/
├── messages/
├── actions/
├── observations/
└── capabilities/
```

Define how components communicate: `Observation`, `Action`, `Goal`, `Skill`, `Capability`, `RobotState`, `WorldState`, `Task`, `Event`. The protocol layer should remain **stable** even as individual implementations change.

---

## 17. SDK

External developers and researchers interact with the system through a simple API.

```python
brain = RobotBrain(robot)

brain.observe()

brain.execute(
    "pick",
    object="red_cup"
)
```

```python
robot.capabilities()
# navigation, manipulation, vision, grasping, speech
```

> The exact API is expected to evolve as the architecture matures.

---

## 18. Teleoperation

```text
apps/teleoperation/
```

A demonstration can become training data:

```text
Human demonstration
        ↓
Observation sequence
        ↓
Action sequence
        ↓
Skill representation
        ↓
Learning
        ↓
Reusable skill
```

A bridge between **human expertise** and **robot learning**.

---

## 19. Dashboard

```text
apps/dashboard/
```

Views: World, Robot state, Current task, Active plan, Current skill, Sensor streams, Memory, Events, Errors, Safety state, Performance.

> A researcher should be able to understand **what the robot believes and why it is acting**.

---

## 20. Example Execution

> "Put the blue box on the table."

```text
Human
 │
 ▼
Natural language
 │
 ▼
Goal parser
 │
 ▼
"place blue_box on table"
 │
 ▼
World Model  { blue_box, table, robot }
 │
 ▼
Capability check
 │
 ▼
Planner
 │
 ▼
Plan
 ├── locate(box)
 ├── navigate_to(box)
 ├── grasp(box)
 ├── navigate_to(table)
 ├── place(box, table)
 └── verify()
 │
 ▼
Safety → Embodiment Adapter → Robot Controller → Robot
 │
 ▼
Environment → Sensors → World Model
```

If the grasp fails:

```text
grasp() → verification → FAILED → recovery → new grasp strategy → retry
```

> The system should not simply stop because the first action failed.

---

## Design Principles

1. **Intelligence before hardware** — the system must be useful in simulation before requiring physical robots.
2. **Brain ≠ Robot** — the intelligence layer stays independent from individual embodiments.
3. **Abstractions over motor commands** — reason about *objects, goals, skills, capabilities, constraints*, not `servo_17`, `motor_4`, `joint_6`.
4. **World model as shared state** — perception, planning, memory, reasoning operate around a shared representation of the world.
5. **Skills are reusable** — composable, verifiable, recoverable, transferable.
6. **Simulation is part of the product** — not a development convenience, a research environment.
7. **Safety is architectural** — enforced before physical execution.
8. **Hardware should be replaceable** — changing the robot must not require rebuilding the intelligence stack.

---

## Roadmap

| Version | Milestone | Status |
|---|---|---|
| **v0.1** | Cognitive core (world model, reasoning, planning, skills, memory, runtime) + 1 simulated robot | 🚧 In progress |
| **v0.2** | Multi-embodiment — same goal, 2+ simulated robots through the same interface | ⏳ Planned |
| **v0.3** | Cross-embodiment skill transfer — `open_drawer()` from Robot A → Robot B | ⏳ Planned |
| **v0.4** | Learning loop — demonstrations, imitation, first skill learning pipeline | ⏳ Planned |
| **v0.5** | Benchmark suite + evaluation harness | ⏳ Planned |
| **v1.0** | Physical robot adapter (first real embodiment) | ⏳ Planned |

---

## Quick Start

> ⚠️ **Under construction.** The first runnable demo targets **v0.1**.
> In the meantime, you can clone the repo and explore the architecture and docs.

```bash
git clone https://github.com/phaladamou/Open-Robot-Brain.git
cd Open-Robot-Brain
```

```text
Coming soon:
  make install
  make demo
```

---

## Related Work

Open Robot Brain sits at the intersection of robotics middleware, foundation models, and cognitive architectures. It is **complementary** to — not a replacement for — the following:

| Project | Focus | Relationship |
|---|---|---|
| **ROS 2** | Robotics middleware | Provides transport, no cognitive layer |
| **MuJoCo / Isaac Lab / PyBullet** | Simulators | Used as simulation backends |
| **LeRobot** (HuggingFace) | Robot learning | Learning pipelines, robot-specific |
| **OpenVLA / π0 / RT-2** | VLA foundation models | Candidate policy/vision models inside `models/` |
| **Skild AI / Physical Intelligence** | Foundation models (closed) | Shared thesis (robot-agnostic), different scope (closed, model-first) |
| **Open Robot Brain** | **Open cognitive architecture** | **Robot-agnostic, brain-first, simulation-first** |

---

## Research Directions

- **World Models** — maintaining useful internal models of dynamic environments
- **General-Purpose Skills** — reusable across tasks and embodiments
- **Skill Transfer** — knowledge from one robot to another
- **Long-Term Memory** — remembering over weeks, months, years
- **Continual Learning** — improving without forgetting
- **Planning** — long-horizon tasks in uncertain environments
- **Embodied Reasoning** — reasoning that respects physical constraints
- **Multimodal Intelligence** — vision, language, audio, touch, proprioception
- **Simulation-to-Real** — how much intelligence can be developed in simulation
- **Collective Robotics** — multiple robots sharing skills, world knowledge, experience

---

## Non-Goals

Open Robot Brain is **not**:

- a single robot product
- a simple chatbot controlling a robot
- a collection of disconnected robotics scripts
- a wrapper around one model
- a robot-specific control stack
- a replacement for low-level motor controllers
- a hardware-first project

The project focuses on the **intelligence layer between high-level goals and robotic embodiment**.

---

## Long-Term Vision

A world where robotic intelligence is **not locked inside individual machines**.

- A skill learned by one robot becomes available to another.
- A world model persists beyond a single session.
- A robot acquires new capabilities without replacing its entire software stack.
- Different physical bodies share the same underlying intelligence architecture.

```text
                 OPEN ROBOT BRAIN
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
     Robot A         Robot B         Robot C
        │               │               │
        ▼               ▼               ▼
      Body             Body            Body
```

> **The body becomes an embodiment.  
> The intelligence becomes a platform.**

---

## Status

🚧 **Early research / experimental**

The architecture is developed incrementally, beginning with simulation and software infrastructure before physical hardware integration.

---

## Citation

If you use Open Robot Brain in academic work, please cite:

```bibtex
@misc{openrobotbrain2026,
  title        = {Open Robot Brain: An Open Cognitive Architecture for Robot-Agnostic Intelligence},
  author       = {Adamou, Phal},
  year         = {2026},
  howpublished = {\url{https://github.com/phaladamou/Open-Robot-Brain}},
  note         = {Early research project}
}
```

---

## Contributing

Contributions are welcome.

Areas of interest:

```text
robotics · embodied AI · world models · perception · planning
simulation · reinforcement learning · imitation learning
robot control · skill learning · safety · robot interfaces
distributed robotics
```

Before implementing a new subsystem, please review the architecture and design principles in `docs/`.

**Workflow**

1. Open an issue describing the subsystem or change.
2. Align on the interface (`protocols/`, `packages/interfaces/`).
3. Submit a focused PR — one subsystem at a time.

---

## License

Licensed under the **Apache License 2.0** — see [`LICENSE`](LICENSE) for details.

---

## Author

**Phal Adamou**
GitHub: [@phaladamou](https://github.com/phaladamou)

---

<p align="center">
  <strong>One brain. Many bodies.</strong><br/>
  <em>Perceive. Reason. Plan. Act. Learn. Transfer.</em>
</p>