"""Smoke test for the committed data files. Needs no GPU and no model.

The default run only stats files and reads the small JSON files. Set
SIXTH_BOROUGH_FULL_DATA=1 to also parse the five borough files (231 MB of
JSON) and count buildings.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA = REPO_ROOT / "data"

# (bytes, building records) for each file as committed in 9102a56, 12 Apr 2026.
BOROUGHS = {
    "manhattan": (12_798_818, 45_194),
    "bronx": (25_315_405, 104_277),
    "brooklyn": (67_939_793, 330_097),
    "queens": (93_983_373, 460_952),
    "staten": (30_758_833, 142_311),
}
TOTAL_BUILDINGS = 1_082_831

FULL_DATA = os.environ.get("SIXTH_BOROUGH_FULL_DATA") == "1"


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("borough", BOROUGHS)
def test_borough_file_has_committed_size(borough):
    # A wrong size means a partial download, an LFS pointer or a re-export
    # that the counts below no longer describe.
    expected_bytes, _ = BOROUGHS[borough]
    assert (DATA / f"{borough}_compact.json").stat().st_size == expected_bytes


def test_landmark_infrastructure():
    infra = _read(DATA / "landmarks-infrastructure.json")
    assert len(infra["bridges"]) == 8
    assert len(infra["stadiums"]) == 8
    assert sum(s["type"] == "stadium_ghost" for s in infra["stadiums"]) == 3
    assert {g["b"] for g in infra["ghost_buildings"]} == {
        "WTC1", "WTC2", "WTC3", "WTC7", "PENN_ORIG", "SINGER",
    }


def test_demolished_landmarks():
    assert len(_read(DATA / "demolished-landmarks.json")) == 286


def test_every_oldnyc_photo_has_a_thumbnail():
    index = _read(REPO_ROOT / "cultural-content" / "oldnyc" / "index.json")
    assert len(index) == 750
    missing = [p["thumb"] for p in index if not (REPO_ROOT / p["thumb"]).is_file()]
    assert not missing


def test_narration_cache_covers_every_seed_event():
    # The demo falls back to this cache when the model is unreachable.
    seed = {e["id"] for e in _read(DATA / "events-seed.json")["events"]}
    cache = _read(DATA / "narration_cache.json")["narrations"]
    assert len(seed) == 19
    assert set(cache) == seed


@pytest.mark.skipif(not FULL_DATA, reason="set SIXTH_BOROUGH_FULL_DATA=1 to parse all five borough files")
def test_building_counts():
    total = 0
    for borough, (_, expected) in BOROUGHS.items():
        records = _read(DATA / f"{borough}_compact.json")
        assert len(records) == expected, borough
        assert all("p" in r and "h" in r for r in records), borough
        total += len(records)
        del records
    assert total == TOTAL_BUILDINGS
