#!/usr/bin/env python3
"""PRE-REGISTERED parser tests, written before extract_local_keys.py."""
from __future__ import annotations

import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/extract_local_keys.py"
FIXTURE = ROOT / "fixtures/synthetic_memory.fixture"
EXPECTED = ROOT / "fixtures/expected.json"
checks = []


def ck(label, ok, detail=""):
    checks.append((bool(ok), label, detail))


def run(*args):
    return subprocess.run([sys.executable, str(TOOL), *map(str, args)], capture_output=True,
                          text=True, timeout=10)


ck("P1 parser, fixture and expected files exist", all(p.exists() for p in (TOOL, FIXTURE, EXPECTED)))

if all(p.exists() for p in (TOOL, FIXTURE, EXPECTED)):
    expected = json.loads(EXPECTED.read_text())
    default = run("--input", FIXTURE)
    try:
        rows = json.loads(default.stdout)
    except json.JSONDecodeError:
        rows = None
    synthetic_keys = expected["keys"]
    ck("P2 default output extracts/deduplicates expected records",
       default.returncode == 0 and isinstance(rows, list)
       and len(rows) == expected["record_count"], default.stdout + default.stderr)
    ck("P3 default output contains no local key or raw identifiers",
       rows is not None and not any(value in default.stdout for value in synthetic_keys)
       and all("local_key" not in row and "device_id" not in row and "mac" not in row for row in rows))
    ck("P4 default output has stable key fingerprints",
       rows is not None and all(len(row.get("key_fingerprint", "")) == 12 for row in rows))

    stdout_full = run("--input", FIXTURE, "--include-keys")
    ck("P5 full-key output to stdout is refused", stdout_full.returncode != 0
       and "refusing" in (stdout_full.stdout + stdout_full.stderr).lower())

    with tempfile.TemporaryDirectory() as raw:
        out = Path(raw) / "private.json"
        full = run("--input", FIXTURE, "--include-keys", "--output", out)
        values = json.loads(out.read_text()) if out.exists() else []
        ck("P6 explicit private output contains keys and is mode 600",
           full.returncode == 0 and all(key in out.read_text() for key in synthetic_keys)
           and stat.S_IMODE(out.stat().st_mode) == 0o600, full.stdout + full.stderr)
        second = run("--input", FIXTURE, "--include-keys", "--output", out)
        ck("P7 existing output is refused", second.returncode != 0)

        target = Path(raw) / "target"
        target.write_text("sentinel")
        link = Path(raw) / "link"
        link.symlink_to(target)
        symlinked = run("--input", FIXTURE, "--include-keys", "--output", link)
        ck("P8 symlink output is refused without changing target",
           symlinked.returncode != 0 and target.read_text() == "sentinel")
else:
    for label in range(2, 9):
        ck(f"P{label} unavailable", False, "implementation absent")

passed = sum(ok for ok, _, _ in checks)
for ok, label, detail in checks:
    print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f"  {detail}" if detail and not ok else ""))
print(f"\n{passed}/{len(checks)} checks passed; {len(checks)-passed} failed")
raise SystemExit(0 if passed == len(checks) else 1)
