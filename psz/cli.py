"""Command-line interface for PSZ."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .core import SUPPORTED_LANGUAGES, create_archive, open_archive


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="psz",
        description=(
            "PSZ – Encrypted project archives with paired unpackers "
            "(.psz + Python / PHP / HTML)"
        ),
    )
    parser.add_argument(
        "--version", action="version", version=f"psz {__version__}"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # ---- make ----
    p_make = sub.add_parser(
        "make",
        help="Create an encrypted .psz archive + matching unpackers",
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
        "--lang",
        "--language",
        dest="languages",
        action="append",
        choices=list(SUPPORTED_LANGUAGES) + ["all"],
        default=None,
        help=(
            "Unpacker language(s) to generate: python, php, html, or all. "
            "Can be repeated. Default: all"
        ),
    )
    p_make.add_argument(
        "--lor",
        type=Path,
        default=None,
        help="Custom path for a single unpacker (only when one --lang is set)",
    )

    # ---- open ----
    p_open = sub.add_parser(
        "open",
        help="Open/decrypt a .psz archive using a matching unpacker file",
    )
    p_open.add_argument(
        "archive",
        type=Path,
        help="The .psz archive file",
    )
    p_open.add_argument(
        "lor",
        type=Path,
        help="Matching unpacker (.lor / .php / .html) that embeds the key",
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
            langs = args.languages
            if langs is None or "all" in langs:
                languages = list(SUPPORTED_LANGUAGES)
            else:
                languages = langs

            psz_path, unpackers = create_archive(
                source=args.source,
                output_psz=args.output,
                lor_path=args.lor,
                languages=languages,
            )
            print(f"Created: {psz_path}")
            for u in unpackers:
                print(f"Created: {u}")
            print()
            print("To extract later:")
            print(f"  psz open {psz_path.name} <unpacker> -o output_dir")
            for u in unpackers:
                name = u.name
                if name.endswith(".lor"):
                    print(f"  python {name} {psz_path.name} -o output_dir")
                elif name.endswith(".php"):
                    print(f"  php {name} {psz_path.name} -o output_dir")
                elif name.endswith(".html"):
                    print(f"  open {name} in a browser and select {psz_path.name}")
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
