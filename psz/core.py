"""
Core logic for creating and opening PSZ archives.

.psz          = AES-256-GCM encrypted tar archive
.psz-data.lor = self-contained Python unpacker script that holds the key
"""

from __future__ import annotations

import io
import os
import tarfile
from pathlib import Path
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


MAGIC = b"PSZ1"
VERSION = 1
NONCE_SIZE = 12
KEY_SIZE = 32  # AES-256


def _pack_directory(source: Path) -> bytes:
    """Create an in-memory tar archive of the source directory."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        for root, dirs, files in os.walk(source):
            for name in files:
                full = Path(root) / name
                arcname = full.relative_to(source)
                tar.add(full, arcname=str(arcname), recursive=False)
            for name in dirs:
                full = Path(root) / name
                arcname = full.relative_to(source)
                try:
                    tar.add(full, arcname=str(arcname), recursive=False)
                except Exception:
                    pass
    return buf.getvalue()


def _unpack_tar(data: bytes, dest: Path) -> None:
    """Extract a tar archive (bytes) into dest directory."""
    dest.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO(data)
    with tarfile.open(fileobj=buf, mode="r") as tar:
        def is_safe(member: tarfile.TarInfo) -> bool:
            name = member.name
            if name.startswith("/") or ".." in Path(name).parts:
                return False
            return True

        for member in tar.getmembers():
            if is_safe(member):
                tar.extract(member, path=dest)


def create_archive(
    source: Path,
    output_psz: Path,
    lor_path: Optional[Path] = None,
) -> tuple[Path, Path]:
    """
    Create an encrypted .psz archive and a matching .psz-data.lor unpacker.

    Returns (psz_path, lor_path)
    """
    source = source.resolve()
    if not source.is_dir():
        raise ValueError(f"Source must be a directory: {source}")

    output_psz = output_psz.resolve()
    if lor_path is None:
        lor_path = output_psz.with_suffix(output_psz.suffix + "-data.lor")
    else:
        lor_path = lor_path.resolve()

    # 1. Pack
    plain = _pack_directory(source)

    # 2. Encrypt
    key = AESGCM.generate_key(bit_length=256)
    aesgcm = AESGCM(key)
    nonce = os.urandom(NONCE_SIZE)
    ciphertext = aesgcm.encrypt(nonce, plain, None)

    # 3. Write .psz
    # Format: MAGIC (4) + VERSION (1) + nonce (12) + ciphertext
    with open(output_psz, "wb") as f:
        f.write(MAGIC)
        f.write(bytes([VERSION]))
        f.write(nonce)
        f.write(ciphertext)

    # 4. Generate self-contained .lor unpacker script
    key_hex = key.hex()
    lor_content = _generate_lor_script(key_hex, output_psz.name)

    with open(lor_path, "w", encoding="utf-8") as f:
        f.write(lor_content)

    try:
        os.chmod(lor_path, 0o755)
    except OSError:
        pass

    return output_psz, lor_path


def open_archive(
    psz_path: Path,
    lor_path: Path,
    output_dir: Path,
) -> None:
    """
    Open a .psz archive using the matching .psz-data.lor.
    The .lor must contain the correct key for this archive.
    """
    psz_path = psz_path.resolve()
    lor_path = lor_path.resolve()
    output_dir = output_dir.resolve()

    if not psz_path.is_file():
        raise FileNotFoundError(f"Archive not found: {psz_path}")
    if not lor_path.is_file():
        raise FileNotFoundError(f"Unpacker not found: {lor_path}")

    key = _extract_key_from_lor(lor_path)

    with open(psz_path, "rb") as f:
        data = f.read()

    if not data.startswith(MAGIC):
        raise ValueError("Not a valid PSZ archive (bad magic)")

    version = data[4]
    if version != VERSION:
        raise ValueError(f"Unsupported PSZ version: {version}")

    nonce = data[5 : 5 + NONCE_SIZE]
    ciphertext = data[5 + NONCE_SIZE :]

    aesgcm = AESGCM(key)
    try:
        plain = aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as e:
        raise ValueError(
            "Decryption failed. Wrong .lor file or corrupted archive."
        ) from e

    _unpack_tar(plain, output_dir)


def _extract_key_from_lor(lor_path: Path) -> bytes:
    """Parse the key out of a generated .lor script."""
    text = lor_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("KEY_HEX"):
            parts = line.split("=", 1)
            if len(parts) == 2:
                raw = parts[1].strip().strip('"').strip("'")
                return bytes.fromhex(raw)
    raise ValueError("Could not find KEY_HEX in the .lor file")


def _generate_lor_script(key_hex: str, archive_name: str) -> str:
    """Generate a self-contained Python unpacker script."""
    return f'''#!/usr/bin/env python3
"""
PSZ Data Loader / Unpacker
This file was generated specifically for the archive: {archive_name}

Usage:
    python {Path(archive_name).stem}.psz-data.lor {archive_name} -o output_dir

Or with the main psz tool:
    psz open {archive_name} this_file.lor -o output_dir
"""

from __future__ import annotations

import argparse
import io
import os
import sys
import tarfile
from pathlib import Path

# Embedded key for this specific archive (do not share publicly if sensitive)
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

    # Extract
    output_dir.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO(plain)
    with tarfile.open(fileobj=buf, mode="r") as tar:
        for member in tar.getmembers():
            name = member.name
            if name.startswith("/") or ".." in Path(name).parts:
                continue  # skip unsafe paths
            tar.extract(member, path=output_dir)

    print(f"Successfully extracted to: {{output_dir}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
