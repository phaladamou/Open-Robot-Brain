"""State store for Open Robot Brain.

The :class:`StateStore` is the runtime's single source of truth for:

- the **world state** (what the brain believes about the environment),
- the **robot state** (what the brain believes about its own body).

It is a **passive container**: it does not compute, reconcile, or infer.
Updates are complete-state replacements. Every update publishes an event
on the injected :class:`EventBus` so the rest of the runtime can react.

History is intentionally **not** stored here — that is the role of the
:class:`~orb_runtime.events.log.EventLog`.
"""

from orb_runtime.state.store import StateStore

__all__ = ["StateStore"]
