#!/usr/bin/env bash
# Sixth Borough — run the pytest suite.
#
# Tests cover: schema validation, seed JSON loader, stub narration backend.
# Run before pushing any commit to your branch.
#
# Usage:
#   pip install -r requirements.txt
#   ./scripts/dev-test.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

exec pytest tests/ -v
