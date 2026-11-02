#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
DOCS_DIR="${DOCS_DIR:-$REPO_ROOT/docs/zh}"
PYTHON="${PYTHON:-python3}"
BUILD_DIR="${BUILD_DIR:-$DOCS_DIR/_build/html}"
GENERATED_DIR="${GENERATED_DIR:-$DOCS_DIR/python-api/generated}"
PREVIEW_DIR="${PREVIEW_DIR:-${TMPDIR:-/tmp}/ascend-interface-docs-preview}"
PORT="${PORT:-8766}"
BIND="${BIND:-127.0.0.1}"
KEEP_BUILD="${KEEP_BUILD:-0}"
SERVE=0

for arg in "$@"; do
  case "$arg" in
    --serve) SERVE=1 ;;
    -h|--help)
      echo "usage: build_preview.sh [--serve]"
      echo "env: REPO_ROOT DOCS_DIR PYTHON BUILD_DIR GENERATED_DIR PREVIEW_DIR PORT BIND KEEP_BUILD"
      exit 0
      ;;
    *) echo "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if ! "$PYTHON" -c "import sphinx" >/dev/null 2>&1; then
  echo "sphinx is not importable by $PYTHON" >&2
  echo "install it with: $PYTHON -m pip install sphinx sphinx_rtd_theme myst_parser" >&2
  exit 1
fi

if [[ ! -d "$DOCS_DIR" ]]; then
  echo "docs directory not found: $DOCS_DIR" >&2
  exit 1
fi

echo "==> build: $DOCS_DIR"
(
  cd "$DOCS_DIR"
  TORCH_DEVICE_BACKEND_AUTOLOAD=0 \
    "$PYTHON" -m sphinx -b html . "$BUILD_DIR" -j auto
)

echo "==> copy: $BUILD_DIR -> $PREVIEW_DIR"
rm -rf "$PREVIEW_DIR"
mkdir -p "$PREVIEW_DIR"
cp -a "$BUILD_DIR/." "$PREVIEW_DIR"/

if [[ "$KEEP_BUILD" != "1" ]]; then
  echo "==> clean: $DOCS_DIR/_build $GENERATED_DIR"
  rm -rf "$DOCS_DIR/_build" "$GENERATED_DIR"
fi

echo "==> preview: $PREVIEW_DIR"
if [[ "$SERVE" == "1" ]]; then
  mkdir -p "$PREVIEW_DIR"
  nohup "$PYTHON" -m http.server "$PORT" --bind "$BIND" \
    --directory "$PREVIEW_DIR" \
    > "$PREVIEW_DIR/server.log" 2>&1 &
  echo $! > "$PREVIEW_DIR/server.pid"
  sleep 1
  echo "PID: $(cat "$PREVIEW_DIR/server.pid")"
  echo "URL: http://127.0.0.1:$PORT/"
  if [[ "$BIND" != "127.0.0.1" ]]; then
    echo "LAN URL: http://<host>:$PORT/"
  fi
else
  echo "HTML copied. Run with --serve to start a local server."
fi
