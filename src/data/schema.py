"""Pydantic schemas for cultural events, narration requests, and narration responses.

The CulturalEvent schema is the contract between the seed JSON file
(data/events-seed.json), the loader, the orchestrator, the renderer, and
both narration backends. If you need to change it, ping the team in chat
first because every other component reads from these field names.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CulturalEvent(BaseModel):
    """A single cultural event with a coordinate, year window, and niche tags."""

    model_config = ConfigDict(extra="allow")

    id: str
    coordinate: tuple[float, float] = Field(
        ...,
        description="(lat, lng) in WGS84. Approximate is fine for the demo.",
    )
    start_year: int
    end_year: Optional[int] = Field(
        default=None,
        description="When the event/place stops being 'active' on the slider. None means ongoing or instantaneous.",
    )
    niche_tags: list[str]
    title: str
    narration_seed: str = Field(
        ...,
        description="Hand-written hook fed into the LLM at runtime. Do not generate these.",
    )
    era_visual_mode: str = Field(
        ...,
        description="Maps to a renderer post-process parameter set (palette + Sobel intensity + vignette warmth).",
    )
    source_url: Optional[str] = None
    importance_score: int = Field(
        default=50,
        ge=0,
        le=100,
        description="Used to prioritize pins when many events overlap on the map at the same time.",
    )


class NarrationRequest(BaseModel):
    """Request body for POST /narrate."""

    event_id: str
    year: int
    niche: str
    nearby_event_titles: list[str] = Field(default_factory=list)


class NarrationResponse(BaseModel):
    """Response body from POST /narrate. Same shape from stub and real backends."""

    text: str
    era_visual_mode: str
    duration_ms: int = Field(
        ...,
        description="Approximate time the renderer should hold the narration on screen.",
    )
    backend: str = Field(
        ...,
        description="Either 'stub' or 'real'. Useful for sanity-checking which backend is wired.",
    )
