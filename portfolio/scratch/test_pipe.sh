#!/usr/bin/env bash
set -eo pipefail
echo "Starting test..."
x=$(find /usr/bin -maxdepth 1 | sort | sed -n '1p')
echo "Result: $x"
echo "Done."
