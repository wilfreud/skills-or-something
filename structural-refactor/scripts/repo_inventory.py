#!/usr/bin/env python3
"""Rank source files for structural *inspection*.

This script intentionally does not decide whether a file should be refactored.
It emits cheap, deterministic triage signals; semantic interpretation belongs to
an engineer/agent with repository context.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

SOURCE_EXTS = {
    ".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp",
    ".cs", ".go", ".java", ".kt", ".kts", ".rs", ".swift",
    ".py", ".rb", ".php", ".ex", ".exs", ".erl", ".hrl",
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte",
}

DEFAULT_IGNORES = {
    ".git", ".hg", ".svn", "node_modules", "vendor", "dist", "build",
    "coverage", ".next", ".nuxt", ".turbo", ".cache", "target", "out",
    "Pods", ".venv", "venv", "__pycache__",
}

IMPORT_PATTERNS = [
    re.compile(r"^\s*import\s", re.M),
    re.compile(r"^\s*from\s+\S+\s+import\s", re.M),
    re.compile(r"^\s*#include\s*[<\"]", re.M),
    re.compile(r"^\s*using\s+[^;]+;", re.M),
    re.compile(r"\brequire\s*\(", re.M),
]

# A deliberately crude control-flow token count, NOT cyclomatic complexity.
CONTROL_FLOW = re.compile(
    r"\b(if|else\s+if|for|while|switch|case|catch|except|match|when)\b|&&|\|\|"
)

GENERATED_HINTS = (
    "generated", "gen/", "dist/", "build/", ".min.js", ".min.css",
    "openapi", "swagger", "graphql.generated", "__generated__",
)


def is_probably_generated(rel: str, text_head: str) -> bool:
    lower = rel.lower().replace("\\", "/")
    if any(h in lower for h in GENERATED_HINTS):
        return True
    head = text_head.lower()
    return "generated file" in head or "do not edit" in head or "auto-generated" in head


def inspect_file(path: Path, root: Path) -> dict:
    raw = path.read_text(encoding="utf-8", errors="replace")
    lines = raw.splitlines()
    nonblank = sum(1 for line in lines if line.strip())
    imports = sum(len(p.findall(raw)) for p in IMPORT_PATTERNS)
    flow_tokens = len(CONTROL_FLOW.findall(raw))
    rel = path.relative_to(root).as_posix()
    return {
        "path": rel,
        "ext": path.suffix.lower(),
        "lines": len(lines),
        "nonblank": nonblank,
        "imports_approx": imports,
        "control_flow_tokens_approx": flow_tokens,
        "probably_generated": is_probably_generated(rel, raw[:2000]),
    }


def iter_source_files(root: Path, include_generated: bool):
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in DEFAULT_IGNORES]
        current_path = Path(current)
        for name in files:
            path = current_path / name
            if path.suffix.lower() not in SOURCE_EXTS:
                continue
            try:
                data = inspect_file(path, root)
            except (OSError, UnicodeError):
                continue
            if data["probably_generated"] and not include_generated:
                continue
            yield data


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank source files for structural inspection.")
    parser.add_argument("root", nargs="?", default=".", help="Repository root (default: .)")
    parser.add_argument("--top", type=int, default=40, help="Number of files to show (default: 40)")
    parser.add_argument("--min-lines", type=int, default=1, help="Ignore files smaller than this")
    parser.add_argument("--include-generated", action="store_true", help="Include likely generated files")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")

    rows = [r for r in iter_source_files(root, args.include_generated) if r["lines"] >= args.min_lines]
    rows.sort(key=lambda r: (r["lines"], r["control_flow_tokens_approx"], r["imports_approx"]), reverse=True)
    rows = rows[: max(args.top, 0)]

    if args.json:
        print(json.dumps({"root": str(root), "files": rows}, indent=2))
        return 0

    print("# Repository structural inventory")
    print()
    print("Triage only. `imports_approx` and `control_flow_tokens_approx` are regex signals, not semantic metrics.")
    print()
    print("| file | lines | nonblank | imports≈ | flow tokens≈ |")
    print("|---|---:|---:|---:|---:|")
    for r in rows:
        print(f"| `{r['path']}` | {r['lines']} | {r['nonblank']} | {r['imports_approx']} | {r['control_flow_tokens_approx']} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
