#!/usr/bin/env python3
"""Send one frame through the Nocturne stylization workflow on ComfyUI.

Workflow: DreamShaper 8 (SD1.5) + 3D Render LoRA + ControlNet Canny, img2img.
Expects the input image to live in ~/Documents/ComfyUI/input/ (that's where
ComfyUI's LoadImage node reads from).

Style direction comes from styleguide.md. The Ellis Island cinematic is a
Mode B (Encounter) moment — the user diving into a memory. Per the guide,
the immigration niche gets a **warm amber** saturated accent against a
muted sepia base. Vertex lighting, faceted polygons, volumetric fog,
256x256 textures, 16-color palette feel, no PBR, no smooth shading.

Usage:
    stylize_frame.py <image_filename> [options]

Examples:
    stylize_frame.py ellis_frame_45s.png
    stylize_frame.py ellis_frame_45s.png --denoise 0.6 --lora 1.0 --cn 0.9
    stylize_frame.py ellis_frame_45s.png --mode overworld
    stylize_frame.py ellis_frame_45s.png --prompt "custom override" --seed 42
"""

import argparse
import json
import os
import random
import sys
import time
import urllib.request
import urllib.parse

COMFY_URL = "http://127.0.0.1:8000"

# Mode B — Encounter (ghost dive). Ellis Island cinematic lives here.
# Immigration niche accent color is warm amber per styleguide.md.
PROMPT_ENCOUNTER = (
    "shin megami tensei nocturne art style, ps2 era low poly 3d rendering, "
    "faceted polygons with vertex lighting, hard shading facets, no smooth shading, "
    "muted desaturated sepia base palette, warm amber accent light, "
    "volumetric atmospheric fog, cool blue shadows, dreamlike memory, "
    "monumental architectural scale, tiny figures dwarfed by scale, "
    "256x256 low resolution textures, 16 color palette, "
    "painted illustration style, cinematic framing, vignette, "
    "period archival footage, ellis island 1903 immigrants arrival, "
    "iconic landmark anchoring the scene"
)

# Mode A — Overworld (map lobby). Not used by the Ellis cinematic, but here
# so the same script can stylize overworld frames later.
PROMPT_OVERWORLD = (
    "shin megami tensei nocturne vortex world, top-down isometric diorama, "
    "pale washed grey white beige palette, cool volumetric fog, "
    "low poly buildings as silhouettes, no surface detail, "
    "district as diorama floating in dark void, atmospheric haze, "
    "vertex lighting only, no per-pixel shading, 256x256 textures, "
    "16 color palette, monumental emptiness, architectural scale dwarfs figures, "
    "painted illustration style, ps2 era rendering"
)

DEFAULT_NEGATIVE = (
    "photorealistic, high detail, sharp, smooth shading, PBR, normal maps, "
    "subsurface scattering, ray tracing, HDR, modern, 4k, 8k, hyperrealistic, "
    "high poly, realistic skin, saturated UI, bright vivid colors, "
    "blurry, noisy, jpeg artifacts, signature, watermark, text"
)


def build_workflow(image: str, prompt: str, negative: str, seed: int,
                   steps: int, cfg: float, denoise: float,
                   lora_strength: float, cn_strength: float,
                   canny_low: float, canny_high: float,
                   checkpoint: str, lora_name: str, controlnet_name: str,
                   out_prefix: str) -> dict:
    """Return the ComfyUI API-format workflow graph."""
    return {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": checkpoint},
        },
        "2": {
            "class_type": "LoraLoader",
            "inputs": {
                "model": ["1", 0],
                "clip": ["1", 1],
                "lora_name": lora_name,
                "strength_model": lora_strength,
                "strength_clip": lora_strength,
            },
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": prompt, "clip": ["2", 1]},
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": negative, "clip": ["2", 1]},
        },
        "5": {
            "class_type": "LoadImage",
            "inputs": {"image": image},
        },
        "6": {
            "class_type": "Canny",
            "inputs": {
                "image": ["5", 0],
                "low_threshold": canny_low,
                "high_threshold": canny_high,
            },
        },
        "7": {
            "class_type": "ControlNetLoader",
            "inputs": {"control_net_name": controlnet_name},
        },
        "8": {
            "class_type": "ControlNetApplyAdvanced",
            "inputs": {
                "positive": ["3", 0],
                "negative": ["4", 0],
                "control_net": ["7", 0],
                "image": ["6", 0],
                "strength": cn_strength,
                "start_percent": 0.0,
                "end_percent": 1.0,
            },
        },
        "9": {
            "class_type": "VAEEncode",
            "inputs": {"pixels": ["5", 0], "vae": ["1", 2]},
        },
        "10": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["2", 0],
                "positive": ["8", 0],
                "negative": ["8", 1],
                "latent_image": ["9", 0],
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": denoise,
            },
        },
        "11": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["10", 0], "vae": ["1", 2]},
        },
        "12": {
            "class_type": "SaveImage",
            "inputs": {"images": ["11", 0], "filename_prefix": out_prefix},
        },
    }


def post_prompt(workflow: dict) -> str:
    body = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(
        f"{COMFY_URL}/prompt",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    if "prompt_id" not in data:
        raise RuntimeError(f"ComfyUI rejected the workflow: {data}")
    return data["prompt_id"]


def wait_for_completion(prompt_id: str, timeout: float = 600) -> dict:
    start = time.time()
    last_status = ""
    while time.time() - start < timeout:
        with urllib.request.urlopen(f"{COMFY_URL}/history/{prompt_id}") as resp:
            history = json.loads(resp.read())
        if prompt_id in history:
            return history[prompt_id]
        # Queue status
        with urllib.request.urlopen(f"{COMFY_URL}/queue") as resp:
            queue = json.loads(resp.read())
        running = queue.get("queue_running", [])
        pending = queue.get("queue_pending", [])
        status = f"running={len(running)} pending={len(pending)}"
        if status != last_status:
            elapsed = time.time() - start
            print(f"[{elapsed:5.1f}s] {status}", flush=True)
            last_status = status
        time.sleep(1.5)
    raise TimeoutError(f"Prompt {prompt_id} did not complete within {timeout}s")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("image", help="Input image filename (must exist in ~/Documents/ComfyUI/input/)")
    p.add_argument("--mode", choices=["encounter", "overworld"], default="encounter",
                   help="Which styleguide mode's default prompt to use. Ignored if --prompt is set.")
    p.add_argument("--prompt", default=None,
                   help="Override prompt. If not set, uses --mode default.")
    p.add_argument("--negative", default=DEFAULT_NEGATIVE)
    p.add_argument("--seed", type=int, default=None, help="Default: random")
    p.add_argument("--steps", type=int, default=20)
    p.add_argument("--cfg", type=float, default=7.5)
    p.add_argument("--denoise", type=float, default=0.70,
                   help="img2img strength. 0=copy, 1=full regeneration. Default 0.70")
    p.add_argument("--lora", dest="lora_strength", type=float, default=0.8)
    p.add_argument("--cn", dest="cn_strength", type=float, default=1.0,
                   help="ControlNet Canny strength")
    p.add_argument("--canny-low", type=float, default=0.3)
    p.add_argument("--canny-high", type=float, default=0.7)
    p.add_argument("--checkpoint", default="dreamshaper_8.safetensors")
    p.add_argument("--lora-name", default="3DRenderStyle_SD15.safetensors")
    p.add_argument("--controlnet", default="control_v11p_sd15_canny.pth")
    p.add_argument("--prefix", default="ellis_stylized")
    args = p.parse_args()

    if args.seed is None:
        args.seed = random.randint(0, 2**31 - 1)
    if args.prompt is None:
        args.prompt = PROMPT_ENCOUNTER if args.mode == "encounter" else PROMPT_OVERWORLD

    workflow = build_workflow(
        image=args.image, prompt=args.prompt, negative=args.negative,
        seed=args.seed, steps=args.steps, cfg=args.cfg, denoise=args.denoise,
        lora_strength=args.lora_strength, cn_strength=args.cn_strength,
        canny_low=args.canny_low, canny_high=args.canny_high,
        checkpoint=args.checkpoint, lora_name=args.lora_name,
        controlnet_name=args.controlnet, out_prefix=args.prefix,
    )

    print(f"submit: {args.image}  seed={args.seed}  denoise={args.denoise}  "
          f"lora={args.lora_strength}  cn={args.cn_strength}", flush=True)
    start = time.time()
    prompt_id = post_prompt(workflow)
    print(f"prompt_id: {prompt_id}", flush=True)

    result = wait_for_completion(prompt_id)
    elapsed = time.time() - start

    # Find the saved output paths
    outputs = result.get("outputs", {}).get("12", {}).get("images", [])
    if not outputs:
        print("no output images found in history", file=sys.stderr)
        return 1
    comfy_output = os.path.expanduser("~/Documents/ComfyUI/output")
    for img in outputs:
        path = os.path.join(comfy_output, img.get("subfolder", ""), img["filename"])
        print(f"done in {elapsed:.1f}s -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
