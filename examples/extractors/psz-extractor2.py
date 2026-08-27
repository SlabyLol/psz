#!/usr/bin/env python3
"""PSZ Extractor 2 – choose files; uses psz package API."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from psz import open_archive


def main() -> int:
    p = argparse.ArgumentParser(description="Load .psz using .psz-data.lor (psz package)")
    p.add_argument("psz", type=Path, help=".psz archive")
    p.add_argument("lor", type=Path, help=".psz-data.lor (key file)")
    p.add_argument("-o", "--output", type=Path, default=Path("extracted"))
    p.add_argument("-m", "--member", dest="members", action="append", default=None)
    args = p.parse_args()
    try:
        extracted = open_archive(args.psz, args.lor, args.output, members=args.members)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    print(f"OK – {len(extracted)} item(s) → {args.output.resolve()}")
    for name in extracted:
        print(f"  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
