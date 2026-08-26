#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
bash run-python.sh
bash run-php.sh
bash run-js.sh
echo ""
echo "HTML: open examples/demo.psz-data.html in a browser and select demo.psz"
