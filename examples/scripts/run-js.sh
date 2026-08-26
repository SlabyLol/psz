#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
node demo.psz-data.js demo.psz -o out-js
echo "Done → out-js/"
ls -la out-js/
