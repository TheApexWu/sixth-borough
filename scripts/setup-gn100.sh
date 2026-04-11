#!/usr/bin/env bash
# Sixth Borough — GN100-only setup script (DGX Spark / GB10 Grace Blackwell)
#
# !!! THIS SCRIPT IS FOR THE GN100 BOX ONLY !!!
# It downloads a 38 GB model and builds llama.cpp with sm_121 CUDA architecture
# flags that only work on a Blackwell GPU. If you're a teammate developing on
# your laptop, DO NOT run this script. Use scripts/dev-stub.sh instead.
#
# Run this AFTER checking out the box and connecting to wifi.
# Approximate time: 15-20 minutes (mostly the 38 GB Nemotron download)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODELS_DIR="${HOME}/models/nemotron3-gguf"
LLAMA_DIR="${HOME}/llama.cpp"

echo "==> Sixth Borough setup starting"
echo "==> Repo root: ${REPO_ROOT}"
echo "==> Models dir: ${MODELS_DIR}"

# Step 1 — verify prereqs
echo "==> [1/6] Verifying prerequisites"
git --version || { echo "git missing"; exit 1; }
cmake --version || { echo "cmake missing"; exit 1; }
nvcc --version || { echo "nvcc missing"; exit 1; }

# Step 2 — Hugging Face CLI
echo "==> [2/6] Installing Hugging Face CLI"
if [ ! -d "${REPO_ROOT}/.venv" ]; then
  python3 -m venv "${REPO_ROOT}/.venv"
fi
source "${REPO_ROOT}/.venv/bin/activate"
pip install -U "huggingface_hub[cli]"

# Step 3 — clone llama.cpp
echo "==> [3/6] Cloning llama.cpp"
if [ ! -d "${LLAMA_DIR}" ]; then
  git clone https://github.com/ggml-org/llama.cpp "${LLAMA_DIR}"
fi

# Step 4 — build llama.cpp with CUDA targeting GB10 sm_121
echo "==> [4/6] Building llama.cpp with CUDA (~5-10 min)"
cd "${LLAMA_DIR}"
mkdir -p build
cd build
cmake .. -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES="121" -DLLAMA_CURL=OFF
make -j8

# Step 5 — download Nemotron-3-Nano weights (~38 GB)
echo "==> [5/6] Downloading Nemotron-3-Nano-30B-A3B Q8 GGUF (~38 GB)"
echo "==> This is the riskiest step on bad wifi. Download is resumable."
mkdir -p "${MODELS_DIR}"
hf download unsloth/Nemotron-3-Nano-30B-A3B-GGUF \
  Nemotron-3-Nano-30B-A3B-UD-Q8_K_XL.gguf \
  --local-dir "${MODELS_DIR}"

# Step 6 — verify
echo "==> [6/6] Verifying setup"
ls -lh "${MODELS_DIR}"
ls -lh "${LLAMA_DIR}/build/bin/llama-server"

echo ""
echo "==> Setup complete."
echo "==> Next: ./scripts/start-gn100.sh"
