#!/usr/bin/env bash
# Extract frames from a video into a directory of PNGs.
#
# Usage:
#   ./extract_frames.sh <input_video> <output_dir> [--every N] [--fps N]
#
# Examples:
#   ./extract_frames.sh ../../cultural-content/ellis-island-clips/ellis-island-1903-web.mp4 ./frames
#   ./extract_frames.sh input.mp4 ./frames --every 10     # every 10th frame (for test runs)
#   ./extract_frames.sh input.mp4 ./frames --fps 12       # force 12fps sampling
#
# Output filenames are zero-padded so reassembly keeps the correct order:
#   frame_000001.png, frame_000002.png, ...

set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: $0 <input_video> <output_dir> [--every N] [--fps N]" >&2
  exit 1
fi

INPUT="$1"
OUTDIR="$2"
shift 2

MODE="all"
VALUE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --every) MODE="every"; VALUE="$2"; shift 2 ;;
    --fps)   MODE="fps";   VALUE="$2"; shift 2 ;;
    *) echo "unknown option: $1" >&2; exit 1 ;;
  esac
done

mkdir -p "$OUTDIR"
rm -f "$OUTDIR"/frame_*.png

case "$MODE" in
  all)
    ffmpeg -hide_banner -loglevel warning -i "$INPUT" "$OUTDIR/frame_%06d.png"
    ;;
  every)
    ffmpeg -hide_banner -loglevel warning -i "$INPUT" \
      -vf "select=not(mod(n\,$VALUE))" -vsync vfr "$OUTDIR/frame_%06d.png"
    ;;
  fps)
    ffmpeg -hide_banner -loglevel warning -i "$INPUT" \
      -vf "fps=$VALUE" "$OUTDIR/frame_%06d.png"
    ;;
esac

COUNT=$(ls "$OUTDIR"/frame_*.png 2>/dev/null | wc -l | tr -d ' ')
echo "extracted $COUNT frames to $OUTDIR"
