"""Guard: production code must not call ``Path.write_text`` directly."""

from __future__ import annotations

import ast
from pathlib import Path


def _src_root() -> Path:
    return Path(__file__).resolve().parents[1] / "src"


def _iter_py_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.py") if p.is_file())


def _calls_write_text(tree: ast.AST) -> list[int]:
    """Return line numbers of ``*.write_text(...)`` call sites."""
    lines: list[int] = []

    class Visitor(ast.NodeVisitor):
        def visit_Call(self, node: ast.Call) -> None:  # noqa: N802 — ast API
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == "write_text":
                lines.append(node.lineno)
            self.generic_visit(node)

    Visitor().visit(tree)
    return lines


def test_src_avoids_path_write_text_except_atomic_helper() -> None:
    """Regression guard: route user-visible writes through ``atomic_write_text``."""
    root = _src_root()
    violations: list[str] = []
    for path in _iter_py_files(root):
        if path.resolve() == (root / "pipeline" / "atomic.py").resolve():
            continue
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        for lineno in _calls_write_text(tree):
            rel = path.relative_to(root.parent)
            violations.append(f"{rel}:{lineno}")

    assert not violations, "Direct .write_text() calls under src/:\n" + "\n".join(violations)
