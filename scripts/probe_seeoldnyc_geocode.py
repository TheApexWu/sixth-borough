#!/usr/bin/env python3
"""Probe script: fetch a sample of seeoldnyc posts and try geocoding each
title via Nominatim (constrained to the NYC bounding box). Reports the hit
rate and sample results so we can decide whether this approach is viable
before rebuilding the full index.
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nyc_gazetteer import GAZETTEER

UA = "sixth-borough-hackathon/0.1 (research prototype)"
API = "https://seeoldnyc.com/wp-json/wp/v2/posts"
NOMINATIM = "https://nominatim.openstreetmap.org/search"
NYC_VIEWBOX = "-74.27,40.92,-73.68,40.49"  # left,top,right,bottom

YEAR_RE = re.compile(r"\b(18\d{2}|19\d{2}|20\d{2})\b")
STOPWORDS = {
    "the", "a", "an", "of", "in", "on", "at", "and", "or", "to", "for",
    "through", "with", "from", "by", "before", "after", "during", "into",
    "nyc", "new", "york", "city",
}
DECADE_RE = re.compile(r"\b\d{4}s\b", re.IGNORECASE)


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def strip_html(s):
    s = re.sub(r"<[^>]+>", "", s or "")
    return unescape(s).strip()


def clean_title_for_geocode(title):
    # Nominatim does better with a short place phrase than a whole sentence.
    # Strip year numbers, decade tags, and obvious filler words.
    t = YEAR_RE.sub("", title)
    t = DECADE_RE.sub("", t)
    t = re.sub(r"[^\w\s,\-']", " ", t)
    t = re.sub(r"\s+", " ", t).strip(" ,-")
    return t


def extract_phrases(title):
    """Yield candidate location phrases, longest/first-priority first."""
    cleaned = clean_title_for_geocode(title)
    if not cleaned:
        return []
    # strategy: try the part before the first colon (usually a place name
    # in a "Brooklyn Bridge: A Story of …" construction), then the whole
    # cleaned string.
    candidates = []
    if ":" in cleaned:
        candidates.append(cleaned.split(":", 1)[0].strip())
    candidates.append(cleaned)
    # also try the first 4-word chunk — often contains the landmark.
    words = cleaned.split()
    if len(words) > 4:
        candidates.append(" ".join(words[:4]))
    # dedupe preserving order
    seen = set()
    out = []
    for c in candidates:
        if c and c.lower() not in seen:
            seen.add(c.lower())
            out.append(c)
    return out


def geocode(query):
    params = {
        "q": f"{query}, New York City",
        "format": "json",
        "limit": "1",
        "viewbox": NYC_VIEWBOX,
        "bounded": "1",
        "addressdetails": "1",
    }
    url = f"{NOMINATIM}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.load(r)
    except Exception as e:
        return None, str(e)
    if not data:
        return None, None
    hit = data[0]
    return (float(hit["lat"]), float(hit["lon"])), hit.get("display_name", "")


def gazetteer_match(text):
    low = text.lower()
    for keyword, lat, lon in GAZETTEER:
        if keyword.lower() in low:
            return keyword, (lat, lon)
    return None, None


def main():
    print("fetching sample posts from seeoldnyc…")
    # Pull 3 pages = 300 posts for a better sample of the whole archive.
    posts = []
    for page in range(1, 4):
        batch = fetch_json(f"{API}?per_page=100&page={page}&_embed=1")
        if not batch:
            break
        posts.extend(batch)
    print(f"  got {len(posts)} posts\n")

    gaz_hits = nom_hits = misses = 0
    miss_titles = []
    by_keyword = {}
    for i, p in enumerate(posts, 1):
        title = strip_html((p.get("title") or {}).get("rendered", ""))
        # Also pull excerpt for richer search.
        excerpt = strip_html((p.get("excerpt") or {}).get("rendered", ""))
        search_text = f"{title}  {excerpt}"
        kw, coord = gazetteer_match(search_text)
        if coord:
            gaz_hits += 1
            by_keyword[kw] = by_keyword.get(kw, 0) + 1
            continue
        # Fall back to Nominatim for unmatched titles.
        phrases = extract_phrases(title)
        nom_coord = None
        for phrase in phrases:
            nom_coord, display = geocode(phrase)
            time.sleep(1.1)
            if nom_coord:
                break
        if nom_coord:
            nom_hits += 1
        else:
            misses += 1
            miss_titles.append(title)

    total = gaz_hits + nom_hits + misses
    print(f"\ngazetteer hits: {gaz_hits}/{total} ({gaz_hits/total*100:.0f}%)")
    print(f"nominatim hits: {nom_hits}/{total} ({nom_hits/total*100:.0f}%)")
    print(f"total hits    : {gaz_hits+nom_hits}/{total} ({(gaz_hits+nom_hits)/total*100:.0f}%)")
    print(f"misses        : {misses}")
    print("\ntop gazetteer keywords hit:")
    for k, n in sorted(by_keyword.items(), key=lambda x: -x[1])[:15]:
        print(f"  {n:3d} × {k}")
    print("\nsample misses (first 20):")
    for t in miss_titles[:20]:
        print(f"  - {t[:90]}")


if __name__ == "__main__":
    main()
