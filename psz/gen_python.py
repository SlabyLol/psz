"""Unpacker generator."""
from pathlib import Path

def _generate_python_lor(key_hex: str, archive_name: str) -> str:
    """Generate a self-contained Python unpacker script."""
    return f'''#!/usr/bin/env python3
"""
PSZ Data Loader / Unpacker (Python)
Generated for archive: {archive_name}

Usage:
    python {Path(archive_name).stem}.psz-data.lor {archive_name} -o output_dir

Or with the main psz tool:
    psz open {archive_name} this_file.lor -o output_dir
"""

from __future__ import annotations

import argparse
import io
import sys
import tarfile
from pathlib import Path

KEY_HEX = "{key_hex}"

MAGIC = b"PSZ1"
NONCE_SIZE = 12


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Unpack a PSZ encrypted archive (paired with this .lor file)"
    )
    parser.add_argument("archive", type=Path, help="Path to the .psz file")
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("extracted"),
        help="Output directory (default: ./extracted)"
    )
    args = parser.parse_args()

    psz_path = args.archive.resolve()
    output_dir = args.output.resolve()

    if not psz_path.is_file():
        print(f"Error: archive not found: {{psz_path}}", file=sys.stderr)
        return 1

    key = bytes.fromhex(KEY_HEX)

    with open(psz_path, "rb") as f:
        data = f.read()

    if not data.startswith(MAGIC):
        print("Error: not a valid PSZ archive", file=sys.stderr)
        return 1

    version = data[4]
    nonce = data[5:5 + NONCE_SIZE]
    ciphertext = data[5 + NONCE_SIZE:]

    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        aesgcm = AESGCM(key)
        plain = aesgcm.decrypt(nonce, ciphertext, None)
    except ImportError:
        print(
            "Error: 'cryptography' package is required.\\n"
            "Install with:  pip install cryptography",
            file=sys.stderr,
        )
        return 1
    except Exception:
        print(
            "Error: decryption failed. "
            "This .lor file does not match the archive or the file is corrupted.",
            file=sys.stderr,
        )
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO(plain)
    with tarfile.open(fileobj=buf, mode="r") as tar:
        for member in tar.getmembers():
            name = member.name
            if name.startswith("/") or ".." in Path(name).parts:
                continue
            tar.extract(member, path=output_dir)

    print(f"Successfully extracted to: {{output_dir}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
