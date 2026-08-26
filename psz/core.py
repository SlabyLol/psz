"""
Core logic for creating and opening PSZ archives.

.psz              = AES-256-GCM encrypted tar archive
.psz-data.lor     = Python unpacker (key embedded)
.psz-data.php     = PHP unpacker (key embedded)
.psz-data.html    = Browser (HTML+JS) unpacker (key embedded)
"""

from __future__ import annotations

import io
import os
import tarfile
from pathlib import Path
from typing import Iterable, Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .unpackers import (
    _generate_python_lor,
    _generate_php_lor,
    _generate_js_lor,
    _generate_html_lor,
)

MAGIC = b"PSZ1"
VERSION = 1
NONCE_SIZE = 12
KEY_SIZE = 32  # AES-256

SUPPORTED_LANGUAGES = ("python", "php", "js", "html")


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


def _lor_path_for(output_psz: Path, lang: str) -> Path:
    """Default path for a language-specific unpacker next to the .psz."""
    if lang == "python":
        return Path(str(output_psz) + "-data.lor")
    if lang == "php":
        return Path(str(output_psz) + "-data.php")
    if lang == "js":
        return Path(str(output_psz) + "-data.js")
    if lang == "html":
        return Path(str(output_psz) + "-data.html")
    raise ValueError(f"Unsupported language: {lang}")


def create_archive(
    source: Path,
    output_psz: Path,
    lor_path: Optional[Path] = None,
    languages: Optional[Iterable[str]] = None,
) -> tuple[Path, list[Path]]:
    """
    Create an encrypted .psz archive and matching unpackers.

    languages: iterable of "python", "php", "js", "html". Default: all.
    lor_path: only used when a single language is requested (legacy).

    Returns (psz_path, list_of_unpacker_paths)
    """
    source = source.resolve()
    if not source.is_dir():
        raise ValueError(f"Source must be a directory: {source}")

    output_psz = output_psz.resolve()
    if languages is None:
        languages = list(SUPPORTED_LANGUAGES)
    else:
        languages = [lang.lower().strip() for lang in languages]
        for lang in languages:
            if lang not in SUPPORTED_LANGUAGES:
                raise ValueError(
                    f"Unsupported language '{lang}'. "
                    f"Supported: {', '.join(SUPPORTED_LANGUAGES)}"
                )

    plain = _pack_directory(source)

    key = AESGCM.generate_key(bit_length=256)
    aesgcm = AESGCM(key)
    nonce = os.urandom(NONCE_SIZE)
    ciphertext = aesgcm.encrypt(nonce, plain, None)

    with open(output_psz, "wb") as f:
        f.write(MAGIC)
        f.write(bytes([VERSION]))
        f.write(nonce)
        f.write(ciphertext)

    key_hex = key.hex()
    archive_name = output_psz.name
    unpackers: list[Path] = []

    for lang in languages:
        if lor_path is not None and len(languages) == 1:
            path = lor_path.resolve()
        else:
            path = _lor_path_for(output_psz, lang)

        if lang == "python":
            content = _generate_python_lor(key_hex, archive_name)
            path.write_text(content, encoding="utf-8")
            try:
                os.chmod(path, 0o755)
            except OSError:
                pass
        elif lang == "php":
            content = _generate_php_lor(key_hex, archive_name)
            path.write_text(content, encoding="utf-8")
        elif lang == "js":
            content = _generate_js_lor(key_hex, archive_name)
            path.write_text(content, encoding="utf-8")
            try:
                os.chmod(path, 0o755)
            except OSError:
                pass
        elif lang == "html":
            content = _generate_html_lor(key_hex, archive_name)
            path.write_text(content, encoding="utf-8")

        unpackers.append(path)

    return output_psz, unpackers


def open_archive(
    psz_path: Path,
    lor_path: Path,
    output_dir: Path,
) -> None:
    """
    Open a .psz archive using a matching unpacker (.lor / .php / .js / .html).
    """
    psz_path = psz_path.resolve()
    lor_path = lor_path.resolve()
    output_dir = output_dir.resolve()

    if not psz_path.is_file():
        raise FileNotFoundError(f"Archive not found: {psz_path}")
    if not lor_path.is_file():
        raise FileNotFoundError(f"Unpacker not found: {lor_path}")

    key = _extract_key_from_unpacker(lor_path)

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
            "Decryption failed. Wrong unpacker file or corrupted archive."
        ) from e

    _unpack_tar(plain, output_dir)


def _extract_key_from_unpacker(path: Path) -> bytes:
    """Parse the key from a generated unpacker (Python / PHP / JS / HTML)."""
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        stripped = line.strip()
        if "KEY_HEX" not in stripped and "key_hex" not in stripped:
            continue
        for quote in ('"', "'"):
            if quote not in stripped:
                continue
            parts = stripped.split(quote)
            for part in parts:
                candidate = part.strip()
                if len(candidate) == 64 and all(
                    c in "0123456789abcdefABCDEF" for c in candidate
                ):
                    return bytes.fromhex(candidate)
    raise ValueError("Could not find KEY_HEX in the unpacker file")
