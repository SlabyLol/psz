#!/usr/bin/env bash
# Load demo.psz with the Python .lor unpacker
set -euo pipefail
cd "$(dirname "$0")/.."
echo "Loading demo.psz via Python (.lor)..."
python3 demo.psz-data.lor demo.psz -o out-python
echo "OK → out-python/"
ls -la out-python/
