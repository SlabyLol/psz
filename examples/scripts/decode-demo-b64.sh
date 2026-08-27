#!/usr/bin/env bash
# Rebuild demo.psz from base64 parts on GitHub
set -euo pipefail
cd "$(dirname "$0")/.."
cat demo.psz.b64.part0 demo.psz.b64.part1 demo.psz.b64.part2 | base64 -d > demo.psz
echo "Wrote demo.psz ($(wc -c < demo.psz) bytes)"
python3 -c "import pathlib; d=pathlib.Path('demo.psz').read_bytes(); assert d[:4]==b'PSZ1', d[:4]; print('PSZ1 OK')"
