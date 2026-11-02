#!/usr/bin/env python3
"""Check that selected Python functions have usable reST docstrings."""

from __future__ import annotations

import argparse
import ast
import pathlib
import sys


def _real_args(node: ast.FunctionDef) -> list[str]:
    args = [a.arg for a in node.args.posonlyargs + node.args.args]
    args += [a.arg for a in node.args.kwonlyargs]
    return [a for a in args if a not in {"self", "cls", "_semantic", "_generator"}]


def _returns_none(node: ast.FunctionDef) -> bool:
    ann = node.returns
    if ann is None:
        return False
    text = ast.unparse(ann)
    return text in {"None", "NoneType"}


def check(path: pathlib.Path, names: set[str], strict: bool) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    errors: list[str] = []
    found: set[str] = set()

    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if names and node.name not in names:
            continue
        found.add(node.name)
        doc = ast.get_docstring(node, clean=True) or ""
        if not doc.strip():
            errors.append(f"{path}:{node.lineno}: {node.name}: missing docstring")
            continue

        args = _real_args(node)
        if args and ":param " not in doc:
            errors.append(f"{path}:{node.lineno}: {node.name}: missing :param entries")
        if not _returns_none(node) and ":return:" not in doc and ":rtype:" not in doc:
            errors.append(f"{path}:{node.lineno}: {node.name}: missing :return:/:rtype:")
        if strict:
            for arg in args:
                if f":param {arg}:" not in doc:
                    errors.append(
                        f"{path}:{node.lineno}: {node.name}: missing :param {arg}:"
                    )
                if f":type {arg}:" not in doc:
                    errors.append(
                        f"{path}:{node.lineno}: {node.name}: missing :type {arg}:"
                    )

    if names:
        for name in sorted(names - found):
            errors.append(f"{path}: function not found: {name}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=pathlib.Path)
    parser.add_argument("--names", help="comma-separated function names")
    parser.add_argument("--strict", action="store_true", help="require per-argument :param/:type entries")
    args = parser.parse_args()

    names = set()
    if args.names:
        names = {name.strip() for name in args.names.split(",") if name.strip()}

    errors = check(args.source, names, args.strict)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"OK: {args.source} ({len(names) if names else 'all'} functions)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
