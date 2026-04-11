#!/usr/bin/env bash
# Stylize every mp4 in a directory. Use --test for one clip only.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"

if [[ "${1:-}" == "--test" ]]; then
  "$HERE/stylize_video.sh" \
    cultural-content/ellis-island-clips/ellis-island-1903-web.mp4 \
    out/styled/ellis-1903-styled.mp4 \
    --every 2
  exit 0
fi

IN_DIR="${1:-cultural-content/ellis-island-clips}"
OUT_DIR="${2:-out/styled}"
mkdir -p "$OUT_DIR"

for f in "$IN_DIR"/*.mp4; do
  name="$(basename "$f" .mp4)"
  echo "=========================================="
  echo "  $name"
  echo "=========================================="
  "$HERE/stylize_video.sh" "$f" "$OUT_DIR/${name}_styled.mp4"
done
