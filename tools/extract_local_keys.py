#!/usr/bin/env python3
"""Extract Tuya local-key records from an offline memory-scanner stream.

Default output contains only hashes and redacted metadata. Full keys require --include-keys and an
exclusive mode-600 output file; full values are never written to stdout.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

OBJECT = re.compile(rb"\{[^{}]{0,8192}\}")
KEY_SHAPE = re.compile(r"^[\x21-\x7e]{16}$")


def _objects(data: bytes):
    for match in OBJECT.finditer(data):
        try:
            value = json.loads(match.group().decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        if isinstance(value, dict):
            yield value


def extract(data: bytes) -> list[dict]:
    records = []
    seen = set()
    for value in _objects(data):
        key = value.get("localKey")
        if not isinstance(key, str) or not KEY_SHAPE.fullmatch(key):
            continue
        identity = value.get("devId") or value.get("deviceId") or value.get("id") or ""
        digest = hashlib.sha256(key.encode()).hexdigest()
        record_id = hashlib.sha256(f"{identity}\0{digest}".encode()).hexdigest()[:12]
        if record_id in seen:
            continue
        seen.add(record_id)
        records.append({
            "record_fingerprint": record_id,
            "key_fingerprint": digest[:12],
            "local_key": key,
        })
    return records


def redacted(records: list[dict]) -> list[dict]:
    return [{"record_fingerprint": row["record_fingerprint"],
             "key_fingerprint": row["key_fingerprint"]} for row in records]


def write_private(path: Path, rows: list[dict]) -> None:
    if path.is_symlink():
        raise ValueError("refusing symlink output")
    os.umask(0o077)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(rows, stream, indent=2)
            stream.write("\n")
    except Exception:
        try:
            path.unlink()
        except OSError:
            pass
        raise
    if stat.S_IMODE(path.stat().st_mode) != 0o600:
        path.unlink(missing_ok=True)
        raise ValueError("private output mode was not 600")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Parse offline Tuya memory scanner output")
    parser.add_argument("--input", type=Path, help="input dump; default stdin")
    parser.add_argument("--include-keys", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        data = args.input.read_bytes() if args.input else sys.stdin.buffer.read()
        records = extract(data)
        if args.include_keys:
            if args.output is None:
                raise ValueError("refusing full keys on stdout; use --output")
            write_private(args.output, records)
            print(f"wrote {len(records)} private record(s) to a mode-600 file")
        else:
            if args.output is not None:
                raise ValueError("--output is reserved for --include-keys private output")
            json.dump(redacted(records), sys.stdout, indent=2)
            sys.stdout.write("\n")
        return 0
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
