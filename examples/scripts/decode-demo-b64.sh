#!/usr/bin/env bash
# Decode examples/demo.psz.b64 -> examples/demo.psz (if b64 file is present)
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -f demo.psz.b64 ]]; then
  echo "demo.psz.b64 missing – run: bash scripts/make-demo.sh"
  exit 1
fi
base64 -d demo.psz.b64 > demo.psz
echo "Wrote demo.psz ($(wc -c < demo.psz) bytes)"
