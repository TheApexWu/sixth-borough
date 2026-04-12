"""Prompt synthesis layer.

Takes the structured record from lookup.py, formats it into a tight prompt,
calls the local llama-server (Nemotron-3-Nano-30B already loaded), returns
the markdown narrative.

Drafted Apr 12 ~02:30 UTC, Session 45.
"""

from __future__ import annotations

import json
import os
from typing import Any

import httpx

LLAMA_SERVER_URL = os.environ.get("LLAMA_SERVER_URL", "http://127.0.0.1:8090")
LLAMA_TIMEOUT_S = float(os.environ.get("BIOGRAPHY_LLAMA_TIMEOUT_S", "120"))
LLAMA_MAX_TOKENS = int(os.environ.get("BIOGRAPHY_MAX_TOKENS", "1024"))


SYSTEM_PROMPT = """You are a forensic building historian for the Sixth Borough project, a local NYC cultural memory engine. You write structured biographies of New York City buildings using ONLY the public-record data provided in the user message. You never speculate, never predict, never invent owners or events that are not in the record. If a field is null or empty, you say "no record." Every claim is grounded in the structured data shown to you.

Your output is a 4-section markdown document. The sections are exactly:

## 1. Identification
A factual paragraph naming the BIN, year built, height in meters, borough, and approximate location. Cite the dataset (NYC Open Data Building Footprints, 5zhs-2jue) for each fact.

## 2. Physical history
A factual paragraph describing what the structured record proves about the building's physical existence: when it was built, how tall it is, what era of New York architecture it belongs to, what's documented near it. If alteration data is present, mention it. If demolition data is present, treat the building as historical, not extant.

## 3. Cultural significance
A paragraph weaving together the nearby NYPL Milstein photographs (cite years and titles), nearby cultural events (cite dates and event titles), and any anchor event tied to this building. The voice here can be elegiac and specific. Name people, dates, and places. Do not invent. If the anchor event is the August 11 1973 Kool Herc party at 1520 Sedgwick, name it directly and tie it to the displacement context that brought families onto that block.

## 4. What the receipts prove
A short closing paragraph that ties the chain together. The Sixth Borough thesis: we don't predict gentrification, we trace it from the receipts. Name what the public record makes verifiable about this address. Close with the building's place in the larger cultural memory of NYC.

Rules:
- Every numerical claim cites a dataset name in parentheses
- No em dashes
- No hedging language ("perhaps", "might be", "possibly")
- No invented owners, prices, or events
- If data is missing, say so plainly: "No demolition record." "No alterations on file."
- Maximum 4 sections, ~600 words total
- No headers other than the 4 numbered sections above
"""


def build_prompt(record: dict[str, Any]) -> str:
    """Format the structured record from lookup.py into a tight user message.

    The model sees only what's actually in the record. We do not embellish.
    JSON serialization keeps the field names verbatim so the model can cite
    them. Field names are part of the contract."""

    building = record.get("building")
    anchor = record.get("anchor_event")
    photos = record.get("nearby_photos", [])
    landmarks = record.get("nearby_landmarks", [])
    events = record.get("nearby_events", [])
    sources = record.get("data_sources", [])

    lines = []
    lines.append("STRUCTURED RECORD FOR BUILDING BIOGRAPHY:")
    lines.append("")

    # Building block
    if building:
        lines.append("=== BUILDING (NYC Open Data Building Footprints, 5zhs-2jue) ===")
        lines.append(f"BIN: {building.get('bin', 'unknown')}")
        lines.append(f"Borough: {building.get('borough', 'unknown')}")
        h = building.get("height_m")
        lines.append(f"Roof height (LiDAR-measured): {h} meters" if h else "Roof height: no record")
        y = building.get("year_built")
        lines.append(f"Construction year: {y}" if y else "Construction year: no record")
        lat = building.get("centroid_lat")
        lon = building.get("centroid_lon")
        lines.append(f"Polygon centroid: lat={lat:.5f}, lon={lon:.5f}")
        d = building.get("distance_m")
        if d is not None:
            lines.append(f"Distance from query point: {d} meters")
    else:
        lines.append("=== BUILDING ===")
        lines.append("No building record matched. Proceed with anchor event and surrounding context only.")
    lines.append("")

    # Anchor event
    if anchor:
        lines.append("=== ANCHOR EVENT (data/events-seed.json) ===")
        lines.append(f"Event ID: {anchor.get('id')}")
        for key in ("title", "year", "date", "neighborhood", "description", "niche", "address"):
            v = anchor.get(key)
            if v:
                lines.append(f"{key}: {v}")
        lines.append("")

    # Nearby photos (NYPL Milstein)
    if photos:
        lines.append(f"=== NEARBY PHOTOGRAPHS (NYPL Milstein collection, {len(photos)} within 200m) ===")
        for p in photos:
            title = p.get("title", "untitled")
            year = p.get("year", "?")
            dist = p.get("distance_m", "?")
            url = p.get("nypl_url", "")
            lines.append(f'- "{title}" ({year}) — {dist} m away — {url}')
        lines.append("")

    # Nearby cultural events
    if events:
        lines.append(f"=== NEARBY CULTURAL EVENTS (data/events-seed.json, {len(events)} within 500m) ===")
        for e in events:
            lines.append(f"- {e.get('id', '?')}: {e.get('title', '?')} ({e.get('year', '?')}) — {e.get('distance_m', '?')} m away")
        lines.append("")

    # Demolished landmarks (Wikidata)
    if landmarks:
        lines.append(f"=== DEMOLISHED LANDMARKS NEARBY (Wikidata, {len(landmarks)} within 1km) ===")
        for l in landmarks:
            name = l.get("name", "unknown")
            built = l.get("built", "?")
            demo = l.get("demolished", "?")
            dist = l.get("distance_m", "?")
            lines.append(f"- {name}: built {built}, demolished {demo}, {dist} m away")
        lines.append("")

    # Data source provenance
    if sources:
        lines.append("=== DATA SOURCES USED IN THIS RECORD ===")
        for s in sources:
            lines.append(f"- {s}")
        lines.append("")

    lines.append("Now write the 4-section markdown biography per the system prompt.")

    return "\n".join(lines)


def synthesize(record: dict[str, Any]) -> dict[str, Any]:
    """Send the structured record to the local llama-server and return the
    narrative + metadata.

    Returns:
      {
        "narrative": "<markdown>",
        "model": "Nemotron-3-Nano-30B-A3B",
        "backend": "real",
        "tokens_in": int,
        "tokens_out": int,
        "duration_ms": int,
      }

    Raises httpx.HTTPError on llama-server failure. Caller is responsible for
    catching + degrading gracefully (e.g., serving a stub biography from cache).
    """

    user_prompt = build_prompt(record)

    payload = {
        "model": "nemotron-3-nano-30b-a3b",  # llama-server ignores this but it's the right name
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": LLAMA_MAX_TOKENS,
        "temperature": 0.4,  # low temp — this is forensic, not creative
        "stream": False,
    }

    url = f"{LLAMA_SERVER_URL}/v1/chat/completions"
    with httpx.Client(timeout=LLAMA_TIMEOUT_S) as client:
        resp = client.post(url, json=payload)
        resp.raise_for_status()
        body = resp.json()

    choice = body["choices"][0]["message"]
    # Nemotron's reasoning models sometimes split content into reasoning_content
    # + content. Use whichever is non-empty (matches narration_real.py fallback).
    narrative = choice.get("content") or choice.get("reasoning_content") or ""

    usage = body.get("usage", {})
    return {
        "narrative": narrative.strip(),
        "model": body.get("model", "unknown"),
        "backend": "real",
        "tokens_in": usage.get("prompt_tokens", 0),
        "tokens_out": usage.get("completion_tokens", 0),
        "duration_ms": int(body.get("timings", {}).get("predicted_ms", 0)) if body.get("timings") else 0,
    }
