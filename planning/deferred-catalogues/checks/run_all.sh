#!/bin/sh
# Every catalogue check, plus the JSON->markdown no-drift guard.
set -e
cd "$(dirname "$0")/.."
for f in *.json; do python3 -c "import json,sys; json.load(open('$f'))" || exit 1; done
echo "all JSON parses"
python3 checks/check01.py
python3 checks/check23.py
python3 checks/check04.py
python3 checks/check05.py
python3 checks/check06.py
python3 checks/check07.py
python3 render.py --check
