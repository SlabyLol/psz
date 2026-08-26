#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 demo.psz-data.lor demo.psz -o out-python
echo "Done → out-python/"
ls -la out-python/
