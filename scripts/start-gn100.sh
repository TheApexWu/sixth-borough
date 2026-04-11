#!/usr/bin/env bash
# Sixth Borough — start the Nemotron narration server (GN100 only)
#
# !!! THIS SCRIPT IS FOR THE GN100 BOX ONLY !!!
# Requires Nemotron-3-Nano-30B-A3B (~38 GB) + llama.cpp built with sm_121
# CUDA arch flags. Run scripts/setup-gn100.sh first.
#
# If you're a teammate developing on your laptop, use scripts/dev-stub.sh
# instead - the stub serves the same OpenAI-compatible API on the same
# port (:30000), so the renderer code never has to know which backend is
# wired.

set -euo pipefail

LLAMA_DIR="${HOME}/llama.cpp"
MODEL_PATH="${HOME}/models/nemotron3-gguf/Nemotron-3-Nano-30B-A3B-UD-Q8_K_XL.gguf"

if [ ! -f "${MODEL_PATH}" ]; then
  echo "ERROR: Model not found at ${MODEL_PATH}"
  echo "Run ./scripts/setup-gn100.sh first."
  exit 1
fi

if [ ! -x "${LLAMA_DIR}/build/bin/llama-server" ]; then
  echo "ERROR: llama-server binary not found at ${LLAMA_DIR}/build/bin/llama-server"
  echo "Run ./scripts/setup-gn100.sh first."
  exit 1
fi

echo "==> Starting Nemotron narration server on :30000"
echo "==> Test with: curl http://localhost:30000/v1/chat/completions -H 'Content-Type: application/json' -d '{\"model\":\"nemotron\",\"messages\":[{\"role\":\"user\",\"content\":\"hello\"}]}'"
echo ""

cd "${LLAMA_DIR}/build"
./bin/llama-server \
  --model "${MODEL_PATH}" \
  --host 0.0.0.0 \
  --port 30000 \
  --n-gpu-layers 99 \
  --ctx-size 8192 \
  --threads 8
