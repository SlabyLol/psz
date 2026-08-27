"""Unpacker generator."""
from pathlib import Path

def _generate_python_lor(key_hex: str, archive_name: str) -> str:
    """Generate a self-contained Python unpacker script."""
    return f'''#!/usr/bin/env python3
"""
PSZ Unpacker (Python) - generated for: {archive_name}
Usage: python {Path(archive_name).stem}.psz-data.lor {archive_name} -o output_dir
"""
from __future__ import annotations
import argparse, io, sys, tarfile
from pathlib import Path
KEY_HEX = "{key_hex}"
MAGIC = b"PSZ1"
NONCE_SIZE = 12

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("archive", type=Path)
    p.add_argument("-o", "--output", type=Path, default=Path("extracted"))
    args = p.parse_args()
    psz_path, output_dir = args.archive.resolve(), args.output.resolve()
    if not psz_path.is_file():
        print(f"Error: archive not found: {{psz_path}}", file=sys.stderr); return 1
    key = bytes.fromhex(KEY_HEX)
    data = psz_path.read_bytes()
    if not data.startswith(MAGIC):
        print("Error: not a valid PSZ archive", file=sys.stderr); return 1
    nonce, ciphertext = data[5:5+NONCE_SIZE], data[5+NONCE_SIZE:]
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        plain = AESGCM(key).decrypt(nonce, ciphertext, None)
    except ImportError:
        print("Error: pip install cryptography", file=sys.stderr); return 1
    except Exception:
        print("Error: decryption failed", file=sys.stderr); return 1
    output_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(plain), mode="r") as tar:
        for m in tar.getmembers():
            if m.name.startswith("/") or ".." in Path(m.name).parts: continue
            tar.extract(m, path=output_dir)
    print(f"Successfully extracted to: {{output_dir}}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
'''
