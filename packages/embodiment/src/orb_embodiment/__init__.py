"""orb-embodiment — embodiment layer for Open Robot Brain.

Public API is re-exported here.
"""

from orb_embodiment.abstraction.robot import BaseRobot
from orb_embodiment.adapters.fake import FakeRobot
from orb_embodiment.adapters.profiles import (
    FULL_ARM_CAPABILITIES,
    SHORT_ARM_CAPABILITIES,
    WEAK_ARM_CAPABILITIES,
)

__all__ = [
    "FULL_ARM_CAPABILITIES",
    "SHORT_ARM_CAPABILITIES",
    "WEAK_ARM_CAPABILITIES",
    "BaseRobot",
    "FakeRobot",
]
