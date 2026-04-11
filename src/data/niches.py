"""Niche taxonomy. The lenses through which the time machine surfaces events.

For the hackathon demo only `hip-hop` is fully populated; the other niches
exist as architecture-proof toggles with 1-2 events each. The niche filter
UI in the renderer reads NICHE_DISPLAY to render its toggle list.
"""

from __future__ import annotations

from enum import Enum


class Niche(str, Enum):
    HIP_HOP = "hip-hop"
    QUEER_HISTORY = "queer-history"
    DEMOLISHED_THEATERS = "demolished-theaters"
    JAZZ = "jazz"
    SALSA = "salsa"
    PUNK = "punk"
    IMMIGRATION = "immigration"


# Display metadata for the niche filter UI.
# `active` controls whether the toggle is on by default in the demo.
NICHE_DISPLAY: dict[str, dict] = {
    Niche.HIP_HOP.value: {
        "label": "Hip-Hop Heads",
        "color": "#e67e22",
        "active": True,
        "description": "Birthplace and early years of hip-hop in the Bronx",
    },
    Niche.QUEER_HISTORY.value: {
        "label": "Queer History",
        "color": "#9b59b6",
        "active": False,
        "description": "Stonewall, Christopher Street, ballroom houses, ACT UP geography",
    },
    Niche.DEMOLISHED_THEATERS.value: {
        "label": "Demolished Theaters",
        "color": "#c0392b",
        "active": False,
        "description": "Loew's Paradise, Bronx Opera House, Windsor Theater, the Roxy",
    },
    Niche.JAZZ.value: {
        "label": "Jazz Heads",
        "color": "#f39c12",
        "active": False,
        "description": "Apollo, Lenox Lounge, Minton's Playhouse, Cotton Club",
    },
    Niche.SALSA.value: {
        "label": "Salsa Spanish Harlem",
        "color": "#e74c3c",
        "active": False,
        "description": "Casino Theater, the Palladium, Eddie Palmieri, Fania Records era",
    },
    Niche.PUNK.value: {
        "label": "Punk Bowery",
        "color": "#34495e",
        "active": False,
        "description": "CBGB, Max's Kansas City, Mudd Club, the Pyramid Club",
    },
    Niche.IMMIGRATION.value: {
        "label": "Immigration Flow",
        "color": "#16a085",
        "active": False,
        "description": "Lower East Side tenements, Crown Heights, Sunset Park, Flushing waves",
    },
}
