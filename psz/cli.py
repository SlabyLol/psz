"""Command-line interface for PSZ."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .core import create_archive, open_archive


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="psz",
        description="PSZ – Encrypted project archives with paired unpacker (.psz + .psz-data.lor)",
    )
    parser.add_argument(
        "--version", action="version", version=f"psz {__version__}"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # ---- make ----
    p_make = sub.add_parser(
        "make",
        help="Create an encrypted .psz archive + matching .psz-data.lor unpacker",
    )
    p_make.add_argument(
        "source",
        type=Path,
        help="Source directory to pack",
    )
    p_make.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Output .psz file (e.g. project.psz)",
    )
    p_make.add_argument(
        "--lor",
        type=Path,
        default=None,
        help="Custom path for the .lor file (default: <output>.psz-data.lor)",
    )

    # ---- open ----
    p_open = sub.add_parser(
        "open",
        help="Open/decrypt a .psz archive using its matching .psz-data.lor",
    )
    p_open.add_argument(
        "archive",
        type=Path,
        help="The .psz archive file",
    )
    p_open.add_argument(
        "lor",
        type=Path,
        help="The matching .psz-data.lor unpacker file",
    )
    p_open.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("extracted"),
        help="Output directory (default: ./extracted)",
    )

    args = parser.parse_args(argv)

    try:
        if args.command == "make":
            psz_path, lor_path = create_archive(
                source=args.source,
                output_psz=args.output,
                lor_path=args.lor,
            )
            print(f"Created: {psz_path}")
            print(f"Created: {lor_path}")
            print()
            print("To extract later:")
            print(f"  psz open {psz_path.name} {lor_path.name} -o output_dir")
            print(f"  # or directly:")
            print(f"  python {lor_path.name} {psz_path.name} -o output_dir")
            return 0

        if args.command == "open":
            open_archive(
                psz_path=args.archive,
                lor_path=args.lor,
                output_dir=args.output,
            )
            print(f"Extracted to: {args.output.resolve()}")
            return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
