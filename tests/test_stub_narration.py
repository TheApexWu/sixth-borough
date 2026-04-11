"""Smoke tests for the stub narration backend."""

from src.data.schema import CulturalEvent
from src.orchestrator.narration_stub import generate_narration


def make_event() -> CulturalEvent:
    return CulturalEvent(
        id="test-1",
        coordinate=(40.84, -73.92),
        start_year=1973,
        niche_tags=["hip-hop"],
        title="Test Event",
        narration_seed="Test narration seed about a place.",
        era_visual_mode="1970s-bronx-warm",
    )


def test_stub_returns_narration_response():
    r = generate_narration(make_event(), year=1973, niche="hip-hop", nearby_titles=[])
    assert r.backend == "stub"
    assert r.era_visual_mode == "1970s-bronx-warm"
    assert "Test Event" in r.text
    assert r.duration_ms > 0


def test_stub_includes_nearby_when_provided():
    r = generate_narration(
        make_event(),
        year=1973,
        niche="hip-hop",
        nearby_titles=["Other Event A", "Other Event B"],
    )
    assert "Other Event A" in r.text
    assert "Other Event B" in r.text


def test_stub_handles_unknown_niche_gracefully():
    r = generate_narration(
        make_event(), year=1973, niche="quantum-computing", nearby_titles=[]
    )
    assert r.backend == "stub"
    assert "Test Event" in r.text


def test_stub_duration_scales_with_text_length():
    short_event = make_event()
    long_event = make_event()
    long_event.narration_seed = "A much longer narration seed " * 20
    r_short = generate_narration(short_event, 1973, "hip-hop", [])
    r_long = generate_narration(long_event, 1973, "hip-hop", [])
    assert r_long.duration_ms > r_short.duration_ms
