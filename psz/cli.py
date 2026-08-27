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
            "Always need: .psz + matching .lor unpacker."
        ),
    )
    parser.add_argument("--version", action="version", version=f"psz {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_make = sub.add_parser("make", help="Pack file(s)/dir into .psz + .lor unpackers")
    p_make.add_argument("sources", nargs="+", type=Path, help="File(s) and/or directory")
    p_make.add_argument("-o", "--output", type=Path, required=True, help="Output .psz")
    p_make.add_argument(
        "--lang", "--language", dest="languages", action="append",
        choices=list(SUPPORTED_LANGUAGES) + ["all"], default=None,
        help="python, php, js, html, or all (default: all)",
    )
    p_make.add_argument("--lor", type=Path, default=None, help="Custom single unpacker path")

    p_open = sub.add_parser("open", help="Extract (needs .psz + .lor unpacker)")
    p_open.add_argument("archive", type=Path, help=".psz archive")
    p_open.add_argument("unpacker", type=Path, help="Matching .lor unpacker with the key")
    p_open.add_argument("-o", "--output", type=Path, default=Path("extracted"))
    p_open.add_argument(
        "-m", "--member", dest="members", action="append", default=None,
        help="Extract only this path from inside the archive (repeatable)",
    )

    p_list = sub.add_parser("list", help="List contents (needs .psz + .lor)")
    p_list.add_argument("archive", type=Path)
    p_list.add_argument("unpacker", type=Path)

    args = parser.parse_args(argv)

    try:
        if args.command == "make":
            langs = args.languages
            languages = list(SUPPORTED_LANGUAGES) if (langs is None or "all" in langs) else langs
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
            print("Keep the .psz AND at least one .lor unpacker together.")
            print("Load / extract:")
            for u in unpackers:
                n = u.name
                if n.endswith(".php.lor"):
                    print(f"  php {n} {psz_path.name} -o out/")
                elif n.endswith(".js.lor"):
                    print(f"  node {n} {psz_path.name} -o out/")
                elif n.endswith(".html.lor"):
                    print(f"  open {n} in browser → select {psz_path.name}")
                elif n.endswith(".lor"):
                    print(f"  python {n} {psz_path.name} -o out/")
            print(f"  psz open {psz_path.name} <unpacker.lor> -o out/")
            print(f"  psz list {psz_path.name} <unpacker.lor>")
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
