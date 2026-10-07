# orb-sdk

Public SDK - the entry point for external users.

```python
from orb_sdk import RobotBrain

brain = RobotBrain(robot)
brain.observe()
brain.execute("pick", object="red_cup")
```

> API is expected to evolve as the architecture matures.
