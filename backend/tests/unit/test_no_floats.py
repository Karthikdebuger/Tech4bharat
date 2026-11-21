"""AST verification test: Absolutely zero floating-point operations in app/domain.

Per ADR-0004 and the Non-Negotiable Coding Rules (§3.3 Rule 1):
No floating point for weight, purity, rate, money or ledger amounts. Integers only.
"""

import ast
from pathlib import Path


class FloatDetector(ast.NodeVisitor):
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.violations: list[str] = []

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, float):
            self.violations.append(
                f"{self.filename}:{node.lineno}: Float literal `{node.value}` found."
            )
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id == "float":
            self.violations.append(f"{self.filename}:{node.lineno}: Reference to `float` found.")
        self.generic_visit(node)


def test_strictly_no_floats_in_domain() -> None:
    """Ensure no Python file in app/domain contains float literals or types."""
    domain_dir = Path(__file__).parent.parent.parent / "app" / "domain"
    assert domain_dir.is_dir(), f"Domain directory {domain_dir} not found"

    all_violations: list[str] = []
    py_files = list(domain_dir.glob("*.py"))
    assert len(py_files) >= 2, "Expected domain python files"

    for py_file in py_files:
        with open(py_file, encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=str(py_file))
        detector = FloatDetector(str(py_file.name))
        detector.visit(tree)
        all_violations.extend(detector.violations)

    assert not all_violations, "Float violations found in domain:\n" + "\n".join(all_violations)
