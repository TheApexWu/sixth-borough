# Comfy Stylization Pipeline — Operator Brief

This file is written as a handoff brief for an LLM agent operating a fresh
Ubuntu + NVIDIA box that will run ComfyUI. A human can read it too, but the
phrasing assumes you're the agent carrying out the task.

## What you're doing

Applying a Shin Megami Tensei Nocturne / PS2 low-poly look to archival NYC
footage, per `styleguide.md` Mode B ("Encounter" — the user diving into a
memory). Stack is **DreamShaper 8** (SD1.5) + **3DRenderStyle_SD15** LoRA +
**control_v11p_sd15_canny** ControlNet, img2img at denoise 0.70. The style
direction (prompts, negative prompt, defaults) is hardcoded in
`stylize_frame.py` — you do not need to read `styleguide.md` at runtime.

Two phases, in order:

1. **Phase 1 — storyboard stills.** Stylize ~10 sparse frames from a test
   clip, compare against reference PNGs checked into the repo, tune params
   until the look matches.
2. **Phase 2 — full-video export.** Once Phase 1 params are locked, run the
   full-video driver on the same clip, then batch the rest of the directory.

**Do not run Phase 2 without explicit human approval of the Phase 1 output.**

## Environment assumptions

- Fresh Ubuntu (22.04 or 24.04), sudo available.
- `nvidia-smi` works and returns a CUDA-capable GPU. Stop and report if not.
- Python 3.11+, git, internet access to HuggingFace.
- ComfyUI will listen on `127.0.0.1:8000` — **do not change the port**,
  `stylize_frame.py` hardcodes `COMFY_URL = "http://127.0.0.1:8000"`. If 8000
  is occupied, kill the conflicting process rather than switching ports.

## Setup (one-shot)

```bash
git clone https://github.com/TheApexWu/sixth-borough.git
cd sixth-borough
git checkout feature/sketch-overlay
./scripts/comfy-pipeline/setup-comfy-linux.sh
```

`setup-comfy-linux.sh` installs `comfy-cli` in `~/comfy-env`, runs
`comfy install --nvidia`, symlinks `~/Documents/ComfyUI` → `~/comfy/ComfyUI`
(so the Mac-written `stylize_frame.py` finds its input/output dirs without
edits), downloads DreamShaper 8 and the Canny ControlNet, then launches
ComfyUI in the background on port 8000. It ends with a `curl` to
`/system_stats` — verify that response includes a CUDA device.

### Blocker — the LoRA is not auto-downloaded

The `3DRenderStyle_SD15.safetensors` LoRA must be placed at:

```
~/comfy/ComfyUI/models/loras/3DRenderStyle_SD15.safetensors
```

The setup script warns if it's missing. The human operator will either
`scp` it from a Mac, share a download URL, or provide a Civitai API token.
**Do not substitute a different LoRA** — the style fidelity depends on this
specific file. Ask the human for it and wait.

## Phase 1 — storyboard tuning

The reference the human wants you to match lives in the repo at:

```
cultural-content/ellis-island-clips/storyboard-stylized/ellis_sb_{N}s_00001_.png
```

Ten PNGs, one per timestamp (5, 21, 37, 53, 69, 85, 101, 117, 133, 150 seconds).
These were produced on a Mac with the same pipeline and are the ground truth
for "does the style look right".

### Baseline run

```bash
./scripts/comfy-pipeline/storyboard_stylize.sh \
    cultural-content/ellis-island-clips/ellis-island-1903-web.mp4 \
    --stem ellis_sb_baseline \
    -- --seed 12345
```

Outputs go to `out/storyboard/ellis_sb_baseline/`. Compare each output to the
reference of the same timestamp. Report per-frame:

- Does the faceted low-poly / vertex-lighting look come through?
- Is the warm amber accent present (the Ellis Island / immigration niche
  accent per the styleguide)?
- Any obvious regressions vs. the reference (blurring, photorealism, wrong
  palette)?

### Tuning variants (only if baseline is off)

Change **one parameter at a time**. Keep `--seed 12345` fixed so results are
directly A/B-able. Use a distinct `--stem` for each run so outputs don't
clobber each other.

```bash
# Less regeneration, preserve more source detail:
./scripts/comfy-pipeline/storyboard_stylize.sh \
    cultural-content/ellis-island-clips/ellis-island-1903-web.mp4 \
    --stem ellis_sb_lessDenoise -- --seed 12345 --denoise 0.6

# Stronger LoRA push:
./scripts/comfy-pipeline/storyboard_stylize.sh \
    cultural-content/ellis-island-clips/ellis-island-1903-web.mp4 \
    --stem ellis_sb_moreLora -- --seed 12345 --lora 1.0

# Stronger edge lock from ControlNet:
./scripts/comfy-pipeline/storyboard_stylize.sh \
    cultural-content/ellis-island-clips/ellis-island-1903-web.mp4 \
    --stem ellis_sb_strongCN -- --seed 12345 --cn 1.1
```

Cap yourself at **three tuning variants** per session. If none match, stop
and report — don't keep flailing on params.

Stop after Phase 1. Wait for human approval of a specific param set before
proceeding.

## Phase 2 — full-video export

Once the human has locked a param set, run the full-video driver with the
**exact same params** after the `--` separator, including the fixed seed.
Keeping the seed stable across all frames is the single biggest thing you
can do to reduce temporal flicker.

```bash
./scripts/comfy-pipeline/stylize_video.sh \
    cultural-content/ellis-island-clips/ellis-island-1903-web.mp4 \
    out/styled/ellis-1903-styled.mp4 \
    -- --denoise 0.7 --lora 0.8 --seed 12345
```

The driver extracts every frame, stylizes each via `stylize_frame.py`,
reassembles with the original fps, and muxes the original audio back in.
Output is an mp4 at the path you specified.

After the single-clip run succeeds and the human approves the result, batch
the rest:

```bash
./scripts/comfy-pipeline/batch_stylize_videos.sh \
    cultural-content/ellis-island-clips \
    out/styled
```

## Failure modes to watch for

- **LoRA missing** → ComfyUI returns a node error in `/history/<prompt_id>`.
  `stylize_frame.py` raises; the bash driver exits non-zero. Fail fast,
  tell the human, don't substitute.
- **Port 8000 conflict** → `comfy launch` silently picks a different port
  and the whole pipeline fails to connect. Check `ss -ltnp | grep 8000`
  before launch; kill conflicts, don't switch ports.
- **OOM on KSampler** → drop `--steps 15` and retry one frame. If still
  OOM, drop resolution (ask the human, don't guess).
- **Comfy output directory mismatch** → the scripts assume
  `~/Documents/ComfyUI/output`. If the symlink step in setup failed, the
  drivers won't find their outputs. Check `ls -la ~/Documents/ComfyUI`.
- **Per-frame non-determinism** → if `--seed` isn't passed through Phase 2,
  every frame gets a random latent and flicker explodes. Always forward the
  Phase 1 seed.

## Useful references in the repo

- `scripts/comfy-pipeline/stylize_frame.py` — the actual workflow graph,
  hardcoded prompts (`PROMPT_ENCOUNTER`, `PROMPT_OVERWORLD`), all defaults.
  Read this if you need to understand or override anything.
- `scripts/comfy-pipeline/extract_frames.sh`,
  `scripts/comfy-pipeline/reassemble_frames.sh` — ffmpeg helpers that the
  video driver composes.
- `styleguide.md` at the repo root — the human-authored style bible. The
  pipeline does not read it at runtime; treat it as context if the human
  asks you to change the look.
- `cultural-content/ellis-island-clips/storyboard-stylized/` — Phase 1
  reference PNGs. A/B against these.

## Do-not-do list

- Do not change the ComfyUI port from 8000.
- Do not substitute a different LoRA if `3DRenderStyle_SD15.safetensors` is
  missing. Ask for it.
- Do not run Phase 2 without explicit Phase 1 approval.
- Do not change multiple tuning params at once in Phase 1 — single-variable
  A/B only.
- Do not edit `stylize_frame.py`'s hardcoded prompts unless the human
  explicitly asks; use `--prompt` at the CLI for one-off overrides instead.
- Do not push branches or commit anything from the remote box without being
  asked; the pipeline is read-only consumer of the repo.
