# orb-brain

Cognitive core for Open Robot Brain.

**Responsibilities:**
- `world_model/` — maintains the brain's belief about the world
- `reasoning/` — interprets goals and world state
- `planning/` — turns goals into plans
- `skills/` — implements reusable skills
- `memory/` — episodic, semantic, and skill memory
- `decision/` — selects between candidate actions
- `learning/` — improves from experience

The brain is **body-agnostic**. It reasons over **capabilities**, never
over motors, servos, or joints. It reads and writes state exclusively
through the `StateStore`, and communicates with the rest of the system
exclusively through the `EventBus`.
