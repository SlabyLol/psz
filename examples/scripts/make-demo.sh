#!/usr/bin/env bash
# Create demo.psz + demo.psz-data.lor from sample-project
set -euo pipefail
cd "$(dirname "$0")/../.."
export PYTHONPATH="${PYTHONPATH:-.}"
python3 -m psz make examples/sample-project -o examples/demo.psz
python3 -m psz make examples/single-file.txt -o examples/single.psz --lang python
echo "Created examples/demo.psz and examples/single.psz"
ls -la examples/demo.psz examples/demo.psz-data.lor examples/single.psz examples/single.psz-data.lor
