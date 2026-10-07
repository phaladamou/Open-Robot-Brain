"""orb-embodiment — embodiment layer for Open Robot Brain.

Public API is re-exported here.
"""

from orb_embodiment.abstraction.robot import BaseRobot
from orb_embodiment.adapters.fake import FakeRobot

__all__ = [
    "BaseRobot",
    "FakeRobot",
]
