#!/usr/bin/env bash
# Stylize a single mp4 with the Nocturne/PS2 workflow — full-video export.
#
# Usage:
#   ./stylize_video.sh <input.mp4> <output.mp4> [--every N] [--fps N] \
#                      [-- stylize_frame.py args...]
#
# Everything after a bare `--` is forwarded to stylize_frame.py, so you can
# tune --denoise, --lora, --cn, --seed, --mode, etc. per clip. Keep --seed
# fixed across all frames to minimise temporal flicker.

set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
COMFY_IN="$HOME/Documents/ComfyUI/input"
COMFY_OUT="$HOME/Documents/ComfyUI/output"

if [[ $# -lt 2 ]]; then
  echo "usage: $0 <input.mp4> <output.mp4> [--every N|--fps N] [-- stylize args]" >&2
  exit 1
fi

INPUT="$1"; OUTPUT="$2"; shift 2
SAMPLE_ARGS=()
while [[ $# -gt 0 && "$1" != "--" ]]; do
  SAMPLE_ARGS+=("$1"); shift
done
[[ "${1:-}" == "--" ]] && shift
STYLIZE_ARGS=("$@")

NAME="$(basename "${INPUT%.*}")"
WORK="$(mktemp -d -t stylize_${NAME}_XXXX)"
FRAMES_IN="$WORK/in"
FRAMES_OUT="$WORK/out"
mkdir -p "$FRAMES_IN" "$FRAMES_OUT" "$COMFY_IN"

echo ">>> probing $INPUT"
FPS=$(ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate \
              -of csv=p=0 "$INPUT")
FPS_DECIMAL=$(awk -F/ '{printf "%.3f", $1/$2}' <<<"$FPS")
echo "    fps=$FPS_DECIMAL"

echo ">>> extracting frames"
"$HERE/extract_frames.sh" "$INPUT" "$FRAMES_IN" "${SAMPLE_ARGS[@]}"

# Stage frames into ComfyUI input dir under a unique namespace per clip
STAGE_PREFIX="stylize_${NAME}_$$"
for f in "$FRAMES_IN"/frame_*.png; do
  base="$(basename "$f")"
  cp "$f" "$COMFY_IN/${STAGE_PREFIX}_${base}"
done

echo ">>> stylizing $(ls "$FRAMES_IN"/frame_*.png | wc -l) frames"
for f in "$FRAMES_IN"/frame_*.png; do
  base="$(basename "$f" .png)"          # frame_000001
  staged="${STAGE_PREFIX}_${base}.png"
  out_prefix="stylized/${STAGE_PREFIX}/${base}"

  python3 "$HERE/stylize_frame.py" "$staged" \
    --prefix "$out_prefix" "${STYLIZE_ARGS[@]}"

  # Comfy writes output/stylized/STAGE_PREFIX/frame_000001_00001_.png
  produced=$(ls "$COMFY_OUT/stylized/${STAGE_PREFIX}/${base}"_*.png 2>/dev/null | head -n1)
  if [[ -z "$produced" ]]; then
    echo "!! no output for $base" >&2; exit 1
  fi
  cp "$produced" "$FRAMES_OUT/${base}.png"
done

echo ">>> reassembling -> $OUTPUT"
mkdir -p "$(dirname "$OUTPUT")"
"$HERE/reassemble_frames.sh" "$FRAMES_OUT" "$OUTPUT" --fps "${FPS_DECIMAL%.*}"

# Keep audio from the original
TMP_MUXED="${OUTPUT%.mp4}.muxed.mp4"
ffmpeg -hide_banner -loglevel warning -y \
  -i "$OUTPUT" -i "$INPUT" \
  -map 0:v:0 -map 1:a:0? -c copy -shortest "$TMP_MUXED" \
  && mv "$TMP_MUXED" "$OUTPUT" || echo "  (no audio track to mux)"

echo ">>> cleanup"
rm -rf "$WORK"
rm -f "$COMFY_IN/${STAGE_PREFIX}_"*.png
rm -rf "$COMFY_OUT/stylized/${STAGE_PREFIX}"

echo "done: $OUTPUT"
