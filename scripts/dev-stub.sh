#!/usr/bin/env bash
# Sixth Borough — start the stub narration server on :30000.
#
# This is the dev mode anyone can run on any laptop. No GPU, no model
# download, no GN100 required. The stub returns templated narration
# that satisfies the same /narrate contract as the real Nemotron, so
# the renderer code never has to know which backend is wired.
#
# Usage:
#   pip install -r requirements.txt
#   ./scripts/dev-stub.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

export NARRATION_MODE=stub

echo "==> Starting Sixth Borough orchestrator (stub mode) on :30000"
echo "==> Health check: curl http://localhost:30000/health"
echo "==> Stop with Ctrl-C"
echo ""

exec uvicorn src.orchestrator.main:app --host 0.0.0.0 --port 30000 --reload
