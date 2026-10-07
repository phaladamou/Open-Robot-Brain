"""Adapters for specific robots (simulated or physical).

Each adapter translates the common ORB robot interface into a concrete
backend: an in-process fake, a MuJoCo model, a ROS 2 node, etc.
"""

from orb_embodiment.adapters.fake import FakeRobot

__all__ = ["FakeRobot"]
