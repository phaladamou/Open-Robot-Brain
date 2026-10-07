"""Goal parser: natural language → structured :class:`Goal`.

v0.1 uses deterministic regex rules. This keeps the parser:

- fast,
- dependency-free,
- fully testable,
- reproducible.

The interface is designed so an LLM-based parser can be plugged in later
without changing the public API. Only English is supported in v0.1.
"""

from __future__ import annotations

import re

from orb_types import Goal, GoalId, GoalKind, ObjectId, new_id, utc_now

# ─── Errors ──────────────────────────────────────────────────────────────


class ParseError(ValueError):
    """Raised when a natural-language instruction cannot be parsed."""


# ─── Known colors ────────────────────────────────────────────────────────
#
# The ``color`` capture is restricted to a known list so that it cannot
# accidentally swallow an explicit object identifier (e.g. "cup cup_01").

_COLORS = "red|blue|green|yellow|black|white|orange|purple|pink|brown|gray|grey"

_COLOR_GROUP = f"(?P<color>{_COLORS})"


# ─── Rule table ──────────────────────────────────────────────────────────
#
# Each rule is a (GoalKind, compiled regex) pair. The regex may capture
# named groups: ``object_id``, ``object_type``, ``color``, ``target``,
# ``location``. Rules are tried in order; the first match wins.

_RULES: list[tuple[GoalKind, re.Pattern[str]]] = [
    (
        GoalKind.MANIPULATION,
        re.compile(
            r"^\s*pick\s+(?:up\s+)?(?:the\s+)?"
            r"(?:(?P<color>red|blue|green|yellow|black|white|orange|purple|pink|brown|gray|grey)\s+)?"
            r"(?P<object_type>\w+)"
            r"(?:\s+(?P<object_id>\w+_\w+))?\s*$",
            re.IGNORECASE,
        ),
    ),
    (
        GoalKind.MANIPULATION,
        re.compile(
            r"^\s*place\s+(?:the\s+)?"
            r"(?:(?P<color>red|blue|green|yellow|black|white|orange|purple|pink|brown|gray|grey)\s+)?"
            r"(?P<object_type>\w+)"
            r"\s+(?:on|onto)\s+(?:the\s+)?(?P<target>\w+)\s*$",
            re.IGNORECASE,
        ),
    ),
    (
        GoalKind.NAVIGATION,
        re.compile(
            r"^\s*(?:go|navigate|move)\s+to\s+(?:the\s+)?(?P<location>\w+)\s*$",
            re.IGNORECASE,
        ),
    ),
    (
        GoalKind.MANIPULATION,
        re.compile(
            r"^\s*(?P<action>open|close)\s+(?:the\s+)?(?P<object_type>\w+)\s*$",
            re.IGNORECASE,
        ),
    ),
    (
        GoalKind.PERCEPTUAL,
        re.compile(
            r"^\s*(?:find|look\s+for|locate)\s+(?:the\s+)?"
            r"(?:(?P<color>red|blue|green|yellow|black|white|orange|purple|pink|brown|gray|grey)\s+)?(?P<object_type>\w+)\s*$",
            re.IGNORECASE,
        ),
    ),
]


# ─── Parser ──────────────────────────────────────────────────────────────


class GoalParser:
    """Turn an English instruction into a structured :class:`Goal`.

    Example
    -------
    >>> parser = GoalParser()
    >>> goal = parser.parse("pick the red cup")
    >>> goal.kind
    <GoalKind.MANIPULATION: 'manipulation'>
    >>> goal.args["color"]
    'red'
    """

    def parse(self, instruction: str, *, goal_id: GoalId | None = None) -> Goal:
        """Parse an instruction into a :class:`Goal`.

        Raises
        ------
        ParseError
            If no rule matches the instruction.
        """
        text = instruction.strip()
        if not text:
            msg = "empty instruction"
            raise ParseError(msg)

        for kind, pattern in _RULES:
            match = pattern.match(text)
            if match is None:
                continue
            return self._build_goal(text, kind, match, goal_id=goal_id)

        msg = f"could not parse instruction: {instruction!r}"
        raise ParseError(msg)

    def can_parse(self, instruction: str) -> bool:
        """Return whether the instruction matches any rule."""
        text = instruction.strip()
        if not text:
            return False
        return any(p.match(text) is not None for _, p in _RULES)

    # ─── Internal ───────────────────────────────────────────────────────

    def _build_goal(
        self,
        description: str,
        kind: GoalKind,
        match: re.Match[str],
        *,
        goal_id: GoalId | None,
    ) -> Goal:
        groups = {k: v.lower() for k, v in match.groupdict().items() if v is not None}

        # Normalise capture names into the Goal's structured fields.
        object_type = groups.pop("object_type", None)
        color = groups.pop("color", None)
        object_id_raw = groups.pop("object_id", None)
        target = groups.pop("target", None)
        location = groups.pop("location", None)
        action = groups.pop("action", None)

        predicate: str | None = None
        args: dict[str, str] = {}
        target_object: ObjectId | None = None
        target_location: str | None = None

        if object_type is not None:
            args["object_type"] = object_type
        if color is not None:
            args["color"] = color
        if target is not None:
            args["target"] = target
        if location is not None:
            args["location"] = location
            target_location = location
        if action is not None:
            predicate = action

        # If an explicit identifier was captured, adopt it as the target
        # object. Otherwise leave resolution to the reasoner.
        if object_id_raw is not None:
            target_object = ObjectId(object_id_raw)

        if predicate is None:
            if kind is GoalKind.MANIPULATION:
                predicate = "pick" if "place" not in description.lower() else "place"
            elif kind is GoalKind.NAVIGATION:
                predicate = "at"
            elif kind is GoalKind.PERCEPTUAL:
                predicate = "known"

        return Goal(
            goal_id=goal_id if goal_id is not None else GoalId(new_id("goal")),
            description=description,
            kind=kind,
            predicate=predicate,
            args=args,
            target_object=target_object,
            target_location=target_location,
            created_at=utc_now(),
        )


__all__ = ["GoalParser", "ParseError"]
