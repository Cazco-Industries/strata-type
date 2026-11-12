#!/bin/sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
exec python3 -I scripts/resource_guard.py -- python3 -I scripts/fetch_upstream.py
