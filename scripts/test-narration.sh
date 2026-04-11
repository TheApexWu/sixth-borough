#!/usr/bin/env bash
# Sixth Borough — smoke test the raw llama.cpp narration server (GN100 only).
#
# Assumes scripts/start-gn100.sh is running in another terminal.
# This test hits the underlying llama.cpp /v1/chat/completions endpoint
# directly, NOT the orchestrator's /narrate endpoint. Use it only to
# verify that Nemotron itself is responding.
#
# For testing the orchestrator's stub or real /narrate path from your
# laptop, see scripts/dev-stub.sh + scripts/dev-test.sh instead.

set -euo pipefail

echo "==> Pinging narration server"

curl -s http://localhost:30000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nemotron",
    "messages": [{
      "role": "system",
      "content": "You are a historical narrator describing scenes of New York City. Speak in present tense, evocative but grounded. Two sentences max."
    }, {
      "role": "user",
      "content": "Describe Mott Haven, the Bronx, in 1978. Tenements, music, the South Bronx burning."
    }],
    "max_tokens": 200
  }' | python3 -m json.tool

echo ""
echo "==> If you see a response above, the narration loop works."
