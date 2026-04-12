"""Building biography subsystem.

Zero-dependency RAG over local NYC Open Data sources. Joins building footprints,
NYPL Milstein photos, cultural events, demolished landmarks by BIN and lat/lon
proximity. Synthesizes via the existing local Nemotron llama-server. No external
dependencies, no embeddings, no vector DB, no LangChain.

Drafted Apr 12 ~02:30 UTC, Session 45 (post-Carson-departure pivot to the
Cross-Bronx -> 1520 Sedgwick -> Kool Herc causal arc). The single feature that
turns Sixth Borough from "viz with captions" into "look up a building."
"""
