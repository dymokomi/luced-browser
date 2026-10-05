#!/bin/sh
# luced-browser's checks: every Luce module formatted, the headless tests built and run (the
# engine for real, no window). `./test.sh --diagnostic` builds them with the diagnostic profile.
set -e
cd "$(dirname "$0")"
echo "== luce fmt --check"
for file in src/*.luc tests/*.luc; do
    luce fmt "$file" --check > /dev/null || { echo "$file is not formatted (luce fmt $file --write)"; exit 1; }
done
echo "== luce-base fmt --check"
for file in src/*.lucb tests/*.lucb; do
    luce-base fmt "$file" --check > /dev/null || { echo "$file is not formatted (luce-base fmt $file --write)"; exit 1; }
done
echo "== headless tests"
python3 tests/run.py "$@"
