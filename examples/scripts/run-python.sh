#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
echo "Loading demo.psz via demo.psz-data.lor..."
python3 demo.psz-data.lor demo.psz -o out-python
echo "OK → out-python/"
ls -la out-python/
