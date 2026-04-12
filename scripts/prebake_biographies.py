"""Pre-bake biographies for all events in events-seed.json into the cache.

Mirrors the existing prebake_narrations.py pattern but for the /biography
endpoint. Runs each event_id through the orchestrator once, writing the
response to data/biography_cache.json via the cache layer in router.py.
First-call latency is ~1m30s per event on the warm GB10. Cached calls
return in ~10ms. Run this script ONCE before the demo and every event
button click during the demo serves from cache.

USAGE:
    # On the GN100 box where the orchestrator runs:
    python3 scripts/prebake_biographies.py

    # Or pre-bake a specific subset:
    python3 scripts/prebake_biographies.py bronx-1973-08-11-sedgwick bronx-1959-cross-bronx-expressway-displacement
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import urllib.request
import urllib.error

ORCH_URL = "http://127.0.0.1:30001/biography"
EVENTS_FILE = Path(__file__).resolve().parent.parent / "data" / "events-seed.json"
TIMEOUT_S = 300  # 5 min per call worst case (cold model + reasoning + 4 sections)


def load_event_ids() -> list[str]:
    if not EVENTS_FILE.exists():
        print(f"FATAL: {EVENTS_FILE} not found", file=sys.stderr)
        sys.exit(1)
    with open(EVENTS_FILE) as f:
        data = json.load(f)
    events = data.get("events", data) if isinstance(data, dict) else data
    return [e["id"] for e in events if e.get("id")]


def prebake_one(event_id: str) -> tuple[bool, float, int]:
    payload = json.dumps({"event_id": event_id}).encode("utf-8")
    req = urllib.request.Request(
        ORCH_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            body = resp.read()
            elapsed = time.monotonic() - started
            data = json.loads(body)
            backend = data.get("backend", "?")
            tokens_out = data.get("tokens_out", 0)
            narrative_chars = len(data.get("narrative", ""))
            return True, elapsed, narrative_chars
    except urllib.error.HTTPError as e:
        elapsed = time.monotonic() - started
        print(f"  HTTP {e.code} after {elapsed:.1f}s: {e.read().decode('utf-8', errors='replace')[:200]}")
        return False, elapsed, 0
    except (urllib.error.URLError, TimeoutError) as e:
        elapsed = time.monotonic() - started
        print(f"  network error after {elapsed:.1f}s: {e}")
        return False, elapsed, 0


def main():
    if len(sys.argv) > 1:
        event_ids = sys.argv[1:]
    else:
        event_ids = load_event_ids()

    print(f"prebaking {len(event_ids)} biographies via {ORCH_URL}")
    print(f"timeout per call: {TIMEOUT_S}s")
    print()

    total_start = time.monotonic()
    ok = 0
    fail = 0
    for i, eid in enumerate(event_ids, 1):
        print(f"[{i}/{len(event_ids)}] {eid}", flush=True)
        success, elapsed, chars = prebake_one(eid)
        if success:
            ok += 1
            tag = "CACHE HIT" if elapsed < 1.0 else "MODEL"
            print(f"    {tag} {elapsed:.2f}s {chars} chars", flush=True)
        else:
            fail += 1

    total_elapsed = time.monotonic() - total_start
    print()
    print(f"=== done in {total_elapsed:.0f}s ({total_elapsed/60:.1f} min) ===")
    print(f"  ok:   {ok}/{len(event_ids)}")
    print(f"  fail: {fail}/{len(event_ids)}")


if __name__ == "__main__":
    main()
