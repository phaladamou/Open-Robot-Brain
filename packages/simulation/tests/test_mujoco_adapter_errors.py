"""Error paths of MujocoAdapter that need no MuJoCo install.

The model-file check runs before the mujoco import, so a missing file
is reported clearly even in environments without the ``mujoco`` extra.
This module must never ``importorskip("mujoco")``.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from orb_simulation.adapters import MujocoAdapter
from orb_types import NotFoundError


def test_missing_model_raises_not_found(tmp_path: Path) -> None:
    with pytest.raises(NotFoundError, match="not found"):
        MujocoAdapter(tmp_path / "nope.xml")
