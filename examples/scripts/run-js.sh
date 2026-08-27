#!/usr/bin/env bash
# Load demo.psz with the Node.js .lor unpacker
set -euo pipefail
cd "$(dirname "$0")/.."
echo "Loading demo.psz via Node (.js.lor)..."
node demo.psz-data.js.lor demo.psz -o out-js
echo "OK → out-js/"
ls -la out-js/
