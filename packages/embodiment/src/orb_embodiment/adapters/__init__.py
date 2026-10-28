"""Adapters for specific robots (simulated or physical).

Each adapter translates the common ORB robot interface into a concrete
backend: an in-process fake, a MuJoCo model, a ROS 2 node, etc.
"""

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
    "FakeRobot",
]
