#!/usr/bin/env python3
"""PSZ Extractor 1 – DIRECT load via the psz Python package."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from psz import open_archive

BASE = Path(__file__).resolve().parent.parent
PSZ = BASE / "demo.psz"
LOR = BASE / "demo.psz-data.lor"
OUT = BASE / "out-extractor1-py"


def main() -> int:
    if not PSZ.is_file() or not LOR.is_file():
        print(f"Missing {PSZ.name} or {LOR.name}", file=sys.stderr)
        return 1
    extracted = open_archive(PSZ, LOR, OUT)
    print(f"OK – psz package loaded {PSZ.name} via {LOR.name} → {OUT}")
    for name in extracted:
        print(f"  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
