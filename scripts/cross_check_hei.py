#!/usr/bin/env python3
"""Cross-check swiss-hei-open-data against ROR, OpenAlex, and Wikidata.

Reads dashboards/_data/hei.csv and queries external registry APIs to verify
identifiers, detect discrepancies, and report missing data.

Usage::

    uv run python scripts/cross_check_hei.py
    uv run python scripts/cross_check_hei.py --output report.md
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

import pandas as pd

try:
    from cross_check_hei_checks import run_checks
    from cross_check_hei_common import DATA_PATH
    from cross_check_hei_report import format_report
except ImportError:  # pragma: no cover - package import path for tests
    from scripts.cross_check_hei_checks import run_checks
    from scripts.cross_check_hei_common import DATA_PATH
    from scripts.cross_check_hei_report import format_report


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="Cross-check swiss-hei-open-data against external registries.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Write Markdown report to FILE (default: stdout).",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=DATA_PATH,
        help=f"Path to hei.csv (default: {DATA_PATH}).",
    )
    args = parser.parse_args()

    csv_path: Path = args.csv
    if not csv_path.exists():
        print(f"Error: {csv_path} not found.", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} institutions from {csv_path.name}.", file=sys.stderr)

    issues = asyncio.run(run_checks(df))
    report = format_report(issues, df)

    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"\nReport written to {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
