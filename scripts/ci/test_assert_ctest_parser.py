#!/usr/bin/env python3
"""Self-test for assert_ctest_results parser (M06 math floor)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SAMPLE = """\
100% tests passed, 0 tests failed out of 90

Total Test time (real) =   1.20 sec
"""

ROOT = Path(__file__).resolve().parents[2]
ASSERT = ROOT / "scripts/ci/assert_ctest_results.py"


def main() -> int:
    log = ROOT / "scripts/ci/.ctest_parser_selftest.log"
    log.write_text(SAMPLE, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(ASSERT), "--min-passed", "90", "--exact-disabled", "0", str(log)],
        capture_output=True,
        text=True,
    )
    log.unlink(missing_ok=True)
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        return 1
    print("ctest parser self-test OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
