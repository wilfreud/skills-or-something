#!/usr/bin/env python3
"""Small deterministic guard for spec-locked TDD.

Locks hashes of a feature specification and selected test files/directories.
It is intentionally dependency-free and is a process guardrail, not a security boundary.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Iterable

VERSION = 1
DEFAULT_MANIFEST = ".tdd-spec-lock.json"
DEFAULT_AUDIT = ".tdd-spec-lock.audit.log"
IGNORED_DIRS = {".git", "node_modules", "__pycache__", ".pytest_cache", ".next", "dist", "build"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_files(paths: Iterable[str]) -> list[Path]:
    files: set[Path] = set()
    for raw in paths:
        p = Path(raw).expanduser()
        if not p.exists():
            raise FileNotFoundError(raw)
        if p.is_file():
            files.add(p.resolve())
            continue
        for child in p.rglob("*"):
            if any(part in IGNORED_DIRS for part in child.parts):
                continue
            if child.is_file():
                files.add(child.resolve())
    return sorted(files)


def rel_for_manifest(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return os.path.relpath(path, root)


def capture(paths: Iterable[str], root: Path) -> dict[str, str]:
    return {rel_for_manifest(p, root): sha256(p) for p in iter_files(paths)}


def load_manifest(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"lock manifest not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if data.get("version") != VERSION:
        raise ValueError(f"unsupported lock manifest version: {data.get('version')}")
    return data


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")
    tmp.replace(path)


def cmd_lock(args: argparse.Namespace) -> int:
    root = Path.cwd().resolve()
    manifest = Path(args.manifest)
    if manifest.exists() and not args.force:
        print(f"ERROR: {manifest} already exists; check/unlock it first (or use --force intentionally).", file=sys.stderr)
        return 2

    spec_paths = args.spec or []
    test_paths = args.tests or []
    if not spec_paths and not test_paths:
        print("ERROR: lock requires at least one --spec or --tests path.", file=sys.stderr)
        return 2

    try:
        spec = capture(spec_paths, root)
        tests = capture(test_paths, root)
    except FileNotFoundError as e:
        print(f"ERROR: path does not exist: {e}", file=sys.stderr)
        return 2

    if not spec and spec_paths:
        print("ERROR: --spec resolved to no files.", file=sys.stderr)
        return 2
    if not tests and test_paths:
        print("ERROR: --tests resolved to no files.", file=sys.stderr)
        return 2

    payload = {
        "version": VERSION,
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "root": str(root),
        "spec": spec,
        "tests": tests,
    }
    write_json(manifest, payload)
    print(f"LOCKED {len(spec)} spec file(s) and {len(tests)} test file(s) in {manifest}")
    return 0


def diff_group(group: str, expected: dict[str, str], root: Path) -> list[str]:
    problems: list[str] = []
    for rel, old_hash in expected.items():
        p = (root / rel).resolve()
        if not p.exists():
            problems.append(f"{group}: REMOVED {rel}")
        elif not p.is_file():
            problems.append(f"{group}: NOT_A_FILE {rel}")
        else:
            new_hash = sha256(p)
            if new_hash != old_hash:
                problems.append(f"{group}: CHANGED {rel}")
    return problems


def cmd_check(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest)
    try:
        data = load_manifest(manifest_path)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    root = Path(data["root"]).resolve()
    problems = diff_group("SPEC", data.get("spec", {}), root)
    problems += diff_group("TEST", data.get("tests", {}), root)

    if problems:
        print("LOCK VIOLATION")
        for p in problems:
            print(f"- {p}")
        return 1

    print(f"LOCK OK: {len(data.get('spec', {}))} spec file(s), {len(data.get('tests', {}))} test file(s) unchanged")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest)
    try:
        data = load_manifest(manifest_path)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    print(f"manifest: {manifest_path}")
    print(f"created_at_utc: {data.get('created_at_utc')}")
    print(f"root: {data.get('root')}")
    print(f"spec files: {len(data.get('spec', {}))}")
    for p in sorted(data.get("spec", {})):
        print(f"  SPEC {p}")
    print(f"test files: {len(data.get('tests', {}))}")
    for p in sorted(data.get("tests", {})):
        print(f"  TEST {p}")
    return 0


def cmd_unlock(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"ERROR: lock manifest not found: {manifest_path}", file=sys.stderr)
        return 2

    reason = args.reason.strip()
    if not reason:
        print("ERROR: --reason must be non-empty.", file=sys.stderr)
        return 2

    audit_path = Path(args.audit)
    entry = {
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "manifest": str(manifest_path),
        "reason": reason,
    }
    with audit_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")

    manifest_path.unlink()
    print(f"UNLOCKED {manifest_path}; reason recorded in {audit_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Hash-lock TDD specs/tests so oracle changes are explicit.")
    sub = parser.add_subparsers(dest="command", required=True)

    lock = sub.add_parser("lock", help="Create a lock manifest for spec/test files.")
    lock.add_argument("--spec", action="append", default=[], help="Spec file or directory; repeatable.")
    lock.add_argument("--tests", action="append", default=[], help="Test file or directory; repeatable.")
    lock.add_argument("--manifest", default=DEFAULT_MANIFEST)
    lock.add_argument("--force", action="store_true", help="Overwrite an existing manifest intentionally.")
    lock.set_defaults(func=cmd_lock)

    check = sub.add_parser("check", help="Verify locked files are unchanged.")
    check.add_argument("--manifest", default=DEFAULT_MANIFEST)
    check.set_defaults(func=cmd_check)

    status = sub.add_parser("status", help="Show the current lock contents.")
    status.add_argument("--manifest", default=DEFAULT_MANIFEST)
    status.set_defaults(func=cmd_status)

    unlock = sub.add_parser("unlock", help="Remove a lock and append an audit reason.")
    unlock.add_argument("--manifest", default=DEFAULT_MANIFEST)
    unlock.add_argument("--audit", default=DEFAULT_AUDIT)
    unlock.add_argument("--reason", required=True)
    unlock.set_defaults(func=cmd_unlock)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
