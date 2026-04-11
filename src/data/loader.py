"""Loads and validates the cultural events seed JSON.

The seed JSON lives at `data/events-seed.json` with the structure:
{
  "_meta": {...},
  "niches": {...},
  "events": [ <CulturalEvent>, ... ],
  "_notes": "..."
}

Only the "events" array is parsed into CulturalEvent objects. The other
keys are advisory and read by hand by the curators.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .schema import CulturalEvent

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SEED_PATH = REPO_ROOT / "data" / "events-seed.json"


def load_events(path: Optional[Path] = None) -> list[CulturalEvent]:
    """Load and validate every event from the seed JSON. Raises on schema errors."""
    p = Path(path) if path else DEFAULT_SEED_PATH
    raw = json.loads(p.read_text())
    events_raw = raw.get("events", [])
    return [CulturalEvent(**item) for item in events_raw]


def query_events(
    events: list[CulturalEvent],
    year: Optional[int] = None,
    niche: Optional[str] = None,
) -> list[CulturalEvent]:
    """Filter events by year window and/or niche tag."""
    out = events
    if year is not None:
        out = [
            e
            for e in out
            if e.start_year <= year and (e.end_year is None or e.end_year >= year)
        ]
    if niche is not None:
        out = [e for e in out if niche in e.niche_tags]
    return out


def find_event(events: list[CulturalEvent], event_id: str) -> Optional[CulturalEvent]:
    """Look up an event by its stable id. Returns None if not found."""
    return next((e for e in events if e.id == event_id), None)
