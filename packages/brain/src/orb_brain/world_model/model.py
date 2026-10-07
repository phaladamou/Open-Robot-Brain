"""World model implementation.

See :mod:`orb_brain.world_model` for the design rationale.
"""

from __future__ import annotations

import structlog
from orb_runtime import EventBus, StateStore
from orb_types import (
    Event,
    EventKind,
    Object,
    Observation,
    ObservationKind,
    WorldState,
    utc_now,
)

logger = structlog.get_logger(__name__)


class WorldModel:
    """Maintains the brain's belief about the world.

    Parameters
    ----------
    bus:
        Event bus. The model subscribes on :meth:`start` and unsubscribes
        on :meth:`stop`.
    store:
        State store whose ``world`` will be updated on each accepted
        observation.
    confidence_threshold:
        Observations whose ``confidence`` is strictly below this value are
        dropped. Defaults to ``0.0`` (accept everything).

    Example
    -------
    >>> model = WorldModel(bus, store)
    >>> model.start()
    >>> model.apply_observation(obs)  # or let the bus deliver it
    >>> model.stop()
    """

    #: ``ObservationKind`` values this model knows how to apply. Others are
    #: ignored with a debug log.
    HANDLED_KINDS: frozenset[ObservationKind] = frozenset(
        {
            ObservationKind.OBJECT_DETECTED,
            ObservationKind.OBJECT_LOST,
            ObservationKind.SCENE,
        }
    )

    def __init__(
        self,
        bus: EventBus,
        store: StateStore,
        *,
        confidence_threshold: float = 0.0,
    ) -> None:
        self._bus = bus
        self._store = store
        self._threshold = float(confidence_threshold)
        self._subscription: object | None = None
        self._running = False

    # ─── Lifecycle ──────────────────────────────────────────────────────

    def start(self) -> None:
        """Subscribe to the event bus. Idempotent."""
        if self._running:
            return
        self._subscription = self._bus.subscribe(
            self._on_event,
            kind=EventKind.OBSERVATION_CREATED,
        )
        self._running = True
        logger.info("world_model.started")

    def stop(self) -> None:
        """Unsubscribe from the event bus. Idempotent."""
        if not self._running:
            return
        if self._subscription is not None:
            self._bus.unsubscribe(self._subscription)  # type: ignore[arg-type]
            self._subscription = None
        self._running = False
        logger.info("world_model.stopped")

    @property
    def running(self) -> bool:
        """Whether the model is currently subscribed."""
        return self._running

    @property
    def confidence_threshold(self) -> float:
        """The confidence threshold below which observations are dropped."""
        return self._threshold

    # ─── Event handling ─────────────────────────────────────────────────

    def _on_event(self, event: Event) -> None:
        """Handle an incoming event.

        In v0.1, the bus carries observations inside the event payload
        under the key ``"observation"``. This indirection is temporary:
        a first-class ``OBSERVATION_CREATED`` event with a typed payload
        will replace it once ``orb_types.Event`` supports typed payloads.
        """
        raw = event.payload.get("observation")
        if not isinstance(raw, Observation):
            logger.debug("world_model.skipped_untyped_observation", event_id=event.event_id)
            return
        self.apply_observation(raw)

    # ─── Core logic ─────────────────────────────────────────────────────

    def apply_observation(self, obs: Observation) -> None:
        """Apply an observation to the world state.

        Behaviour by ``ObservationKind``:

        - ``OBJECT_DETECTED``: if the observation carries an ``object_id``,
          upsert the corresponding :class:`Object` into the world.
        - ``OBJECT_LOST``: if the observation carries an ``object_id``,
          remove the corresponding object from the world.
        - ``SCENE``: no object-level change in v0.1 (reserved).
        - Any other kind: ignored.

        Observations below the configured confidence threshold are dropped.
        """
        if obs.confidence < self._threshold:
            logger.debug(
                "world_model.dropped_low_confidence",
                observation_id=obs.observation_id,
                confidence=obs.confidence,
                threshold=self._threshold,
            )
            return

        if obs.kind not in self.HANDLED_KINDS:
            logger.debug(
                "world_model.skipped_unsupported_kind",
                observation_id=obs.observation_id,
                kind=obs.kind,
            )
            return

        if obs.kind is ObservationKind.OBJECT_DETECTED:
            self._upsert_object(obs)
        elif obs.kind is ObservationKind.OBJECT_LOST:
            self._remove_object(obs)
        # SCENE: reserved, no-op in v0.1

    # ─── Internal ───────────────────────────────────────────────────────

    def _upsert_object(self, obs: Observation) -> None:
        if obs.object_id is None:
            logger.debug(
                "world_model.object_detected_without_object_id",
                observation_id=obs.observation_id,
            )
            return

        new_object = Object(
            object_id=obs.object_id,
            type=obs.payload.get("type", "unknown"),
            pose=obs.pose if obs.pose is not None else _origin_pose(),
            attributes={
                k: str(v)
                for k, v in obs.payload.items()
                if k != "type" and isinstance(v, (str, int, float, bool))
            },
            confidence=obs.confidence,
        )

        current = self._store.world
        existing = current.get_object(obs.object_id)
        if existing is not None:
            objects = tuple(
                new_object if o.object_id == obs.object_id else o for o in current.objects
            )
            action = "replaced"
        else:
            objects = (*current.objects, new_object)
            action = "added"

        self._store.update_world(
            WorldState(
                timestamp=utc_now(),
                objects=objects,
                agents=current.agents,
                locations=current.locations,
                surfaces=current.surfaces,
            ),
            correlation_id=obs.observation_id,
        )
        logger.debug(
            f"world_model.object_{action}",
            object_id=obs.object_id,
            kind=str(obs.kind),
        )

    def _remove_object(self, obs: Observation) -> None:
        if obs.object_id is None:
            return
        current = self._store.world
        if current.get_object(obs.object_id) is None:
            return
        objects = tuple(o for o in current.objects if o.object_id != obs.object_id)
        self._store.update_world(
            WorldState(
                timestamp=utc_now(),
                objects=objects,
                agents=current.agents,
                locations=current.locations,
                surfaces=current.surfaces,
            ),
            correlation_id=obs.observation_id,
        )
        logger.debug("world_model.object_removed", object_id=obs.object_id)


def _origin_pose() -> object:
    from orb_types import Pose

    return Pose.origin()


__all__ = ["WorldModel"]
