# orb-embodiment

Embodiment layer for Open Robot Brain.

The embodiment layer is the **bridge** between the brain and physical (or
simulated) robots. The brain reasons over **capabilities**; the
embodiment layer exposes them and translates requests into robot-native
commands.

**Responsibilities:**
- `abstraction/` — `BaseRobot`, `CapabilitySet` conventions
- `capabilities/` — capability declarations and lookup helpers
- `kinematics/` — forward and inverse kinematics (v0.2+)
- `calibration/` — sensor and actuator calibration (v0.2+)
- `adapters/` — per-robot adapters (`FakeRobot`, MuJoCo, ROS 2, …)

The embodiment layer **never** imports from `brain/`. The dependency
arrow goes the other way: brain ← embodiment ← runtime.
