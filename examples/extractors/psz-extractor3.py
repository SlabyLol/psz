#!/usr/bin/env python3
"""PSZ Extractor 3 – full CLI using psz package (list / open / selective)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from psz import list_archive_members, open_archive


def main() -> int:
    p = argparse.ArgumentParser(description="PSZ list/open via package")
    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("list", help="List members inside .psz")
    pl.add_argument("psz", type=Path)
    pl.add_argument("lor", type=Path)

    po = sub.add_parser("open", help="Extract .psz")
    po.add_argument("psz", type=Path)
    po.add_argument("lor", type=Path)
    po.add_argument("-o", "--output", type=Path, default=Path("extracted"))
    po.add_argument("-m", "--member", dest="members", action="append", default=None)

    args = p.parse_args()
    try:
        if args.cmd == "list":
            for name in list_archive_members(args.psz, args.lor):
                print(name)
            return 0
        if args.cmd == "open":
            extracted = open_archive(args.psz, args.lor, args.output, members=args.members)
            print(f"Extracted {len(extracted)} → {args.output.resolve()}")
            for name in extracted:
                print(f"  {name}")
            return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
