# orb-simulation

Simulation backends for Open Robot Brain.

The simulation layer is a **first-class research environment**, not a
development convenience. It provides:

- `environments/` — world configurations (scenes, objects, surfaces)
- `robots/` — robot models (MJCF, URDF) and loaders
- `scenarios/` — named scenarios for benchmarking
- `benchmarks/` — evaluation harnesses (v0.2+)

**Backends:**
- `MockSimulator` — pure-Python, no dependencies, used by default and in CI
- `MujocoAdapter` — MuJoCo-backed, available via the `mujoco` extra:
  `uv sync --extra mujoco`

The mock simulator is fully sufficient for developing and testing the
cognitive pipeline. MuJoCo adds realistic dynamics when needed.
