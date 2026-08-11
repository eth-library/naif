#!/usr/bin/env python3
"""Fetch a build-time Matomo snapshot for the site usage dashboard.

Usage::

    uv run python scripts/fetch_matomo_usage.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def main() -> None:
    """Fetch the latest Matomo snapshot when credentials are available."""
    from dashboards._matomo_usage import (
        SNAPSHOT_PATH,
        fetch_usage_snapshot,
        load_matomo_config,
        write_snapshot,
    )

    config = load_matomo_config()
    if config is None:
        print(
            "Skipping Matomo usage snapshot fetch: MATOMO_TOKEN_AUTH is not set.",
            file=sys.stderr,
        )
        return

    snapshot = fetch_usage_snapshot(config)
    write_snapshot(snapshot, SNAPSHOT_PATH)
    print(f"Wrote Matomo usage snapshot to {SNAPSHOT_PATH}", file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    # Deliberately broad: top-level CLI handler must not let any error crash silently.
    except Exception as exc:  # noqa: BLE001 pragma: no cover - integration behaviour
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
