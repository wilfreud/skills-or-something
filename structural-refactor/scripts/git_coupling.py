#!/usr/bin/env python3
"""Surface temporal coupling from Git history.

A pair's coefficient is cochange_count / min(change_count(A), change_count(B)).
High values are hypotheses for investigation, not proof that files should merge.
"""
from __future__ import annotations

import argparse
import itertools
import subprocess
from collections import Counter
from pathlib import Path

SOURCE_EXTS = {
    ".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".cs", ".go",
    ".java", ".kt", ".kts", ".rs", ".swift", ".py", ".rb", ".php",
    ".ex", ".exs", ".erl", ".hrl", ".js", ".jsx", ".ts", ".tsx",
    ".mjs", ".cjs", ".vue", ".svelte",
}

IGNORE_PARTS = {"node_modules", "vendor", "dist", "build", "coverage", "target", ".next"}


def eligible(name: str) -> bool:
    p = Path(name)
    return p.suffix.lower() in SOURCE_EXTS and not any(part in IGNORE_PARTS for part in p.parts)


def git_log(root: Path, max_commits: int) -> str:
    cmd = [
        "git", "-C", str(root), "log", "--no-merges",
        f"-n{max_commits}", "--pretty=format:__COMMIT__", "--name-only",
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode != 0:
        raise SystemExit(proc.stderr.strip() or "git log failed")
    return proc.stdout


def parse_commits(text: str):
    current = set()
    for line in text.splitlines():
        line = line.strip()
        if line == "__COMMIT__":
            if current:
                yield sorted(current)
            current = set()
        elif line and eligible(line):
            current.add(line)
    if current:
        yield sorted(current)


def main() -> int:
    parser = argparse.ArgumentParser(description="Report source-file temporal coupling from Git history.")
    parser.add_argument("root", nargs="?", default=".", help="Repository root (default: .)")
    parser.add_argument("--max-commits", type=int, default=1000)
    parser.add_argument("--min-cochanges", type=int, default=3)
    parser.add_argument("--min-coefficient", type=float, default=0.5)
    parser.add_argument("--top", type=int, default=40)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    text = git_log(root, args.max_commits)

    file_changes = Counter()
    pair_changes = Counter()
    commit_count = 0

    for files in parse_commits(text):
        commit_count += 1
        for f in files:
            file_changes[f] += 1
        # Avoid quadratic explosions from giant mechanical commits.
        if len(files) > 200:
            continue
        for a, b in itertools.combinations(files, 2):
            pair_changes[(a, b)] += 1

    rows = []
    for (a, b), both in pair_changes.items():
        if both < args.min_cochanges:
            continue
        denom = min(file_changes[a], file_changes[b])
        if not denom:
            continue
        coeff = both / denom
        if coeff < args.min_coefficient:
            continue
        rows.append((coeff, both, file_changes[a], file_changes[b], a, b))

    rows.sort(reverse=True)
    rows = rows[: max(args.top, 0)]

    print("# Git temporal coupling")
    print()
    print(f"Commits inspected: {commit_count}. High coupling is a hypothesis, not a merge instruction.")
    print()
    print("| coeff | cochanges | A changes | B changes | file A | file B |")
    print("|---:|---:|---:|---:|---|---|")
    for coeff, both, ca, cb, a, b in rows:
        print(f"| {coeff:.2f} | {both} | {ca} | {cb} | `{a}` | `{b}` |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
