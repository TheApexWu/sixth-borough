"""FastAPI router for the /biography endpoint.

Wired into src/orchestrator/main.py via:

    from src.biography.router import router as biography_router
    app.include_router(biography_router)

That's the entire integration. No other changes to main.py.

Drafted Apr 12 ~02:30 UTC, Session 45.
"""

from __future__ import annotations

from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.biography.lookup import assemble_record
from src.biography.synthesize import synthesize

router = APIRouter(tags=["biography"])


class BiographyRequest(BaseModel):
    """Accept any one of: bin, lat+lon, or event_id. Resolution priority is
    explicit BIN first, then event_id (which carries lat/lon), then lat/lon."""

    bin: str | None = Field(default=None, description="NYC Building Identification Number, e.g. '2008888'")
    lat: float | None = Field(default=None, description="Latitude in WGS84")
    lon: float | None = Field(default=None, description="Longitude in WGS84")
    event_id: str | None = Field(default=None, description="ID from data/events-seed.json, e.g. 'bronx-1973-08-11-sedgwick'")


class BiographyResponse(BaseModel):
    """The full biography envelope: structured record + Nemotron narrative."""

    query: dict[str, Any]
    structured_record: dict[str, Any]
    narrative: str
    citations: list[str]
    backend: str
    model: str | None = None
    tokens_in: int = 0
    tokens_out: int = 0


@router.post("/biography", response_model=BiographyResponse)
def post_biography(req: BiographyRequest) -> BiographyResponse:
    """Generate a footnoted building biography for the given address/BIN/event.

    Pipeline:
      1. Resolve query to a structured record by joining local NYC Open Data
         files (Building Footprints, NYPL Milstein photos, events-seed,
         demolished landmarks).
      2. Send the structured record to the local llama-server (Nemotron 30B).
      3. Return the markdown narrative plus the structured record plus the
         dataset citations.

    Failure modes:
      - 404 if no building OR event matched (caller probably typed wrong address)
      - 503 if llama-server unreachable (caller should fall back to cached biography)
    """
    if not (req.bin or req.event_id or (req.lat is not None and req.lon is not None)):
        raise HTTPException(
            status_code=400,
            detail="Must provide one of: bin, event_id, or (lat, lon).",
        )

    # Step 1: structured retrieval
    record = assemble_record(
        bin=req.bin,
        lat=req.lat,
        lon=req.lon,
        event_id=req.event_id,
    )

    # If we matched nothing useful, 404
    if not record.get("building") and not record.get("anchor_event"):
        raise HTTPException(
            status_code=404,
            detail="No building or event matched the query in the local data.",
        )

    # Step 2: prompt synthesis via llama-server
    try:
        synth = synthesize(record)
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=503,
            detail=f"llama-server unavailable for biography synthesis: {e}",
        )

    # Step 3: assemble the response envelope
    return BiographyResponse(
        query=record["query"],
        structured_record={
            k: v for k, v in record.items()
            if k not in {"query", "data_sources"}
        },
        narrative=synth["narrative"],
        citations=record.get("data_sources", []),
        backend=synth.get("backend", "real"),
        model=synth.get("model"),
        tokens_in=synth.get("tokens_in", 0),
        tokens_out=synth.get("tokens_out", 0),
    )
