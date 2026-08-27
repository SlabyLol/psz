#!/usr/bin/env bash
# Load the same demo.psz with Python, PHP, and Node
set -euo pipefail
cd "$(dirname "$0")"
bash run-python.sh
bash run-php.sh
bash run-js.sh
echo ""
echo "Browser: open examples/demo.psz-data.html.lor and select demo.psz"
