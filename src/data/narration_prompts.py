"""Niche-conditioned narration prompt template.

Used by both the stub and the real Nemotron backends. Lock this template
Friday night and do not iterate on it during the build - prompt drift is
the most common way to lose the consistent narration voice.
"""

from __future__ import annotations

from .schema import CulturalEvent

NARRATION_SYSTEM_PROMPT = (
    "You are a cultural memory narrator. Your voice is grounded, specific, "
    "and present-tense. You speak with the authority of someone who knows "
    "the {niche} scene from the inside, not as a tourist or a textbook. "
    "Two to three sentences per scene. No throat-clearing."
)

NARRATION_USER_PROMPT = """CONTEXT:
- Place: {neighborhood}, {borough}
- Year: {year}
- Era visual mode: {era_visual_mode}
- Active niche lens: {niche}
- Event: {title}
- Hook: {narration_seed}
- Recently active nearby events: {nearby}

Narrate this scene in 2-3 sentences for someone standing here right now,
filtered through the {niche} lens."""


def build_prompt(
    event: CulturalEvent,
    year: int,
    niche: str,
    nearby_titles: list[str],
    neighborhood: str = "Bronx",
    borough: str = "Bronx",
) -> tuple[str, str]:
    """Returns (system, user) prompt strings ready for the LLM."""
    system = NARRATION_SYSTEM_PROMPT.format(niche=niche)
    nearby = ", ".join(nearby_titles) if nearby_titles else "(none)"
    user = NARRATION_USER_PROMPT.format(
        neighborhood=neighborhood,
        borough=borough,
        year=year,
        era_visual_mode=event.era_visual_mode,
        niche=niche,
        title=event.title,
        narration_seed=event.narration_seed,
        nearby=nearby,
    )
    return system, user
