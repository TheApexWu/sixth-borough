"""FastAPI orchestrator app.

Switches between the stub and real narration backends via the
NARRATION_MODE environment variable. Loads the cultural events seed JSON
once at startup and serves four endpoints:

  GET  /health      sanity check + which backend is wired
  GET  /events      filtered list of cultural events (year, niche)
  GET  /niches      niche taxonomy with display metadata
  POST /narrate     generate a narration response for one event

The renderer (Carson's Bevy app or James's WebGL fallback) is the only
client. Both renderers hit the same URLs. The stub and real backends
return the same NarrationResponse shape, so the renderer code never has
to know which backend is wired.

Run locally with:
  pip install -r requirements.txt
  NARRATION_MODE=stub ./scripts/dev-stub.sh
"""

from __future__ import annotations

import os
from typing import Optional

from fastapi import FastAPI, HTTPException

from src.data.loader import find_event, load_events, query_events
from src.data.niches import NICHE_DISPLAY
from src.data.schema import NarrationRequest, NarrationResponse

NARRATION_MODE = os.environ.get("NARRATION_MODE", "stub").lower()

if NARRATION_MODE == "real":
    from src.orchestrator.narration_real import generate_narration, NarrationBackendError  # GN100 only
else:
    from src.orchestrator.narration_stub import generate_narration

    class NarrationBackendError(RuntimeError):  # noqa: E303 – stub never raises this
        pass

app = FastAPI(
    title="Sixth Borough Orchestrator",
    version="0.1.0",
    description="Time machine for niche subcultures across all five boroughs of NYC.",
)

# Load events once at startup. They are immutable for the lifetime of the
# server - if the seed JSON changes, restart the server (dev-stub.sh has
# --reload enabled by default).
EVENTS = load_events()


@app.get("/health")
def health() -> dict:
    """Sanity check. Useful for confirming the renderer can reach the orchestrator."""
    return {
        "status": "ok",
        "narration_mode": NARRATION_MODE,
        "event_count": len(EVENTS),
        "niches": list(NICHE_DISPLAY.keys()),
    }


@app.get("/events")
def get_events(year: Optional[int] = None, niche: Optional[str] = None) -> list[dict]:
    """Filtered list of cultural events.

    Examples:
      GET /events                  -> all events
      GET /events?year=1973        -> events active in 1973
      GET /events?niche=hip-hop    -> all hip-hop events
      GET /events?year=1973&niche=hip-hop  -> both filters
    """
    return [e.model_dump() for e in query_events(EVENTS, year=year, niche=niche)]


@app.get("/niches")
def get_niches() -> dict:
    """Niche taxonomy with display metadata for the renderer's filter UI."""
    return NICHE_DISPLAY


@app.post("/narrate", response_model=NarrationResponse)
def narrate(req: NarrationRequest) -> NarrationResponse:
    """Generate a 2-3 sentence narration for a single event.

    The renderer calls this when the user clicks a pin. The orchestrator
    looks up the event, builds the niche-conditioned prompt, and routes
    to either the stub or the real Nemotron backend depending on
    NARRATION_MODE.
    """
    event = find_event(EVENTS, req.event_id)
    if event is None:
        raise HTTPException(
            status_code=404,
            detail=f"event_id '{req.event_id}' not found in seed",
        )
    try:
        return generate_narration(
            event=event,
            year=req.year,
            niche=req.niche,
            nearby_titles=req.nearby_event_titles,
        )
    except NarrationBackendError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
