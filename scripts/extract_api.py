#!/usr/bin/env python3
"""Extract function signatures and docstrings from a Python source file."""

from __future__ import annotations

import argparse
import ast
import json
import pathlib
import sys


def _signature(node: ast.FunctionDef) -> str:
    args = ast.unparse(node.args)
    ret = f" -> {ast.unparse(node.returns)}" if node.returns is not None else ""
    return f"{node.name}({args}){ret}"


def _first_line(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def extract(path: pathlib.Path, names: set[str] | None) -> list[dict]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    result = []
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if names is not None and node.name not in names:
            continue
        doc = ast.get_docstring(node, clean=True) or ""
        result.append({
            "name": node.name,
            "line": node.lineno,
            "signature": _signature(node),
            "docstring": doc,
            "summary": _first_line(doc),
            "decorators": [ast.unparse(d) for d in node.decorator_list],
        })
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=pathlib.Path)
    parser.add_argument("--names", help="comma-separated function names")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    names = None
    if args.names:
        names = {name.strip() for name in args.names.split(",") if name.strip()}

    rows = extract(args.source, names)
    if args.json:
        json.dump(rows, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0

    for row in rows:
        print(f"## {row['name']} (line {row['line']})")
        print(f"signature: {row['signature']}")
        if row["decorators"]:
            print(f"decorators: {', '.join(row['decorators'])}")
        print(f"summary: {row['summary'] or '<missing>'}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
