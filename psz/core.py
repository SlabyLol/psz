"""
Core logic for PSZ archives.
.psz = AES-256-GCM encrypted tar
Unpacker is always named *.psz-data.lor (language via --lang)
"""
from __future__ import annotations
import io, os, tarfile
from pathlib import Path
from typing import Iterable, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from .unpackers import (
    _generate_python_lor, _generate_php_lor, _generate_js_lor, _generate_html_lor,
)

MAGIC, VERSION, NONCE_SIZE = b"PSZ1", 1, 12
SUPPORTED_LANGUAGES = ("python", "php", "js", "html")

def _is_safe_member(name: str) -> bool:
    return bool(name) and not name.startswith("/") and ".." not in Path(name).parts

def _pack_paths(sources: list[Path]) -> bytes:
    if not sources:
        raise ValueError("No source paths given")
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        for source in sources:
            source = source.resolve()
            if not source.exists():
                raise FileNotFoundError(f"Source not found: {source}")
            if source.is_file():
                tar.add(source, arcname=source.name, recursive=False)
            elif source.is_dir():
                for root, dirs, files in os.walk(source):
                    for name in files:
                        full = Path(root) / name
                        tar.add(full, arcname=str(full.relative_to(source)), recursive=False)
                    for name in dirs:
                        full = Path(root) / name
                        try:
                            tar.add(full, arcname=str(full.relative_to(source)), recursive=False)
                        except Exception:
                            pass
            else:
                raise ValueError(f"Not a file or directory: {source}")
    return buf.getvalue()

def _pack_directory(source: Path) -> bytes:
    return _pack_paths([source])

def _unpack_tar(data: bytes, dest: Path, members: Optional[list[str]] = None) -> list[str]:
    dest.mkdir(parents=True, exist_ok=True)
    extracted, wanted = [], set(members) if members else None
    with tarfile.open(fileobj=io.BytesIO(data), mode="r") as tar:
        for member in tar.getmembers():
            if not _is_safe_member(member.name):
                continue
            if wanted is not None:
                ok = member.name in wanted or any(
                    member.name == m or member.name.startswith(m.rstrip("/") + "/")
                    for m in wanted
                )
                if not ok:
                    continue
            tar.extract(member, path=dest)
            extracted.append(member.name)
    return extracted

def _lor_path_for(output_psz: Path, lang: str) -> Path:
    """Always the same name for compatibility: <archive>.psz-data.lor"""
    if lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {lang}")
    return Path(str(output_psz) + "-data.lor")

def _extract_key_from_unpacker(path: Path) -> bytes:
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if "KEY_HEX" not in line and "key_hex" not in line:
            continue
        for quote in ('"', "'"):
            if quote not in line:
                continue
            for part in line.split(quote):
                c = part.strip()
                if len(c) == 64 and all(ch in "0123456789abcdefABCDEF" for ch in c):
                    return bytes.fromhex(c)
    raise ValueError("Could not find KEY_HEX in the unpacker file")

def _decrypt_psz(psz_path: Path, lor_path: Path) -> bytes:
    psz_path, lor_path = psz_path.resolve(), lor_path.resolve()
    if not psz_path.is_file():
        raise FileNotFoundError(f"Archive not found: {psz_path}")
    if not lor_path.is_file():
        raise FileNotFoundError(f"Unpacker not found: {lor_path}")
    key = _extract_key_from_unpacker(lor_path)
    data = psz_path.read_bytes()
    if not data.startswith(MAGIC):
        raise ValueError("Not a valid PSZ archive (bad magic)")
    if data[4] != VERSION:
        raise ValueError(f"Unsupported PSZ version: {data[4]}")
    nonce, ciphertext = data[5:5+NONCE_SIZE], data[5+NONCE_SIZE:]
    try:
        return AESGCM(key).decrypt(nonce, ciphertext, None)
    except Exception as e:
        raise ValueError("Decryption failed. Wrong unpacker or corrupted archive.") from e

def list_archive_members(psz_path: Path, lor_path: Path) -> list[str]:
    plain = _decrypt_psz(psz_path, lor_path)
    names = []
    with tarfile.open(fileobj=io.BytesIO(plain), mode="r") as tar:
        for m in tar.getmembers():
            if _is_safe_member(m.name):
                names.append(m.name)
    return names

def create_archive(
    source: Path | list[Path],
    output_psz: Path,
    lor_path: Optional[Path] = None,
    languages: Optional[Iterable[str]] = None,
) -> tuple[Path, list[Path]]:
    sources = [source.resolve()] if isinstance(source, Path) else [Path(p).resolve() for p in source]
    for s in sources:
        if not s.exists():
            raise FileNotFoundError(f"Source not found: {s}")
        if not (s.is_dir() or s.is_file()):
            raise ValueError(f"Source must be a file or directory: {s}")
    output_psz = output_psz.resolve()
    if languages is None:
        languages = ["python"]
    else:
        languages = [x.lower().strip() for x in languages]
        for lang in languages:
            if lang not in SUPPORTED_LANGUAGES:
                raise ValueError(f"Unsupported language '{lang}'. Supported: {', '.join(SUPPORTED_LANGUAGES)}")
    if len(languages) > 1:
        raise ValueError(
            "Only one unpacker language per archive when using the standard "
            "name *.psz-data.lor. Use e.g. --lang php  or  --lang python"
        )
    plain = _pack_paths(sources)
    key = AESGCM.generate_key(bit_length=256)
    nonce = os.urandom(NONCE_SIZE)
    ciphertext = AESGCM(key).encrypt(nonce, plain, None)
    with open(output_psz, "wb") as f:
        f.write(MAGIC + bytes([VERSION]) + nonce + ciphertext)
    key_hex, archive_name = key.hex(), output_psz.name
    lang = languages[0]
    gens = {"python": _generate_python_lor, "php": _generate_php_lor, "js": _generate_js_lor, "html": _generate_html_lor}
    path = lor_path.resolve() if lor_path is not None else _lor_path_for(output_psz, lang)
    path.write_text(gens[lang](key_hex, archive_name), encoding="utf-8")
    if lang in ("python", "js"):
        try:
            os.chmod(path, 0o755)
        except OSError:
            pass
    return output_psz, [path]

def open_archive(
    psz_path: Path,
    lor_path: Path,
    output_dir: Path,
    members: Optional[list[str]] = None,
) -> list[str]:
    plain = _decrypt_psz(psz_path, lor_path)
    return _unpack_tar(plain, output_dir.resolve(), members=members)
