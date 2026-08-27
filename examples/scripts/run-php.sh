#!/usr/bin/env bash
# Load demo.psz with the PHP .lor unpacker
set -euo pipefail
cd "$(dirname "$0")/.."
echo "Loading demo.psz via PHP (.php.lor)..."
php demo.psz-data.php.lor demo.psz -o out-php
echo "OK → out-php/"
ls -la out-php/
