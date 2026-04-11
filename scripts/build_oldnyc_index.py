#!/usr/bin/env python3
"""Build a slim NYC subset of the oldnyc.org (NYPL Milstein Collection) dataset.

Input:  cultural-content/oldnyc/raw/data.json       (75 MB, gitignored)
Output: cultural-content/oldnyc/index.json          (slim index, committed)
        cultural-content/oldnyc/thumbs/{id}.jpg     (downloaded thumbnails, committed)

Filters geocoded photos to the 5 NYC boroughs with parseable years, evenly
samples across each borough, and downloads their 600px NYPL thumbnails.

Attribution: photos are from NYPL's Milstein Division (public domain)
via https://www.oldnyc.org — credit in the demo video + docs/DATA_SOURCES.md.
"""
import argparse
import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "cultural-content" / "oldnyc" / "raw" / "data.json"
THUMBS = ROOT / "cultural-content" / "oldnyc" / "thumbs"
OUT = ROOT / "cultural-content" / "oldnyc" / "index.json"

BOROS = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]


def parse_year(rec):
    years = [y for y in (rec.get("years") or []) if y]
    if years:
        try:
            return int(years[0])
        except ValueError:
            pass
    date = rec.get("date") or ""
    if len(date) >= 4 and date[:4].isdigit():
        return int(date[:4])
    return None


def even_sample(records, cap):
    if cap <= 0 or len(records) <= cap:
        return records
    step = len(records) / cap
    return [records[int(i * step)] for i in range(cap)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year-min", type=int, default=1900)
    ap.add_argument("--year-max", type=int, default=1990)
    ap.add_argument("--boroughs", default="all",
                    help="comma-separated list, or 'all'. Options: " + ", ".join(BOROS))
    ap.add_argument("--max-per-boro", type=int, default=150,
                    help="cap per borough via even-chronological sampling (0 = no cap). "
                         "Default 150 → ~750 thumbnails total, ~30–60 MB on disk.")
    ap.add_argument("--skip-download", action="store_true",
                    help="only regenerate the JSON index; don't fetch thumbnails")
    args = ap.parse_args()

    if not RAW.exists():
        sys.exit(f"missing {RAW} — download https://www.oldnyc.org/data.json into that path first")

    target_boros = BOROS if args.boroughs == "all" else [b.strip() for b in args.boroughs.split(",")]
    for b in target_boros:
        if b not in BOROS:
            sys.exit(f"unknown borough: {b!r}. valid: {BOROS}")

    THUMBS.mkdir(parents=True, exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)

    print(f"reading {RAW}")
    raw = json.load(open(RAW))
    photos = raw["photos"]
    print(f"  total photos in dataset: {len(photos)}")

    # Bucket by borough
    by_boro = {b: [] for b in target_boros}
    for p in photos:
        boro = (p.get("geocode") or {}).get("location", {}).get("boro")
        if boro not in by_boro:
            continue
        year = parse_year(p)
        if year is None:
            continue
        if not (args.year_min <= year <= args.year_max):
            continue
        loc = p.get("location") or {}
        if loc.get("lat") is None or loc.get("lon") is None:
            continue
        by_boro[boro].append({
            "id": p["photo_id"],
            "boro": boro,
            "lat": loc["lat"],
            "lon": loc["lon"],
            "year": year,
            "title": (p.get("title") or "").strip(),
            "image_url": p["image_url"],
            "nypl_url": p.get("nypl_url") or "",
        })

    selected = []
    print(f"  filter: {args.year_min}-{args.year_max}, --max-per-boro {args.max_per_boro}")
    for b in target_boros:
        recs = sorted(by_boro[b], key=lambda r: r["year"])
        capped = even_sample(recs, args.max_per_boro)
        print(f"    {b:14s}: {len(recs):4d} candidates → {len(capped):4d} selected")
        selected.extend(capped)

    selected.sort(key=lambda r: (r["boro"], r["year"]))
    print(f"  total selected: {len(selected)}")

    if not args.skip_download:
        new = skipped = failed = 0
        for rec in selected:
            thumb_path = THUMBS / f"{rec['id']}.jpg"
            if thumb_path.exists() and thumb_path.stat().st_size > 0:
                skipped += 1
                continue
            try:
                req = urllib.request.Request(
                    rec["image_url"],
                    headers={"User-Agent": "sixth-borough-build/0.1 (hackathon, NYPL Milstein via oldnyc.org)"},
                )
                with urllib.request.urlopen(req, timeout=30) as r:
                    thumb_path.write_bytes(r.read())
                new += 1
                if new % 25 == 0:
                    print(f"    downloaded {new} thumbnails...")
                time.sleep(0.1)  # gentle on NYPL's CDN
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
                failed += 1
                print(f"    failed {rec['id']}: {e}")
        print(f"  thumbnails: {new} new, {skipped} already present, {failed} failed")

    # Emit slim index — only include records whose thumbnail actually exists locally
    slim = []
    for r in selected:
        thumb_path = THUMBS / f"{r['id']}.jpg"
        if not args.skip_download and not thumb_path.exists():
            continue
        slim.append({
            "id": r["id"],
            "boro": r["boro"],
            "lat": r["lat"],
            "lon": r["lon"],
            "year": r["year"],
            "title": r["title"],
            "thumb": f"cultural-content/oldnyc/thumbs/{r['id']}.jpg",
            "nypl_url": r["nypl_url"],
        })

    OUT.write_text(json.dumps(slim, indent=2))
    size_kb = OUT.stat().st_size // 1024
    print(f"  wrote {OUT} ({size_kb} KB, {len(slim)} records)")

    # Per-borough summary
    counts = {}
    for r in slim:
        counts[r["boro"]] = counts.get(r["boro"], 0) + 1
    for b in target_boros:
        print(f"    {b:14s}: {counts.get(b, 0)} records with local thumbnails")

    print("done. Attribution: NYPL Milstein Division via oldnyc.org")


if __name__ == "__main__":
    main()
