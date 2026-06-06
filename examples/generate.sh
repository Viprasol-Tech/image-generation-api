#!/usr/bin/env bash
# Part of Image Generation API by Viprasol Tech Private Limited (https://viprasol.com).
# Minimal curl demo. Start the server first: `python -m image_generation_api`.
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"

echo "==> Health check"
curl -s "${BASE_URL}/health"
echo

echo "==> Generate (base64 JSON)"
curl -s -X POST "${BASE_URL}/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a serene mountain lake at dawn", "width": 256, "height": 256, "seed": 42}'
echo

echo "==> Generate (raw PNG -> generated_demo.png)"
curl -s -X POST "${BASE_URL}/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "neon city skyline", "response_format": "png"}' \
  --output generated_demo.png
echo "Saved generated_demo.png"
