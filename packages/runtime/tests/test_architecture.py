"""Architecture boundary tests (repo-level).

Non-negotiable #1: ``brain/`` never imports embodiment, simulation,
control, robots, or apps code. import-linter enforces this on installed
packages in CI; these tests enforce it on source files — including
brain tests, which import-linter never sees — on every local pytest
run, with no extra tooling.

This module lives in runtime's tests so it runs in the standard suite
and stays under ``mypy --strict``; it guards the whole repo's
boundary, not runtime behavior.
"""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
BRAIN_SRC = REPO_ROOT / "packages" / "brain" / "src" / "orb_brain"
BRAIN_TESTS = REPO_ROOT / "packages" / "brain" / "tests"

#: Import roots the brain must never touch: importable distributions
#: first, then path-style names guarding a future top-level layout.
FORBIDDEN_ROOTS: frozenset[str] = frozenset(
    {
        "orb_embodiment",
        "orb_simulation",
        "orb_control",
        "orb_robots",
        "orb_apps_simulator",
        "embodiment",
        "simulation",
        "control",
        "robots",
        "apps",
    }
)


def _iter_py_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.py") if "__pycache__" not in p.parts)


def _module_parts(path: Path) -> tuple[str, ...]:
    """Dotted module of a file under ``BRAIN_SRC`` (e.g. ``htn.py``)."""
    rel = path.relative_to(BRAIN_SRC.parent).with_suffix("")
    parts = rel.parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return parts


def _resolve_from_root(
    module: tuple[str, ...], *, is_package: bool, node: ast.ImportFrom
) -> str | None:
    """Resolve a from-import to its absolute root, if provable.

    Returns ``None`` when the import escapes the brain package or its
    level cannot be resolved — both are violations.
    """
    if node.level == 0:
        if node.module is None:  # `from import x` is a syntax error; be safe.
            return None
        return node.module.split(".")[0]
    package = module if is_package else module[:-1]
    if node.level > len(package):
        return None
    base = package[: len(package) - node.level + 1]
    if node.module is not None:
        base = (*base, *node.module.split("."))
    if not base or base[0] != "orb_brain":
        return None
    return base[0]


def _check_from_import(
    path: Path,
    module: tuple[str, ...],
    *,
    is_package: bool,
    packaged: bool,
    node: ast.ImportFrom,
) -> list[str]:
    """Return violations for one from-import, if any."""
    if not packaged:
        if node.level > 0:
            return [f"{path}:{node.lineno}: relative import outside a package"]
        if node.module is not None and node.module.split(".")[0] in FORBIDDEN_ROOTS:
            return [f"{path}:{node.lineno}: from {node.module} import ..."]
        return []
    resolved = _resolve_from_root(module, is_package=is_package, node=node)
    if resolved is None:
        return [f"{path}:{node.lineno}: unresolvable relative import"]
    if resolved in FORBIDDEN_ROOTS:
        return [f"{path}:{node.lineno}: from {node.module} import ..."]
    return []


def _forbidden_in_file(path: Path, *, packaged: bool) -> list[str]:
    """Return ``path:lineno:detail`` entries for forbidden imports."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    module = _module_parts(path) if packaged else ()
    is_package = path.name == "__init__.py"
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in FORBIDDEN_ROOTS:
                    violations.append(f"{path}:{node.lineno}: import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            violations.extend(
                _check_from_import(
                    path, module, is_package=is_package, packaged=packaged, node=node
                )
            )
    return violations


def _scan(root: Path, *, packaged: bool) -> tuple[int, list[str]]:
    files = _iter_py_files(root)
    violations: list[str] = []
    for path in files:
        violations.extend(_forbidden_in_file(path, packaged=packaged))
    return len(files), violations


def test_brain_src_has_no_forbidden_imports() -> None:
    scanned, violations = _scan(BRAIN_SRC, packaged=True)
    assert scanned > 0, f"no files scanned under {BRAIN_SRC}"
    assert violations == [], "forbidden brain imports:\n" + "\n".join(violations)


def test_brain_tests_have_no_forbidden_imports() -> None:
    scanned, violations = _scan(BRAIN_TESTS, packaged=False)
    assert scanned > 0, f"no files scanned under {BRAIN_TESTS}"
    assert violations == [], "forbidden brain-test imports:\n" + "\n".join(violations)
