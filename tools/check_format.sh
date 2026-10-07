#!/bin/sh
# Lint, not a test: every Luce and Luce Base module here is formatted (`luc test` runs the tests).
set -e
cd "$(dirname "$0")/.."
for file in $(find src tests -name '*.luc'); do
    luce fmt "$file" --check > /dev/null || { echo "$file is not formatted (luce fmt $file --write)"; exit 1; }
done
for file in $(find src tests -name '*.lucb'); do
    luce-base fmt "$file" --check > /dev/null || { echo "$file is not formatted (luce-base fmt $file --write)"; exit 1; }
done
echo "formatted"
