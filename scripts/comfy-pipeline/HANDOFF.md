# Comfy Stylization — Handoff

Copy-paste message for the colleague running the NVIDIA Linux box.

---

On the Linux box:

```bash
git clone https://github.com/TheApexWu/sixth-borough.git
cd sixth-borough
git checkout feature/sketch-overlay
./scripts/comfy-pipeline/setup-comfy-linux.sh
```

Then `scp` me the `3DRenderStyle_SD15.safetensors` LoRA from your Mac into `~/comfy/ComfyUI/models/loras/` — the setup script will warn if it's missing, and ComfyUI errors on the first frame without it.

**Phase 1 (style tuning on stills):**

```bash
./scripts/comfy-pipeline/storyboard_stylize.sh \
    cultural-content/ellis-island-clips/ellis-island-1903-web.mp4 \
    --stem ellis_sb_baseline -- --seed 12345
```

Compare the 10 PNGs in `out/storyboard/ellis_sb_baseline/` against `cultural-content/ellis-island-clips/storyboard-stylized/` (the Mac reference). If it matches, good. If not, try `--denoise 0.6` / `--lora 1.0` with a new `--stem` and compare again — keep `--seed 12345` fixed so only the param under test changes.

**Phase 2 (full video, only after phase 1 looks right):**

```bash
./scripts/comfy-pipeline/stylize_video.sh \
    cultural-content/ellis-island-clips/ellis-island-1903-web.mp4 \
    out/styled/ellis-1903-styled.mp4 \
    -- --denoise 0.7 --lora 0.8 --seed 12345
```

(Substitute whatever params locked in during phase 1.)

**Context:** pipeline applies a Shin Megami Tensei Nocturne / PS2 low-poly look per `styleguide.md` Mode B (Encounter). Stack is DreamShaper 8 + 3DRenderStyle LoRA + Canny ControlNet img2img at denoise 0.70. ComfyUI is expected on `127.0.0.1:8000` — the port is hardcoded in `stylize_frame.py`, don't change it.
