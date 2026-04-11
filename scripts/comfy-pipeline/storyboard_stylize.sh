#!/usr/bin/env bash
# Stylize sparse storyboard stills from a single mp4.
# Mirrors the by-hand workflow that produced
# cultural-content/ellis-island-clips/storyboard-stylized/ellis_sb_{N}s_00001_.png
#
# Usage:
#   ./storyboard_stylize.sh <input.mp4> [--stem NAME] [--out DIR] \
#                           [--ts "5 21 37 53 69 85 101 117 133 150"] \
#                           [-- stylize_frame.py args...]
#
# Examples:
#   # Reproduce the Ellis Island storyboard exactly (default timestamps).
#   ./storyboard_stylize.sh ../../cultural-content/ellis-island-clips/ellis-island-1903-web.mp4
#
#   # Tune: lower denoise, bump LoRA, fixed seed for A/B against the reference.
#   ./storyboard_stylize.sh input.mp4 --stem test_v2 -- --denoise 0.6 --lora 0.9 --seed 42
#
#   # Different clip, custom timestamps.
#   ./storyboard_stylize.sh around-the-world-ny-1940.mp4 \
#       --stem ny1940_sb --ts "3 12 28 44 60" -- --denoise 0.65

set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
COMFY_IN="$HOME/Documents/ComfyUI/input"
COMFY_OUT="$HOME/Documents/ComfyUI/output"

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <input.mp4> [--stem NAME] [--out DIR] [--ts \"5 21 ...\"] [-- stylize args]" >&2
  exit 1
fi

INPUT="$1"; shift
STEM=""
OUTDIR=""
TIMESTAMPS="5 21 37 53 69 85 101 117 133 150"   # matches existing reference set
STYLIZE_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --stem) STEM="$2"; shift 2 ;;
    --out)  OUTDIR="$2"; shift 2 ;;
    --ts)   TIMESTAMPS="$2"; shift 2 ;;
    --)     shift; STYLIZE_ARGS=("$@"); break ;;
    *)      echo "unknown option: $1" >&2; exit 1 ;;
  esac
done

: "${STEM:=$(basename "${INPUT%.*}")_sb}"
: "${OUTDIR:=out/storyboard/${STEM}}"
mkdir -p "$OUTDIR" "$COMFY_IN"

echo ">>> storyboard: $INPUT"
echo "    stem=$STEM  out=$OUTDIR  ts=[$TIMESTAMPS]"
echo "    stylize_frame args: ${STYLIZE_ARGS[*]:-(defaults)}"

for T in $TIMESTAMPS; do
  STAGED="${STEM}_${T}s.png"
  echo ">>> extract t=${T}s -> $STAGED"
  ffmpeg -hide_banner -loglevel warning -y \
    -ss "$T" -i "$INPUT" -frames:v 1 \
    "$COMFY_IN/$STAGED"

  PREFIX="${STEM}_${T}s"
  echo ">>> stylize $STAGED (prefix=$PREFIX)"
  python3 "$HERE/stylize_frame.py" "$STAGED" \
    --prefix "$PREFIX" "${STYLIZE_ARGS[@]}"

  # Comfy saves as output/<prefix>_NNNNN_.png — grab the newest match.
  PRODUCED=$(ls -t "$COMFY_OUT/${PREFIX}"_*.png 2>/dev/null | head -n1)
  if [[ -z "$PRODUCED" ]]; then
    echo "!! no output for t=${T}s" >&2; exit 1
  fi
  cp "$PRODUCED" "$OUTDIR/"
  rm -f "$COMFY_IN/$STAGED"
done

echo ""
echo "done: $OUTDIR"
ls -1 "$OUTDIR"
