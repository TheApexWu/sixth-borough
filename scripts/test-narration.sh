#!/usr/bin/env bash
# Sixth Borough — quick smoke test for the narration server
# Assumes start.sh is running in another terminal.

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
