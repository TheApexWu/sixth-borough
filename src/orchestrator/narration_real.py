"""Real Nemotron-3-Nano narration backend (GN100 only).

Filled in on the `orchestrator-narration` branch by Alex. The real backend
calls llama.cpp's OpenAI-compatible API on `localhost:30000` (the same
port the stub uses, deliberately, so the renderer code never has to know
which backend is wired).

Until that branch lands and merges, calling generate_narration() in
NARRATION_MODE=real will raise NotImplementedError with a helpful pointer
to the runbook.
"""

from __future__ import annotations

from src.data.schema import CulturalEvent, NarrationResponse


def generate_narration(
    event: CulturalEvent,
    year: int,
    niche: str,
    nearby_titles: list[str],
) -> NarrationResponse:
    raise NotImplementedError(
        "narration_real not yet implemented. "
        "Run with NARRATION_MODE=stub for development on any laptop, or "
        "see docs/GN100_RUNBOOK.md (coming on the orchestrator-narration "
        "branch) for the real Nemotron setup on the GN100."
    )
