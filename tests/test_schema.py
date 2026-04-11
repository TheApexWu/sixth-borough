"""Smoke tests for the cultural event Pydantic schema."""

from src.data.schema import CulturalEvent, NarrationRequest, NarrationResponse


def test_cultural_event_minimal():
    e = CulturalEvent(
        id="test-1",
        coordinate=(40.0, -73.0),
        start_year=1973,
        niche_tags=["hip-hop"],
        title="Test Event",
        narration_seed="Test seed.",
        era_visual_mode="1970s-bronx-warm",
    )
    assert e.id == "test-1"
    assert e.end_year is None
    assert e.importance_score == 50


def test_cultural_event_with_optional_fields():
    e = CulturalEvent(
        id="test-2",
        coordinate=(40.0, -73.0),
        start_year=1973,
        end_year=1985,
        niche_tags=["hip-hop", "demolished-theaters"],
        title="Test Event 2",
        narration_seed="Test seed 2.",
        era_visual_mode="1970s-bronx-warm",
        source_url="https://example.com/source",
        importance_score=90,
    )
    assert e.end_year == 1985
    assert e.importance_score == 90
    assert "demolished-theaters" in e.niche_tags


def test_narration_request_defaults():
    r = NarrationRequest(event_id="test-1", year=1973, niche="hip-hop")
    assert r.nearby_event_titles == []


def test_narration_response_round_trip():
    r = NarrationResponse(
        text="hello",
        era_visual_mode="1970s-bronx-warm",
        duration_ms=500,
        backend="stub",
    )
    payload = r.model_dump()
    assert payload["backend"] == "stub"
    assert payload["text"] == "hello"
