#!/usr/bin/env python3
"""Parse ctest log lines for pass/fail/disabled floors (M06 math baseline)."""

from __future__ import annotations

import argparse
import re
import sys

CTEST_SUMMARY = re.compile(
    r"(\d+)%\s+tests passed,\s*(\d+)\s+tests failed out of (\d+)",
    re.IGNORECASE,
)
PASS_RE = re.compile(r"(\d+)\s+tests?\s+passed", re.I)
FAIL_RE = re.compile(r"(\d+)\s+tests?\s+failed", re.I)
DISABLED_RE = re.compile(r"(\d+)\s+tests?\s+disabled", re.I)
PAREN_DISABLED = re.compile(r"\(\s*(\d+)\s+disabled\s*\)", re.I)
DISABLED_MARKER = re.compile(r"\(Disabled\)", re.I)


def parse_disabled_from_section(text: str) -> int | None:
    marker = "The following tests did not run:"
    if marker not in text:
        return 0
    tail = text.split(marker, 1)[1]
    section = tail.split("\n\n", 1)[0]
    return len(DISABLED_MARKER.findall(section))


def parse_counts(text: str) -> tuple[int | None, int | None, int | None]:
    passed = failed = disabled = None
    for line in text.splitlines():
        if m := CTEST_SUMMARY.search(line):
            failed = int(m.group(2))
            passed = int(m.group(3)) - failed
            continue
        if m := PASS_RE.search(line):
            passed = int(m.group(1))
        if m := FAIL_RE.search(line):
            failed = int(m.group(1))
        if m := DISABLED_RE.search(line):
            disabled = int(m.group(1))
        if m := PAREN_DISABLED.search(line):
            disabled = int(m.group(1))
    if disabled is None:
        disabled = parse_disabled_from_section(text)
    return passed, failed, disabled


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("logfile", type=argparse.FileType("r", encoding="utf-8", errors="replace"))
    parser.add_argument("--min-passed", type=int, default=90)
    parser.add_argument("--max-failed", type=int, default=0)
    parser.add_argument("--exact-disabled", type=int, default=0)
    args = parser.parse_args()
    text = args.logfile.read()
    passed, failed, disabled = parse_counts(text)
    errors: list[str] = []
    if passed is None or passed < args.min_passed:
        errors.append(f"passed {passed} < minimum {args.min_passed}")
    if failed is None or failed > args.max_failed:
        errors.append(f"failed {failed} > maximum {args.max_failed}")
    if disabled is None or disabled != args.exact_disabled:
        errors.append(f"disabled {disabled} != expected {args.exact_disabled}")
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    print(f"ctest OK: passed={passed} failed={failed} disabled={disabled}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
