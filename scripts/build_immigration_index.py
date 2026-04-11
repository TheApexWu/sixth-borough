#!/usr/bin/env python3
"""Build an NYC immigration dataset: structured records + first-person stories.

Sources
  1. Wikidata SPARQL — people born outside the US who lived or died in NYC
     (filtered to those with a linked English Wikipedia article)
  2. Wikipedia action API — plain-text extract per person, regex-mined for
     arrival year, ship name, port of arrival, and mode of transport
  3. Library of Congress "Federal Writers' Project" collection — oral-history
     stubs from the 1936-40 Life Histories field interviews, filtered to NY
  4. Wikipedia category "Immigrants to the United States through Ellis Island"
     — curated list of notable Ellis Island arrivals, enriched with the same
     Wikipedia extract pipeline (default port = Ellis Island, mode = steamship)

Output
  cultural-content/immigration/index.json

Run
  python scripts/build_immigration_index.py                 # full build (~5-10 min)
  python scripts/build_immigration_index.py --limit 50      # smoke test
  python scripts/build_immigration_index.py --skip-wikidata
  python scripts/build_immigration_index.py --skip-loc

Attribution: Wikidata (CC0), Wikipedia (CC BY-SA), LoC (public domain).
"""
import argparse
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "cultural-content" / "immigration"
OUT = OUT_DIR / "index.json"

UA = "sixth-borough/0.1 (https://github.com/TheApexWu/sixth-borough; hackathon research)"

WDQS = "https://query.wikidata.org/sparql"
WIKI_API = "https://en.wikipedia.org/w/api.php"
LOC_API = "https://www.loc.gov/collections/federal-writers-project/"

# NYC + boroughs in Wikidata (for P551 residence / P20 place of death)
NYC_QIDS = ["Q60", "Q11299", "Q18419", "Q18424", "Q18426", "Q18432"]

SPARQL = """
SELECT DISTINCT ?person ?personLabel ?birthPlaceLabel ?birthCountryLabel
                ?birthDate ?deathDate ?occupationLabel ?article WHERE {
  ?person wdt:P31 wd:Q5 ;
          wdt:P19 ?birthPlace ;
          wdt:P569 ?birthDate .
  ?birthPlace wdt:P17 ?birthCountry .
  FILTER(?birthCountry != wd:Q30)
  FILTER(YEAR(?birthDate) >= 1800 && YEAR(?birthDate) <= 2005)
  {
    { ?person wdt:P551 wd:Q60 } UNION
    { ?person wdt:P551 wd:Q11299 } UNION
    { ?person wdt:P551 wd:Q18419 } UNION
    { ?person wdt:P551 wd:Q18424 } UNION
    { ?person wdt:P551 wd:Q18426 } UNION
    { ?person wdt:P551 wd:Q18432 } UNION
    { ?person wdt:P20 wd:Q60 } UNION
    { ?person wdt:P20 wd:Q11299 } UNION
    { ?person wdt:P20 wd:Q18419 } UNION
    { ?person wdt:P20 wd:Q18424 } UNION
    { ?person wdt:P20 wd:Q18426 } UNION
    { ?person wdt:P20 wd:Q18432 }
  }
  OPTIONAL { ?person wdt:P570 ?deathDate }
  OPTIONAL { ?person wdt:P106 ?occupation }
  ?article schema:about ?person ;
           schema:isPartOf <https://en.wikipedia.org/> .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
}
LIMIT __LIMIT__
"""

SHIP_RE = re.compile(
    r"\b(SS|RMS|MS|MV|SMS|HMS)\s+([A-Z][A-Za-z][A-Za-z \-]{1,30}?)(?=[\s,.;]|$)"
)
ARRIVAL_RE_1 = re.compile(
    r"(?:arrived|immigrated|emigrated|came|moved|landed|sailed)\s+"
    r"(?:to|in|at)\s+(?:the\s+)?"
    r"(?:United States|America|New York(?: City)?|Ellis Island|"
    r"Manhattan|Brooklyn|the Bronx|Queens|Staten Island)"
    r"[^.]{0,80}?(?:in|on|around|by)\s+(\d{4})",
    re.IGNORECASE,
)
ARRIVAL_RE_2 = re.compile(
    r"\bin\s+(\d{4})[,.][^.]{0,80}?"
    r"(?:arrived|immigrated|emigrated|landed|settled)\s+(?:to|in|at)\s+"
    r"(?:the\s+)?(?:United States|America|New York|Ellis Island)",
    re.IGNORECASE,
)
ARRIVAL_RE_3 = re.compile(
    r"(?:arrived|immigrated|emigrated|moved|settled|relocated|came)"
    r"[^.]{0,60}?(?:United States|America|New York|Ellis Island|Manhattan|"
    r"Brooklyn|the Bronx|Queens)[^.]{0,60}?(\d{4})",
    re.IGNORECASE,
)
ELLIS_RE = re.compile(r"\bEllis Island\b", re.IGNORECASE)
CASTLE_RE = re.compile(r"\bCastle Garden\b", re.IGNORECASE)
AIR_RE = re.compile(
    r"\b(JFK|LaGuardia|Kennedy (?:International )?Airport|by plane|"
    r"flew (?:into|to)|by air|airliner)\b",
    re.IGNORECASE,
)


def http_get_json(url, headers=None, timeout=60, retries=4):
    h = {"User-Agent": UA, "Accept": "application/json"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    backoff = 2.0
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                time.sleep(backoff)
                backoff *= 2
                continue
            raise
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < retries - 1:
                time.sleep(backoff)
                backoff *= 2
                continue
            raise


def query_wikidata(limit):
    effective = limit if limit else 1500
    sparql = SPARQL.replace("__LIMIT__", str(effective))
    url = WDQS + "?query=" + urllib.parse.quote(sparql) + "&format=json"
    print(f"wikidata: SPARQL (LIMIT {effective})…")
    data = http_get_json(
        url,
        headers={"Accept": "application/sparql-results+json"},
        timeout=180,
    )
    bindings = data.get("results", {}).get("bindings", [])
    people = {}
    for b in bindings:
        qid = b["person"]["value"].rsplit("/", 1)[-1]
        def v(k):
            return (b.get(k) or {}).get("value")
        if qid in people:
            occ = v("occupationLabel")
            if occ and occ not in people[qid]["occupations"]:
                people[qid]["occupations"].append(occ)
            continue
        people[qid] = {
            "qid": qid,
            "name": v("personLabel") or qid,
            "birth_place": v("birthPlaceLabel"),
            "origin_country": v("birthCountryLabel"),
            "birth_date": v("birthDate"),
            "death_date": v("deathDate"),
            "occupations": [o for o in [v("occupationLabel")] if o],
            "article": v("article"),
        }
    print(f"wikidata: {len(people)} unique people with Wikipedia articles")
    return list(people.values())


def fetch_wiki_extract(title):
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": "1",
        "redirects": "1",
        "titles": title,
        "format": "json",
        "formatversion": "2",
    }
    url = WIKI_API + "?" + urllib.parse.urlencode(params)
    data = http_get_json(url)
    pages = data.get("query", {}).get("pages", [])
    if not pages or pages[0].get("missing"):
        return ""
    return (pages[0].get("extract") or "")[:25000]


def parse_year(s):
    if not s:
        return None
    m = re.match(r"(-?\d{3,4})", s)
    return int(m.group(1)) if m else None


def extract_arrival_details(text, birth_year):
    det = {"arrival_year": None, "ship": None, "port_of_arrival": None, "mode": None}
    if not text:
        return det
    m = ARRIVAL_RE_1.search(text) or ARRIVAL_RE_2.search(text) or ARRIVAL_RE_3.search(text)
    if m:
        y = int(m.group(1))
        if 1800 <= y <= 2026 and (not birth_year or y >= birth_year):
            det["arrival_year"] = y
    sm = SHIP_RE.search(text)
    if sm:
        det["ship"] = f"{sm.group(1)} {sm.group(2).strip(' ,.;')}"
        det["mode"] = "steamship"
    if ELLIS_RE.search(text):
        det["port_of_arrival"] = "Ellis Island"
        det["mode"] = det["mode"] or "steamship"
    elif CASTLE_RE.search(text):
        det["port_of_arrival"] = "Castle Garden"
        det["mode"] = det["mode"] or "sail/steamship"
    elif AIR_RE.search(text):
        det["port_of_arrival"] = "NYC airport"
        det["mode"] = "air"
    if not det["mode"] and det["arrival_year"]:
        y = det["arrival_year"]
        if y < 1960:
            det["mode"] = "steamship"
        elif y >= 1970:
            det["mode"] = "air"
    return det


def first_paragraphs(text, n=2, max_chars=1200):
    if not text:
        return ""
    paras = [p.strip() for p in text.split("\n") if p.strip()]
    out = " ".join(paras[:n])
    return out[:max_chars]


def build_wikidata_records(people, delay=0.55):
    records = []
    total = len(people)
    for i, p in enumerate(people, 1):
        article_url = p.get("article")
        if not article_url:
            continue
        title = urllib.parse.unquote(article_url.rsplit("/", 1)[-1]).replace("_", " ")
        try:
            extract = fetch_wiki_extract(title)
        except Exception as e:
            print(f"  ! {p['name']}: {e}")
            continue
        birth_year = parse_year(p.get("birth_date"))
        det = extract_arrival_details(extract, birth_year)
        story = first_paragraphs(extract)
        if not story:
            continue
        year = det["arrival_year"] or birth_year
        age = None
        if det["arrival_year"] and birth_year:
            age = det["arrival_year"] - birth_year
        records.append({
            "id": f"wd-{p['qid']}",
            "source": "wikidata+wikipedia",
            "name": p["name"],
            "year": year,
            "birth_year": birth_year,
            "arrival_year": det["arrival_year"],
            "age_at_arrival": age,
            "origin_country": p.get("origin_country"),
            "origin_place": p.get("birth_place"),
            "ship": det["ship"],
            "port_of_arrival": det["port_of_arrival"],
            "mode": det["mode"],
            "occupations": p.get("occupations") or [],
            "story": story,
            "source_url": article_url,
        })
        if i % 25 == 0:
            print(f"  wikipedia: {i}/{total} (kept {len(records)})")
        time.sleep(delay)
    print(f"wikidata+wikipedia: {len(records)} records")
    return records


ELLIS_LIST_PAGES = [
    "List of Ellis Island immigrants",
]
# Common-noun / structural links to skip from the list page
ELLIS_SKIP = {
    "Accordion", "Admiral (United States)", "Ellis Island", "Ellis Island (film)",
    "Statue of Liberty", "New York City", "United States", "Immigration",
    "Vaudeville", "Broadway theatre", "Jewish", "Italian Americans",
}


def fetch_ellis_titles():
    titles = []
    seen = set()
    for page in ELLIS_LIST_PAGES:
        params = {
            "action": "query",
            "prop": "links",
            "titles": page,
            "pllimit": "500",
            "plnamespace": "0",
            "format": "json",
            "formatversion": "2",
        }
        url = WIKI_API + "?" + urllib.parse.urlencode(params)
        try:
            data = http_get_json(url)
        except Exception as e:
            print(f"  ! ellis list '{page}': {e}")
            continue
        pages = (data.get("query") or {}).get("pages") or []
        for p in pages:
            for link in p.get("links") or []:
                t = link.get("title")
                if not t or t in seen or t in ELLIS_SKIP:
                    continue
                seen.add(t)
                titles.append(t)
    print(f"ellis: {len(titles)} unique page titles from list articles")
    return titles


def build_ellis_records(titles, existing_urls, delay=0.55):
    records = []
    for i, title in enumerate(titles, 1):
        article_url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
        if article_url in existing_urls:
            continue
        try:
            extract = fetch_wiki_extract(title)
        except Exception as e:
            print(f"  ! {title}: {e}")
            continue
        if not extract:
            continue
        # birth year from first date in intro
        birth_year = None
        bm = re.search(r"\b(1[78]\d{2}|19[0-4]\d)\b", extract[:400])
        if bm:
            birth_year = int(bm.group(1))
        det = extract_arrival_details(extract, birth_year)
        # Ellis Island is the default port for this category
        det["port_of_arrival"] = det["port_of_arrival"] or "Ellis Island"
        det["mode"] = det["mode"] or "steamship"
        story = first_paragraphs(extract)
        if not story:
            continue
        year = det["arrival_year"] or birth_year
        age = None
        if det["arrival_year"] and birth_year:
            age = det["arrival_year"] - birth_year
        records.append({
            "id": f"ellis-{title.replace(' ', '_')}",
            "source": "wikipedia-ellis-island",
            "name": title,
            "year": year,
            "birth_year": birth_year,
            "arrival_year": det["arrival_year"],
            "age_at_arrival": age,
            "origin_country": None,
            "origin_place": None,
            "ship": det["ship"],
            "port_of_arrival": det["port_of_arrival"],
            "mode": det["mode"],
            "occupations": [],
            "story": story,
            "source_url": article_url,
        })
        if i % 25 == 0:
            print(f"  ellis: {i}/{len(titles)} (kept {len(records)})")
        time.sleep(delay)
    print(f"ellis: {len(records)} records")
    return records


def fetch_loc_fwp(max_items=200, delay=0.3):
    records = []
    queries = [
        "immigrant",
        "immigration Ellis Island",
        "Italian life history new york",
        "Jewish life history new york",
        "Irish life history new york",
    ]
    seen = set()
    for q in queries:
        for page in range(1, 6):
            params = {
                "q": q,
                "fo": "json",
                "c": "50",
                "sp": str(page),
                "fa": "location:new york",
            }
            url = LOC_API + "?" + urllib.parse.urlencode(params)
            try:
                data = http_get_json(url, timeout=60)
            except Exception as e:
                print(f"  ! loc '{q}' p{page}: {e}")
                break
            results = data.get("results") or []
            if not results:
                break
            added = 0
            for item in results:
                rid = item.get("id") or item.get("url")
                if not rid or rid in seen:
                    continue
                seen.add(rid)
                title = (item.get("title") or "").strip()
                desc = item.get("description")
                if isinstance(desc, list):
                    desc = " ".join(str(d) for d in desc if d)
                desc = (desc or "").strip()
                date = str(item.get("date") or "")
                ym = re.search(r"(18|19|20)\d{2}", date)
                year = int(ym.group(0)) if ym else 1938
                story = (desc or title)[:1200]
                if not story:
                    continue
                records.append({
                    "id": f"loc-{rid.rstrip('/').rsplit('/', 1)[-1]}",
                    "source": "loc-fwp",
                    "name": title,
                    "year": year,
                    "birth_year": None,
                    "arrival_year": None,
                    "age_at_arrival": None,
                    "origin_country": None,
                    "origin_place": None,
                    "ship": None,
                    "port_of_arrival": None,
                    "mode": None,
                    "occupations": [],
                    "story": story,
                    "source_url": item.get("url") or rid,
                })
                added += 1
                if len(records) >= max_items:
                    break
            print(f"  loc '{q}' p{page}: +{added} (total {len(records)})")
            if len(records) >= max_items or added == 0:
                break
            time.sleep(delay)
        if len(records) >= max_items:
            break
    print(f"loc-fwp: {len(records)} records")
    return records


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="cap Wikidata results")
    ap.add_argument("--skip-wikidata", action="store_true")
    ap.add_argument("--skip-loc", action="store_true")
    ap.add_argument("--skip-ellis", action="store_true")
    ap.add_argument("--loc-max", type=int, default=200)
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    all_records = []
    if not args.skip_wikidata:
        people = query_wikidata(args.limit)
        all_records.extend(build_wikidata_records(people))
    if not args.skip_ellis:
        existing = {r["source_url"] for r in all_records if r.get("source_url")}
        titles = fetch_ellis_titles()
        all_records.extend(build_ellis_records(titles, existing))
    if not args.skip_loc:
        all_records.extend(fetch_loc_fwp(max_items=args.loc_max))

    all_records.sort(key=lambda r: (r.get("year") or 9999, r.get("name") or ""))
    OUT.write_text(json.dumps(all_records, indent=2, ensure_ascii=False))

    size_kb = OUT.stat().st_size // 1024
    print(f"\nwrote {OUT} ({size_kb} KB, {len(all_records)} records)")
    years = [r["year"] for r in all_records if r.get("year")]
    if years:
        print(f"year range: {min(years)}-{max(years)}")
    print(
        f"detail coverage: "
        f"arrival_year={sum(1 for r in all_records if r.get('arrival_year'))}, "
        f"ship={sum(1 for r in all_records if r.get('ship'))}, "
        f"port={sum(1 for r in all_records if r.get('port_of_arrival'))}, "
        f"mode={sum(1 for r in all_records if r.get('mode'))}"
    )
    print("done.")


if __name__ == "__main__":
    main()
