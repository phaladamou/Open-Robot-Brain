# Contributing to Open Robot Brain

Thanks for your interest. This project aims to be a **rigorous, open research
architecture** — contributions are welcome, but they must respect the design
principles and interfaces defined in `docs/`.

---

## Ground Rules

1. **Interfaces before implementations.** New subsystems must first be expressed
   as protocols/interfaces in `packages/interfaces/` and `protocols/`.
2. **No hardware coupling.** `brain/` must never import from `embodiment/` or
   `simulation/` directly. Use capabilities.
3. **Simulation-first.** Every feature must be demonstrable in simulation.
4. **Typed. Tested. Documented.** `ruff` + `mypy --strict` + `pytest` must pass.
5. **One concept per PR.**

---

## Development Setup

make install        # install uv
make sync           # install workspace dependencies
make pre-commit-install
make check          # lint + typecheck + tests

---

## Commit Convention

We follow Conventional Commits:

feat(brain/world-model): add uncertainty field to Object
fix(runtime/executor): handle empty plan gracefully
docs(architecture): clarify embodiment abstraction
refactor(protocols): split Capability into spec/impl
test(skills): add precondition failure case

Scopes typically map to a top-level module:
brain, embodiment, control, perception, runtime, learning,
simulation, models, robots, protocols, packages, infra, docs.

---

## Pull Requests

Before opening a PR:

- [ ] make check passes locally
- [ ] New code is typed and tested
- [ ] Docs updated if behavior/interface changed
- [ ] No new external dependency without justification
- [ ] PR description explains why, not just what

---

## Code of Conduct

Be respectful. Be rigorous. Disagree on ideas, not on people.

---

One brain. Many bodies.
