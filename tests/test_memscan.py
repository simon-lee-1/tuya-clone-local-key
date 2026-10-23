#!/usr/bin/env python3
"""PRE-REGISTERED strict-build and byte-search tests, written before memscan.c."""
from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/memscan.c"
checks = []


def ck(label, ok, detail=""):
    checks.append((bool(ok), label, detail))


with tempfile.TemporaryDirectory() as raw:
    binary = Path(raw) / "memscan"
    built = subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-O2",
                            str(SOURCE), "-o", str(binary)], capture_output=True, text=True)
    ck("M1 scanner compiles with strict warnings", built.returncode == 0,
       built.stdout + built.stderr)

    if built.returncode == 0:
        help_result = subprocess.run([str(binary), "--help"], capture_output=True, text=True)
        ck("M2 help declares owner-authorised privileged use", help_result.returncode == 0
           and "owner-authorised" in (help_result.stdout + help_result.stderr).lower()
           and "privileged" in (help_result.stdout + help_result.stderr).lower())

        invalid = subprocess.run([str(binary), "not-a-pid", "needle"], capture_output=True, text=True)
        ck("M3 non-numeric PID is rejected", invalid.returncode != 0)
        empty = subprocess.run([str(binary), "1", ""], capture_output=True, text=True)
        ck("M4 empty search is rejected", empty.returncode != 0)

        # Test-only file mode uses the same overlap-aware scan core but never ptrace/root/ADB.
        data = b"A" * 65533 + b"localKey" + b"B" * 11 + b"localKey" + b"C" * 20
        fixture = Path(raw) / "bytes.bin"
        fixture.write_bytes(data)
        scanned = subprocess.run([str(binary), "--test-file", str(fixture), "localKey",
                                  "--context", "8"], capture_output=True, timeout=10)
        ck("M5 file harness finds chunk-boundary and later matches",
           scanned.returncode == 0 and scanned.stdout.count(b"===MATCH===") == 2,
           scanned.stderr.decode("utf-8", "replace"))
        ck("M6 context output is bounded", len(scanned.stdout) < 256)
    else:
        for label in range(2, 7):
            ck(f"M{label} unavailable", False, "build failed")

passed = sum(ok for ok, _, _ in checks)
for ok, label, detail in checks:
    print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f"  {detail}" if detail and not ok else ""))
print(f"\n{passed}/{len(checks)} checks passed; {len(checks)-passed} failed")
raise SystemExit(0 if passed == len(checks) else 1)
