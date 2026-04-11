#!/usr/bin/env bash
# Provision a fresh Ubuntu + NVIDIA box to run the sixth-borough Comfy pipeline.
# Assumes: nvidia-smi works, sudo available, python3.11+.
set -euo pipefail

sudo apt-get update
sudo apt-get install -y python3-venv python3-pip git ffmpeg wget

# 1. comfy-cli in an isolated venv
python3 -m venv ~/comfy-env
source ~/comfy-env/bin/activate
pip install --upgrade pip
pip install comfy-cli

# 2. Install ComfyUI (CUDA 12.1 wheels). Default path: ~/comfy/ComfyUI
comfy --skip-prompt install --nvidia --cuda-version 12.1

# 3. Make the Mac-ism in stylize_frame.py work on Linux without edits.
#    stylize_frame.py references ~/Documents/ComfyUI/{input,output}.
mkdir -p ~/Documents
ln -sfn ~/comfy/ComfyUI ~/Documents/ComfyUI

# 4. Models — exact filenames stylize_frame.py defaults to.
COMFY=~/comfy/ComfyUI

# DreamShaper 8 (SD1.5 checkpoint)
wget -c -O "$COMFY/models/checkpoints/dreamshaper_8.safetensors" \
  "https://huggingface.co/Lykon/DreamShaper/resolve/main/DreamShaper_8_pruned.safetensors"

# ControlNet Canny for SD1.5
wget -c -O "$COMFY/models/controlnet/control_v11p_sd15_canny.pth" \
  "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_canny.pth"

# 3D Render Style LoRA — not auto-downloaded. scp it from the Mac, or wget
# from Civitai with an API token, to:
#   $COMFY/models/loras/3DRenderStyle_SD15.safetensors
if [ ! -f "$COMFY/models/loras/3DRenderStyle_SD15.safetensors" ]; then
  echo "!! MISSING: $COMFY/models/loras/3DRenderStyle_SD15.safetensors" >&2
  echo "   Copy it from the Mac before running the pipeline." >&2
fi

# 5. Launch ComfyUI on :8000 (matches COMFY_URL in stylize_frame.py)
comfy launch --background -- --listen 0.0.0.0 --port 8000
sleep 4
curl -sf http://127.0.0.1:8000/system_stats | head -c 400 && echo
echo "OK — ComfyUI listening on :8000"
