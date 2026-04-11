#!/usr/bin/env python3
"""Build a slim index of seeoldnyc.com posts via its WordPress REST API.

Each post on seeoldnyc.com is a historical NYC photo with a decade tag
(1860s → 2000s). The NYPL Milstein oldnyc.org dataset ends at 1956, so this
source fills the 1960s–2000s gap in the photo-mode slideshow.

Output:
  cultural-content/seeoldnyc/index.json          — slim index (committed)
  cultural-content/seeoldnyc/thumbs/{id}.jpg     — downloaded thumbnails (committed)

Run with --skip-download to regenerate just the JSON.

Attribution: seeoldnyc.com aggregates imagery from multiple archives; credit
the site on-screen and note individual sources where known.
"""
import argparse
import json
import re
import sys
import time
import urllib.request
import urllib.error
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THUMBS = ROOT / "cultural-content" / "seeoldnyc" / "thumbs"
OUT = ROOT / "cultural-content" / "seeoldnyc" / "index.json"

API = "https://seeoldnyc.com/wp-json/wp/v2/posts"
PER_PAGE = 100
UA = "sixth-borough/0.1 (+hackathon research; contact: james)"

DECADE_RE = re.compile(r"\b(18[6-9]0|19[0-9]0|20[0-2]0)s\b", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(18[6-9]\d|19\d{2}|20[0-2]\d)\b")


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def strip_html(s):
    s = re.sub(r"<[^>]+>", "", s or "")
    return unescape(s).strip()


def pick_year(title, decade_tags):
    # Prefer a specific year parsed from the title ("1977 Blackout"); fall back
    # to the midpoint of the first decade tag.
    m = YEAR_RE.search(title or "")
    if m:
        return int(m.group(1))
    for tag in decade_tags:
        dm = DECADE_RE.search(tag)
        if dm:
            return int(dm.group(1)) + 5  # decade midpoint
    return None


def extract_record(post):
    title = strip_html((post.get("title") or {}).get("rendered", ""))
    slug = post.get("slug", "")
    pid = post.get("id")
    embedded = post.get("_embedded") or {}
    media = (embedded.get("wp:featuredmedia") or [])
    image_url = None
    if media:
        image_url = media[0].get("source_url")
        if not image_url:
            sizes = ((media[0].get("media_details") or {}).get("sizes") or {})
            for key in ("large", "medium_large", "medium", "full"):
                if key in sizes and sizes[key].get("source_url"):
                    image_url = sizes[key]["source_url"]
                    break
    terms = embedded.get("wp:term") or []
    tag_names = []
    for group in terms:
        for t in group:
            name = t.get("name")
            if name:
                tag_names.append(name)
    year = pick_year(title, tag_names)
    if year is None or not image_url:
        return None
    return {
        "id": f"seeold-{pid}",
        "year": year,
        "title": title,
        "image_url": image_url,
        "slug": slug,
        "post_url": post.get("link") or f"https://seeoldnyc.com/{slug}/",
        "tags": tag_names,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-download", action="store_true")
    ap.add_argument("--max-posts", type=int, default=0,
                    help="stop after N posts (0 = all)")
    args = ap.parse_args()

    THUMBS.mkdir(parents=True, exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)

    print("fetching seeoldnyc posts…")
    all_posts = []
    page = 1
    while True:
        url = f"{API}?per_page={PER_PAGE}&page={page}&_embed=1"
        try:
            batch = fetch_json(url)
        except urllib.error.HTTPError as e:
            if e.code == 400:  # past last page
                break
            raise
        if not batch:
            break
        all_posts.extend(batch)
        print(f"  page {page}: {len(batch)} posts (running total {len(all_posts)})")
        if len(batch) < PER_PAGE:
            break
        page += 1
        if args.max_posts and len(all_posts) >= args.max_posts:
            break
        time.sleep(0.3)

    print(f"total posts fetched: {len(all_posts)}")

    records = []
    skipped = 0
    for p in all_posts:
        r = extract_record(p)
        if r is None:
            skipped += 1
            continue
        records.append(r)
    print(f"records with year+image: {len(records)} (skipped {skipped})")

    records.sort(key=lambda r: (r["year"], r["id"]))

    if not args.skip_download:
        new = skipped_dl = failed = 0
        for rec in records:
            path = THUMBS / f"{rec['id']}.jpg"
            if path.exists() and path.stat().st_size > 0:
                skipped_dl += 1
                rec["thumb"] = f"cultural-content/seeoldnyc/thumbs/{rec['id']}.jpg"
                continue
            try:
                req = urllib.request.Request(rec["image_url"], headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=30) as r:
                    data = r.read()
                path.write_bytes(data)
                rec["thumb"] = f"cultural-content/seeoldnyc/thumbs/{rec['id']}.jpg"
                new += 1
                if new % 25 == 0:
                    print(f"  downloaded {new} new thumbnails…")
                time.sleep(0.15)
            except Exception as e:
                print(f"  ! {rec['id']}: {e}")
                failed += 1
        print(f"thumbnails: {new} new, {skipped_dl} cached, {failed} failed")
    else:
        for rec in records:
            path = THUMBS / f"{rec['id']}.jpg"
            if path.exists():
                rec["thumb"] = f"cultural-content/seeoldnyc/thumbs/{rec['id']}.jpg"

    records = [r for r in records if r.get("thumb")]
    slim = [
        {
            "id": r["id"],
            "year": r["year"],
            "title": r["title"],
            "thumb": r["thumb"],
            "source": "seeoldnyc.com",
            "source_url": r["post_url"],
        }
        for r in records
    ]

    OUT.write_text(json.dumps(slim, indent=2))
    size_kb = OUT.stat().st_size // 1024
    print(f"wrote {OUT} ({size_kb} KB, {len(slim)} records)")
    if slim:
        print(f"year range: {slim[0]['year']}-{slim[-1]['year']}")
    print("done. Attribution: seeoldnyc.com")


if __name__ == "__main__":
    main()
