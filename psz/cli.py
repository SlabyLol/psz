"""Command-line interface for PSZ."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .core import (
    SUPPORTED_LANGUAGES,
    create_archive,
    list_archive_members,
    open_archive,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="psz",
        description=(
            "PSZ – Encrypted archives with multi-language unpackers "
            "(Python / PHP / JS / HTML). "
            "Always need: .psz + matching .psz-data.lor."
        ),
    )
    parser.add_argument("--version", action="version", version=f"psz {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_make = sub.add_parser("make", help="Pack file(s)/dir into .psz + .psz-data.lor")
    p_make.add_argument("sources", nargs="+", type=Path, help="File(s) and/or directory")
    p_make.add_argument("-o", "--output", type=Path, required=True, help="Output .psz")
    p_make.add_argument(
        "--lang", "--language", dest="languages", action="append",
        choices=list(SUPPORTED_LANGUAGES), default=None,
        help="Content language of .psz-data.lor: python, php, js, html (default: python)",
    )
    p_make.add_argument("--lor", type=Path, default=None, help="Custom unpacker path")

    p_open = sub.add_parser("open", help="Extract (needs .psz + .psz-data.lor)")
    p_open.add_argument("archive", type=Path, help=".psz archive")
    p_open.add_argument("unpacker", type=Path, help="Matching .psz-data.lor with the key")
    p_open.add_argument("-o", "--output", type=Path, default=Path("extracted"))
    p_open.add_argument(
        "-m", "--member", dest="members", action="append", default=None,
        help="Extract only this path from inside the archive (repeatable)",
    )

    p_list = sub.add_parser("list", help="List contents (needs .psz + .psz-data.lor)")
    p_list.add_argument("archive", type=Path)
    p_list.add_argument("unpacker", type=Path)

    args = parser.parse_args(argv)

    try:
        if args.command == "make":
            languages = ["python"] if args.languages is None else args.languages
            if len(languages) > 1:
                print("Note: only one language per .psz-data.lor; using: " + languages[0], file=sys.stderr)
                languages = [languages[0]]
            sources = list(args.sources)
            psz_path, unpackers = create_archive(
                source=sources if len(sources) > 1 else sources[0],
                output_psz=args.output,
                lor_path=args.lor,
                languages=languages,
            )
            print(f"Created: {psz_path}")
            for u in unpackers:
                print(f"Created: {u}")
            print()
            print("Always the same name: *.psz-data.lor (any language).")
            print("Load the .psz with the .lor:")
            n = unpackers[0].name
            print(f"  python {n} {psz_path.name} -o out/     # if --lang python")
            print(f"  php    {n} {psz_path.name} -o out/     # if --lang php")
            print(f"  node   {n} {psz_path.name} -o out/     # if --lang js")
            print(f"  open {n} in browser                   # if --lang html")
            print(f"  psz open {psz_path.name} {n} -o out/")
            print(f"  psz list {psz_path.name} {n}")
            return 0

        if args.command == "open":
            members = args.members or None
            extracted = open_archive(
                psz_path=args.archive,
                lor_path=args.unpacker,
                output_dir=args.output,
                members=members,
            )
            print(f"Extracted {len(extracted)} item(s) → {args.output.resolve()}")
            for name in extracted:
                print(f"  {name}")
            return 0

        if args.command == "list":
            names = list_archive_members(args.archive, args.unpacker)
            print("(empty)" if not names else "\n".join(names))
            return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
