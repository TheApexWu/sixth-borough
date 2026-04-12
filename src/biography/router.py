"""FastAPI router for the /biography endpoint.

Wired into src/orchestrator/main.py via:

    from src.biography.router import router as biography_router
    app.include_router(biography_router)

That's the entire integration. No other changes to main.py.

Drafted Apr 12 ~02:30 UTC, Session 45.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.biography.lookup import assemble_record
from src.biography.synthesize import synthesize

# Pre-baked biography cache. Mirrors data/narration_cache.json for the
# /narrate endpoint. Same idea: a 30B model takes 1-2 min to produce a
# 4-section forensic biography — fine for offline processing, painful
# for a live demo click. We pre-bake hot keys (1520 Sedgwick + a handful
# of canonical Cross-Bronx events) into this file at code freeze, then
# the endpoint serves cache hits in <50 ms with backend tagged "cache".
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_CACHE_PATH = _REPO_ROOT / "data" / "biography_cache.json"


def _cache_key(req: BiographyRequest) -> str:  # noqa: F821 — forward ref
    """Deterministic cache key. Order of precedence matches lookup.py."""
    if req.bin:
        return f"bin:{req.bin.strip()}"
    if req.event_id:
        return f"event:{req.event_id.strip()}"
    if req.lat is not None and req.lon is not None:
        return f"latlon:{round(req.lat, 5)},{round(req.lon, 5)}"
    return ""


def _load_cache() -> dict[str, Any]:
    if not _CACHE_PATH.exists():
        return {}
    try:
        with open(_CACHE_PATH) as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cache(cache: dict[str, Any]) -> None:
    _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)

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

    # Step 0: cache hit. Pre-baked biographies for canonical demo addresses
    # (1520 Sedgwick, Cross-Bronx anchor events) live in data/biography_cache.json
    # and return in <50 ms. Cache is keyed deterministically by request shape.
    key = _cache_key(req)
    cache = _load_cache()
    if key and key in cache:
        cached = dict(cache[key])
        cached["backend"] = "cache"
        return BiographyResponse(**cached)

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
    response = BiographyResponse(
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

    # Step 4: write back to cache so the next click on the same key is instant.
    if key:
        cache[key] = response.model_dump()
        try:
            _save_cache(cache)
        except OSError:
            pass  # cache write failure should not break the response

    return response
