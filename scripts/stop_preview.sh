#!/usr/bin/env bash
set -euo pipefail

PREVIEW_DIR="${PREVIEW_DIR:-${TMPDIR:-/tmp}/ascend-interface-docs-preview}"
PID_FILE="$PREVIEW_DIR/server.pid"

if [[ ! -f "$PID_FILE" ]]; then
  echo "no preview server pid file: $PID_FILE"
  exit 0
fi

PID="$(cat "$PID_FILE")"
if [[ -n "$PID" ]] && kill -0 "$PID" 2>/dev/null; then
  kill "$PID"
  echo "stopped preview server: $PID"
else
  echo "preview server is not running: $PID"
fi
rm -f "$PID_FILE"
