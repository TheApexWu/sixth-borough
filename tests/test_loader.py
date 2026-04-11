"""Smoke tests for the seed JSON loader + query helpers."""

from src.data.loader import find_event, load_events, query_events


def test_loads_seed_file():
    events = load_events()
    assert len(events) > 0, "seed file should have at least one event"


def test_all_events_have_narration_seeds():
    events = load_events()
    for e in events:
        assert e.narration_seed, f"event {e.id} missing narration_seed"
        assert len(e.narration_seed) >= 20, (
            f"event {e.id} has a suspiciously short narration_seed"
        )


def test_all_events_have_at_least_one_niche():
    events = load_events()
    for e in events:
        assert e.niche_tags, f"event {e.id} has no niche_tags"


def test_query_by_year_window():
    events = load_events()
    in_1973 = query_events(events, year=1973)
    for e in in_1973:
        assert e.start_year <= 1973
        assert e.end_year is None or e.end_year >= 1973


def test_query_by_niche():
    events = load_events()
    hh = query_events(events, niche="hip-hop")
    for e in hh:
        assert "hip-hop" in e.niche_tags
    assert len(hh) > 0, "expected at least one hip-hop event in seed"


def test_query_by_year_and_niche():
    events = load_events()
    hh_1973 = query_events(events, year=1973, niche="hip-hop")
    for e in hh_1973:
        assert "hip-hop" in e.niche_tags
        assert e.start_year <= 1973


def test_find_event_by_id():
    events = load_events()
    if events:
        first = events[0]
        assert find_event(events, first.id) is first
        assert find_event(events, "nonexistent-id-12345") is None
