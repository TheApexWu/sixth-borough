# NYC Immigration Timeline Data

Annual NYC immigration arrivals, 1719–2026 — drives the garden-hose dot-spray visualization (one scalar per year maps to particle pressure/density).

## Files

| File | Purpose |
|---|---|
| `us_totals_1820_2023_dhs.csv` | Raw DHS Yearbook Table 1 — US totals. Verbatim, unmodified. |
| `nyc_immigration_timeline.csv` | **Primary output.** 308 annual rows, NYC-weighted, with tier + source columns. |
| `nyc_immigration_timeline.json` | Same data as JSON, wrapped with metadata. Load this from the frontend. |

Rebuild with `python3 scripts/build_immigration_timeline.py` — script is deterministic and self-contained, no external fetches.

## Tiers (data quality)

| Tier | Years | Source | Notes |
|---|---|---|---|
| 1 | 1820–2023 | DHS Yearbook of Immigration Statistics, Table 1 | Federal records. Authoritative. |
| 2 | 1719–1819 | Scholarly decadal anchors, monotone-cubic interpolated | Colonial + early federal. Shape is sound, exact annual values are estimates. See `scripts/build_immigration_timeline.py` for anchor list and citations. |
| 3 | 2024–2026 | Held flat at 2023 value | DHS has not published these years. |

## NYC share weighting

DHS publishes US totals only. NYC arrivals are derived by multiplying by a piecewise historical "Port of NY share" that reflects Castle Garden (1855–1890), Ellis Island (1892–1954), and post-Ellis LPR-by-metro data:

| Era | NYC share |
|---|---|
| 1719–1755 | 15% (colonial NYC behind Philly, Boston, Charleston) |
| 1756–1800 | 20% |
| 1801–1824 | 35% (pre-Erie-Canal rise) |
| 1825–1854 | 60% (Erie Canal opens, NYC becomes #1 port) |
| 1855–1891 | 70% (Castle Garden era) |
| 1892–1924 | 75% (Ellis Island peak) |
| 1925–1945 | 65% (Quota Acts + Depression + WWII) |
| 1946–1954 | 55% (Ellis winding down) |
| 1955–1975 | 30% (JFK airport opens; Ellis closed 1954) |
| 1976–1990 | 22% |
| 1991–2010 | 15% |
| 2011–2026 | 13% (current NYC metro LPR share) |

Historical shape is well-supported; exact era boundaries are judgment calls based on Ellis Island Foundation arrival tables, Historical Statistics of the US, and DHS LPR-by-state reports.

## Record schema

```jsonc
{
  "year": 1907,
  "us_arrivals": 1285350,     // DHS or colonial estimate
  "nyc_share": 0.75,           // era-weighted share applied
  "nyc_arrivals": 964012,      // us_arrivals * nyc_share
  "intensity": 1.0,            // nyc_arrivals / peak (peak year = 1907)
  "tier": 1,                   // data quality tier
  "source": "dhs-table-1"
}
```

The `intensity` field (0..1, normalized to the 1907 peak) is what the garden-hose viz should bind to — maps directly to particle spawn rate, initial velocity, and spray cone angle.

## Sources

- DHS Office of Homeland Security Statistics. *Yearbook of Immigration Statistics 2023*, Table 1: Persons Obtaining Lawful Permanent Resident Status, Fiscal Years 1820 to 2023. [ohss.dhs.gov](https://ohss.dhs.gov/topics/immigration/yearbook/2023/table1)
- Carter, Susan B. et al. *Historical Statistics of the United States, Millennial Edition.* Cambridge University Press, 2006. (Port of NY annual column, 1820–1957)
- Bailyn, Bernard. *Voyagers to the West: A Passage in the Peopling of America on the Eve of the Revolution.* Knopf, 1986.
- Grabbe, Hans-Jürgen. "European Immigration to the United States in the Early National Period, 1783–1820." *Proceedings of the American Philosophical Society* 133.2 (1989).
- McClelland, Peter D. and Richard J. Zeckhauser. *Demographic Dimensions of the New Republic.* Cambridge University Press, 1982.
- Statue of Liberty–Ellis Island Foundation. Annual arrival counts, 1892–1954.
