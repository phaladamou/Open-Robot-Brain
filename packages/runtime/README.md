# orb-runtime

Runtime layer for Open Robot Brain.

**Responsibilities:**
- `events/` — event bus, event log, subscriptions
- `state/` — state store (world + robot state coordination)
- `scheduler/` — tick loop, timers, periodic tasks
- `executor/` — plan and skill execution engine
- `communication/` — inter-process communication (v0.2+)

The runtime is **synchronous** in v0.1 for determinism (essential for
simulation and benchmarks). Async support is planned for v0.3+.

The runtime **coordinates** cognitive and embodiment layers. It does not
own intelligence; it owns execution.
