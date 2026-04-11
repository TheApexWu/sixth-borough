#!/usr/bin/env bash
# Start llama.cpp server hosting Nemotron-3-Nano on :8090.
# Run inside tmux session named `llama`. Idempotent: kills any prior server first.
#
#   tmux new -ds llama
#   tmux send-keys -t llama "~/sixth-borough/scripts/start-llama-nano.sh" Enter
#
# Verify the model is loaded:
#   curl -s http://127.0.0.1:8090/v1/models | python3 -m json.tool

set -euo pipefail

GGUF=~/models/nemotron3-gguf/Nemotron-3-Nano-30B-A3B-UD-Q8_K_XL.gguf
LLAMA_BIN=~/llama.cpp/build/bin/llama-server
LOG=/tmp/llama-nano.log
PORT=8090

if [[ ! -f "$GGUF" ]]; then
  echo "ERROR: GGUF missing or download incomplete: $GGUF"
  echo "Check tmux session nano-dl. If still .incomplete, wait."
  exit 1
fi

# Kill any prior llama-server on this port (graceful)
if pgrep -f "llama-server.*--port $PORT" > /dev/null; then
  echo "Killing prior llama-server on :$PORT"
  pkill -TERM -f "llama-server.*--port $PORT" || true
  sleep 2
fi

echo "Starting llama-server with Nano on :$PORT (full GPU offload)"
exec "$LLAMA_BIN" \
  -m "$GGUF" \
  --host 127.0.0.1 \
  --port "$PORT" \
  -ngl 99 \
  -c 8192 \
  --jinja \
  2>&1 | tee "$LOG"
