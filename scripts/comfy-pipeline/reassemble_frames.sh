#!/usr/bin/env bash
# Reassemble a directory of stylized PNG frames back into an MP4.
#
# Usage:
#   ./reassemble_frames.sh <frames_dir> <output_video> [--fps N]
#
# Defaults to 25 fps (matches ffprobe reading of the 1903 LOC source).
# Expects zero-padded names like frame_000001.png that sort lexicographically.

set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: $0 <frames_dir> <output_video> [--fps N]" >&2
  exit 1
fi

FRAMES="$1"
OUTPUT="$2"
shift 2

FPS=25

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fps) FPS="$2"; shift 2 ;;
    *) echo "unknown option: $1" >&2; exit 1 ;;
  esac
done

ffmpeg -hide_banner -loglevel warning -y \
  -framerate "$FPS" \
  -i "$FRAMES/frame_%06d.png" \
  -c:v libx264 -pix_fmt yuv420p -crf 22 -preset medium \
  -movflags +faststart \
  "$OUTPUT"

echo "wrote $OUTPUT"
