#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
php demo.psz-data.php demo.psz -o out-php
echo "Done → out-php/"
ls -la out-php/
