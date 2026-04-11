#!/usr/bin/env python3
"""
Build a unified annual NYC immigration series, 1719–2026.

Three eras, three data qualities (tracked in `source_tier`):

  tier 1 — federal records (1820–2023). DHS Yearbook Table 1 gives US totals;
           NYC arrivals derived by multiplying by a piecewise Port-of-NY share.
  tier 2 — colonial/early-federal decadal estimates (1719–1819). Smoothed
           from scholarly anchors (Bailyn, Grabbe, McClelland/Zeckhauser,
           Historical Statistics of the US). Precise annual values are a
           monotone cubic interpolation between decade centers.
  tier 3 — forward projection (2024–2026). Held flat at the 2023 value since
           DHS has not published these years yet.

The purpose of this dataset is to drive the "garden-hose" dot-spray viz:
one scalar per year, representing NYC immigration intensity. Absolute
accuracy is secondary to the correct shape: colonial dribble, Castle
Garden rise, Ellis Island gusher, 1924-quota cliff, mid-century trickle,
post-1965 modern rise.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data" / "immigration"
DHS_CSV = DATA / "us_totals_1820_2023_dhs.csv"
OUT_JSON = DATA / "nyc_immigration_timeline.json"
OUT_CSV = DATA / "nyc_immigration_timeline.csv"


# ── tier 2: colonial/early-federal decadal anchors (annual averages) ──
# Each anchor is the ESTIMATED ANNUAL AVERAGE for that decade, US-total.
# Sourced from:
#   - Bailyn, "Voyagers to the West" (1986) — 1760s–1770s British migration
#   - Grabbe, "European Immigration to the US, 1783-1820" (1989)
#   - McClelland & Zeckhauser, "Demographic Dimensions of the New Republic"
#   - US Census, Historical Statistics of the United States, Ad1–Ad2
#   - Wikipedia synthesis ~60k/decade for 1790–1820
# These are deliberately round numbers — the sources disagree at the
# thousands level and nobody claims precision here.
COLONIAL_ANCHORS = [
    (1715, 2500),   # early colonial, sparse migration
    (1725, 4000),   # Scots-Irish & Palatine German flows begin
    (1735, 6000),   # peak Scots-Irish & German Pennsylvania influx
    (1745, 4000),   # King George's War disruption
    (1755, 8000),   # pre-Revolutionary surge (Bailyn)
    (1765, 7500),   # continued high, then Stamp Act tensions
    (1775, 3000),   # Revolution begins, migration collapses
    (1785, 3000),   # post-war rebuild
    (1795, 6000),   # early federal, ~60k/decade
    (1805, 6000),   # Jeffersonian era
    (1815, 6000),   # War of 1812 dip, then recovery
    (1820, 8390),   # federal records begin (matches DHS tier 1)
]


# ── NYC Port share of US immigration, by era ──
# Historical share of total US immigrant arrivals entering through the
# Port of New York (Castle Garden, then Ellis Island, then JFK/LaGuardia).
# Post-1954 "NYC share" reflects the NYC metro share of new LPRs (green
# cards) rather than port arrivals, since Ellis Island closed in 1954
# and overseas arrivals scattered across many airports.
#
# Sources: Historical Statistics of the US (Port of NY column), Ellis
# Island Foundation annual arrival counts, DHS LPR-by-state tables.
NYC_SHARE = [
    # (year_start, year_end, share)
    (1719, 1755, 0.15),   # colonial NYC is 3rd/4th port after Philly, Boston, Charleston
    (1756, 1800, 0.20),   # gradual rise; NYC surpasses Boston
    (1801, 1824, 0.35),   # pre-Erie-Canal, NYC ascendant
    (1825, 1854, 0.60),   # Erie Canal opens, NYC becomes #1 port
    (1855, 1891, 0.70),   # Castle Garden era (opened 1855)
    (1892, 1924, 0.75),   # Ellis Island peak
    (1925, 1945, 0.65),   # Quota Acts + Depression + WWII
    (1946, 1954, 0.55),   # post-war, Ellis Island winding down
    (1955, 1975, 0.30),   # Ellis closed; JFK opens; LA/Miami rising
    (1976, 1990, 0.22),   # NYC metro share of LPRs
    (1991, 2010, 0.15),   # Sun Belt / Cali dominance
    (2011, 2026, 0.13),   # current NYC metro LPR share
]


def monotone_cubic_interpolate(anchors: list[tuple[int, float]], years: range) -> dict[int, float]:
    """Fritsch-Carlson monotone cubic interpolation between decadal anchors.

    Guarantees no overshoot — important so the curve doesn't dip negative
    around sharp drops (e.g. Revolutionary War), and doesn't spike above
    the nearest anchors.
    """
    xs = [float(a[0]) for a in anchors]
    ys = [float(a[1]) for a in anchors]
    n = len(xs)
    # Secant slopes
    d = [(ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]) for i in range(n - 1)]
    # Tangents at each point
    m = [0.0] * n
    m[0] = d[0]
    m[-1] = d[-1]
    for i in range(1, n - 1):
        if d[i - 1] * d[i] <= 0:
            m[i] = 0.0
        else:
            m[i] = (d[i - 1] + d[i]) / 2.0
    # Fritsch-Carlson adjustment to preserve monotonicity
    for i in range(n - 1):
        if d[i] == 0:
            m[i] = 0.0
            m[i + 1] = 0.0
            continue
        a = m[i] / d[i]
        b = m[i + 1] / d[i]
        s = a * a + b * b
        if s > 9.0:
            t = 3.0 / (s ** 0.5)
            m[i] = t * a * d[i]
            m[i + 1] = t * b * d[i]

    out: dict[int, float] = {}
    for y in years:
        x = float(y)
        if x <= xs[0]:
            out[y] = max(0.0, ys[0])
            continue
        if x >= xs[-1]:
            out[y] = max(0.0, ys[-1])
            continue
        # Find segment
        i = 0
        while i < n - 1 and not (xs[i] <= x <= xs[i + 1]):
            i += 1
        h = xs[i + 1] - xs[i]
        t = (x - xs[i]) / h
        h00 = 2 * t ** 3 - 3 * t ** 2 + 1
        h10 = t ** 3 - 2 * t ** 2 + t
        h01 = -2 * t ** 3 + 3 * t ** 2
        h11 = t ** 3 - t ** 2
        val = h00 * ys[i] + h10 * h * m[i] + h01 * ys[i + 1] + h11 * h * m[i + 1]
        out[y] = max(0.0, val)
    return out


def nyc_share_for(year: int) -> float:
    for y0, y1, s in NYC_SHARE:
        if y0 <= year <= y1:
            return s
    raise ValueError(f"no NYC share defined for year {year}")


def load_dhs_totals() -> dict[int, int]:
    with DHS_CSV.open() as f:
        reader = csv.DictReader(f)
        return {int(row["year"]): int(row["arrivals"]) for row in reader}


def main() -> None:
    dhs = load_dhs_totals()

    records: list[dict] = []

    # Tier 2: colonial + early federal (1719–1819)
    colonial_us = monotone_cubic_interpolate(COLONIAL_ANCHORS, range(1719, 1820))
    for year in range(1719, 1820):
        us = round(colonial_us[year])
        share = nyc_share_for(year)
        nyc = round(us * share)
        records.append({
            "year": year,
            "us_arrivals": us,
            "nyc_share": round(share, 2),
            "nyc_arrivals": nyc,
            "tier": 2,
            "source": "colonial-estimate",
        })

    # Tier 1: federal records (1820–2023)
    for year in range(1820, 2024):
        us = dhs[year]
        share = nyc_share_for(year)
        nyc = round(us * share)
        records.append({
            "year": year,
            "us_arrivals": us,
            "nyc_share": round(share, 2),
            "nyc_arrivals": nyc,
            "tier": 1,
            "source": "dhs-table-1",
        })

    # Tier 3: forward projection (2024–2026)
    last = dhs[2023]
    for year in range(2024, 2027):
        share = nyc_share_for(year)
        nyc = round(last * share)
        records.append({
            "year": year,
            "us_arrivals": last,
            "nyc_share": round(share, 2),
            "nyc_arrivals": nyc,
            "tier": 3,
            "source": "held-flat-from-2023",
        })

    # Normalize for the garden-hose viz — each year gets an intensity 0..1
    # scaled to the series max, which will drive particle-spray pressure.
    peak = max(r["nyc_arrivals"] for r in records)
    for r in records:
        r["intensity"] = round(r["nyc_arrivals"] / peak, 4)

    DATA.mkdir(parents=True, exist_ok=True)

    with OUT_JSON.open("w") as f:
        json.dump({
            "description": "Annual NYC immigration, 1719–2026. Drives the garden-hose dot-spray visualization.",
            "peak_year": max(records, key=lambda r: r["nyc_arrivals"])["year"],
            "peak_nyc_arrivals": peak,
            "records": records,
        }, f, indent=2)

    with OUT_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["year", "us_arrivals", "nyc_share", "nyc_arrivals", "intensity", "tier", "source"])
        writer.writeheader()
        writer.writerows(records)

    print(f"wrote {len(records)} rows")
    print(f"  peak: {peak:,} NYC arrivals in {max(records, key=lambda r: r['nyc_arrivals'])['year']}")
    print(f"  tier 1 (dhs):       {sum(1 for r in records if r['tier'] == 1)} years")
    print(f"  tier 2 (colonial):  {sum(1 for r in records if r['tier'] == 2)} years")
    print(f"  tier 3 (projected): {sum(1 for r in records if r['tier'] == 3)} years")


if __name__ == "__main__":
    main()
