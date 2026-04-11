"""Templated narration backend.

Returns deterministic, template-driven responses so teammates can develop
the renderer wiring without the GN100 or the 38 GB Nemotron model. Don't
judge narration quality from this backend - that's a Saturday-night job
on the real model. Use the stub to test wiring only.
"""

from __future__ import annotations

from src.data.schema import CulturalEvent, NarrationResponse

# Per-niche voice fragments. The stub uses these to make the templated
# narration feel slightly different per niche so the renderer can verify
# the niche switch is wired correctly end-to-end.
NICHE_VOICE: dict[str, str] = {
    "hip-hop": "in the breakbeat heart of the borough",
    "queer-history": "in the rooms where queerness made itself visible",
    "demolished-theaters": "where the lobby used to glow",
    "jazz": "in the long line from Minton's to here",
    "salsa": "where the conga still bleeds through the walls",
    "punk": "where the Bowery taught the country how to scream",
    "immigration": "where another wave learned the city",
}


def generate_narration(
    event: CulturalEvent,
    year: int,
    niche: str,
    nearby_titles: list[str],
) -> NarrationResponse:
    """Build a templated narration response from the event + niche + nearby context."""
    voice = NICHE_VOICE.get(niche, "in this place at this moment")
    nearby_phrase = (
        f" Around the corner: {', '.join(nearby_titles)}." if nearby_titles else ""
    )
    text = (
        f"{event.title}, {year}, {voice}. "
        f"{event.narration_seed}"
        f"{nearby_phrase}"
    )
    # Approximate the time the renderer should hold this on screen.
    duration_ms = max(2000, len(text) * 50)
    return NarrationResponse(
        text=text,
        era_visual_mode=event.era_visual_mode,
        duration_ms=duration_ms,
        backend="stub",
    )
