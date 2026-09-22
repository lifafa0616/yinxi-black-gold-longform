#!/usr/bin/env python3
"""Create the only pre-confirmation case artifact: one empty plan.md.

This deliberately does not create assets, frames, render.html, poster.html or
final.png.  It gives the agent one narrow, repeatable way to start a case
without accidentally beginning production before the user approves the copy
and first-screen strategy.
"""

import argparse
import shutil
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
PLAN_TEMPLATE = SKILL_ROOT / "references" / "daily-plan-template.md"


def valid_case_name(value: str) -> bool:
    candidate = Path(value)
    return bool(value.strip()) and candidate.name == value and value not in {".", ".."}


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a pre-confirmation longform case plan and nothing else.")
    parser.add_argument("--output-root", required=True, type=Path, help="user-designated output root")
    parser.add_argument("--case", required=True, help="semantic case folder name; no path separators")
    args = parser.parse_args()
    if not valid_case_name(args.case):
        parser.error("--case must be one semantic folder name without path separators")
    if not PLAN_TEMPLATE.is_file():
        print(f"plan template is missing: {PLAN_TEMPLATE}", file=sys.stderr)
        return 1
    case_dir = args.output_root / "cases" / args.case
    plan = case_dir / "plan.md"
    if plan.exists():
        print(f"refusing to overwrite existing case plan: {plan}", file=sys.stderr)
        return 1
    if case_dir.exists() and any(case_dir.iterdir()):
        print(f"refusing to use a non-empty case directory before confirmation: {case_dir}", file=sys.stderr)
        return 1
    case_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(PLAN_TEMPLATE, plan)
    print(f"created pre-confirmation plan: {plan}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
