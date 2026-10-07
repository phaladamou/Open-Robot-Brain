"""Tests for orb_brain.reasoning.goal_parser."""

from __future__ import annotations

import pytest
from orb_brain.reasoning.goal_parser import GoalParser, ParseError
from orb_types import GoalKind


@pytest.fixture
def parser() -> GoalParser:
    return GoalParser()


# ─── Pick ────────────────────────────────────────────────────────────────


def test_pick_simple(parser: GoalParser) -> None:
    g = parser.parse("pick the cup")
    assert g.kind is GoalKind.MANIPULATION
    assert g.args.get("object_type") == "cup"


def test_pick_with_color(parser: GoalParser) -> None:
    g = parser.parse("pick the red cup")
    assert g.args.get("color") == "red"
    assert g.args.get("object_type") == "cup"


def test_pick_with_up(parser: GoalParser) -> None:
    g = parser.parse("pick up the red cup")
    assert g.args.get("color") == "red"


def test_pick_with_explicit_id(parser: GoalParser) -> None:
    g = parser.parse("pick the cup cup_01")
    assert g.target_object == "cup_01"


def test_pick_case_insensitive(parser: GoalParser) -> None:
    g = parser.parse("PICK the CUP")
    assert g.args.get("object_type") == "cup"


# ─── Place ───────────────────────────────────────────────────────────────


def test_place_on(parser: GoalParser) -> None:
    g = parser.parse("place the red cup on the table")
    assert g.kind is GoalKind.MANIPULATION
    assert g.predicate == "place"
    assert g.args.get("color") == "red"
    assert g.args.get("object_type") == "cup"
    assert g.args.get("target") == "table"


def test_place_onto(parser: GoalParser) -> None:
    g = parser.parse("place the cup onto the shelf")
    assert g.args.get("target") == "shelf"


# ─── Navigation ──────────────────────────────────────────────────────────


def test_go_to(parser: GoalParser) -> None:
    g = parser.parse("go to the kitchen")
    assert g.kind is GoalKind.NAVIGATION
    assert g.target_location == "kitchen"


def test_navigate_to(parser: GoalParser) -> None:
    g = parser.parse("navigate to the living_room")
    assert g.kind is GoalKind.NAVIGATION
    assert g.target_location == "living_room"


# ─── Open / close ────────────────────────────────────────────────────────


def test_open(parser: GoalParser) -> None:
    g = parser.parse("open the drawer")
    assert g.kind is GoalKind.MANIPULATION
    assert g.predicate == "open"


def test_close(parser: GoalParser) -> None:
    g = parser.parse("close the door")
    assert g.predicate == "close"


# ─── Perceptual ──────────────────────────────────────────────────────────


def test_find(parser: GoalParser) -> None:
    g = parser.parse("find the blue bottle")
    assert g.kind is GoalKind.PERCEPTUAL
    assert g.args.get("color") == "blue"
    assert g.args.get("object_type") == "bottle"


# ─── Errors ──────────────────────────────────────────────────────────────


def test_empty_instruction(parser: GoalParser) -> None:
    with pytest.raises(ParseError, match="empty"):
        parser.parse("")


def test_whitespace_only(parser: GoalParser) -> None:
    with pytest.raises(ParseError):
        parser.parse("   ")


def test_unknown_instruction(parser: GoalParser) -> None:
    with pytest.raises(ParseError, match="could not parse"):
        parser.parse("make me a sandwich")


def test_can_parse_true(parser: GoalParser) -> None:
    assert parser.can_parse("pick the red cup")


def test_can_parse_false(parser: GoalParser) -> None:
    assert not parser.can_parse("hello world")


def test_can_parse_empty(parser: GoalParser) -> None:
    assert not parser.can_parse("")


# ─── Goal identity ───────────────────────────────────────────────────────


def test_auto_generated_goal_id(parser: GoalParser) -> None:
    g = parser.parse("pick the cup")
    assert g.goal_id.startswith("goal_")


def test_explicit_goal_id(parser: GoalParser) -> None:
    from orb_types import GoalId

    g = parser.parse("pick the cup", goal_id=GoalId("goal_42"))
    assert g.goal_id == "goal_42"
