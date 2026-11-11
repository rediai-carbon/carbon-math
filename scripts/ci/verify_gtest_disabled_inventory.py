#!/usr/bin/env python3
"""M06: verify Carbon Math gtest DISABLED_ inventory (M01 baseline: zero disabled tests)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TESTS = ROOT / "tests"
EXPECTED_DISABLED = 0
PATTERN = re.compile(
    r"TEST(?:_F)?\s*\(\s*([^,]+)\s*,\s*DISABLED_([^\s\)]+)\s*\)"
)


def main() -> int:
    if not TESTS.is_dir():
        print(f"tests directory missing: {TESTS}", file=sys.stderr)
        return 1
    found: list[str] = []
    for path in sorted(TESTS.glob("*.cpp")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in PATTERN.finditer(text):
            suite, name = match.group(1).strip(), match.group(2).strip()
            found.append(f"{suite}.DISABLED_{name} @ {path.relative_to(ROOT)}")
    print(f"DISABLED_ tests found: {len(found)}")
    for row in found:
        print(f"  - {row}")
    if len(found) != EXPECTED_DISABLED:
        print(
            f"expected {EXPECTED_DISABLED} DISABLED_ tests, found {len(found)}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
