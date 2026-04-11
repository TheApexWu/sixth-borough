"""Real Nemotron-3 narration backend (GN100 only).

Posts a niche-conditioned prompt to a local llama.cpp server (default
http://127.0.0.1:8090) running a Nemotron-3 GGUF model, then maps the
response into the same NarrationResponse shape the stub backend returns.
The renderer cannot tell the difference between stub and real.

Configuration (env vars, all optional):
  LLAMA_SERVER_URL   default http://127.0.0.1:8090
  LLAMA_MODEL_NAME   default nemotron-3-nano-30b-a3b
  LLAMA_MAX_TOKENS   default 220
  LLAMA_TEMPERATURE  default 0.85
  LLAMA_TIMEOUT      default 120 (seconds)

This module uses only the standard library so it has no extra install
footprint beyond what main.py already requires (FastAPI + uvicorn).
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

from src.data.schema import CulturalEvent, NarrationResponse

LLAMA_SERVER_URL = os.environ.get("LLAMA_SERVER_URL", "http://127.0.0.1:8090").rstrip("/")
LLAMA_MODEL_NAME = os.environ.get("LLAMA_MODEL_NAME", "nemotron-3-nano-30b-a3b")
LLAMA_MAX_TOKENS = int(os.environ.get("LLAMA_MAX_TOKENS", "1024"))
LLAMA_TEMPERATURE = float(os.environ.get("LLAMA_TEMPERATURE", "0.85"))
LLAMA_TIMEOUT = float(os.environ.get("LLAMA_TIMEOUT", "120"))

_SYSTEM_PROMPT = (
    "You are the narrator of Sixth Borough, a time-machine map of New York City "
    "subcultures. You write in a tight, present-tense voice that puts the listener "
    "inside the moment. Two to three sentences max. No preamble, no headers, no "
    "lists, no markdown. Reference concrete sensory detail (sound, smell, light, "
    "cloth, brick) over abstract praise. Never break the fourth wall."
)


class NarrationBackendError(RuntimeError):
    """Raised when the local llama-server is unreachable or returns an error."""


def _build_user_prompt(
    event: CulturalEvent,
    year: int,
    niche: str,
    nearby_titles: list[str],
) -> str:
    nearby_block = ""
    if nearby_titles:
        joined = ", ".join(nearby_titles[:5])
        nearby_block = f"\nNearby on the map this year: {joined}."
    return (
        f"Year: {year}. Niche: {niche}. Place: {event.title}.\n"
        f"Hook (do not quote, use as ground truth): {event.narration_seed}"
        f"{nearby_block}\n\n"
        "Write the narration now."
    )


def _post_chat(payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{LLAMA_SERVER_URL}/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=LLAMA_TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        raise NarrationBackendError(
            f"llama-server HTTP {exc.code} from {LLAMA_SERVER_URL}: {detail[:400]}"
        ) from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise NarrationBackendError(
            f"llama-server at {LLAMA_SERVER_URL} unreachable: {exc}"
        ) from exc


def generate_narration(
    event: CulturalEvent,
    year: int,
    niche: str,
    nearby_titles: list[str],
) -> NarrationResponse:
    payload = {
        "model": LLAMA_MODEL_NAME,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(event, year, niche, nearby_titles)},
        ],
        "max_tokens": LLAMA_MAX_TOKENS,
        "temperature": LLAMA_TEMPERATURE,
        "stream": False,
    }
    started = time.monotonic()
    data = _post_chat(payload)

    try:
        msg = data["choices"][0]["message"]
        text = (msg.get("content") or "").strip()
        # Nemotron-3-Nano is a reasoning model: it may put all useful prose
        # into "reasoning_content" and leave "content" empty (especially when
        # max_tokens is tight).  Fall back to the reasoning trace so the
        # renderer still gets a narration.
        if not text:
            text = (msg.get("reasoning_content") or "").strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise NarrationBackendError(
            f"unexpected llama-server response shape: {str(data)[:400]}"
        ) from exc

    if not text:
        raise NarrationBackendError("llama-server returned an empty narration")

    # Renderer holds the narration on screen for ~80 ms per character,
    # clamped to a 6-30 second window so very short or very long outputs
    # still feel reasonable on the map.
    hold_ms = max(6000, min(30000, len(text) * 80))

    return NarrationResponse(
        text=text,
        era_visual_mode=event.era_visual_mode,
        duration_ms=hold_ms,
        backend="real",
    )
