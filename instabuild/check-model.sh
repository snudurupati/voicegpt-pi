#!/usr/bin/env bash
# Usage: ./check-model.sh /path/to/model.gguf

MODEL="$1"

if [[ -z "$MODEL" ]]; then
  echo "Usage: $0 /path/to/model.gguf"
  exit 1
fi

BIN="/srv/llm/llama.cpp/build/bin/llama-cli"

if [[ ! -x "$BIN" ]]; then
  echo "Error: llama-cli not found at $BIN"
  exit 1
fi

echo "==> Dry-run load test (no tokens)..."
$BIN -m "$MODEL" -c 8192 -t $(nproc) -ngl 0 -n 0 -p "" >/dev/null
if [[ $? -eq 0 ]]; then
  echo "[OK] Model loaded successfully"
else
  echo "[FAIL] Model failed to load"
  exit 1
fi

echo "==> One-token probe..."
OUT=$($BIN -m "$MODEL" -c 8192 -t $(nproc) -ngl 0 -n 1 -p "hi" 2>/dev/null)
if [[ $? -eq 0 ]]; then
  echo "[OK] Generation path works"
  echo "Sample output: $OUT"
else
  echo "[FAIL] Model failed during generation"
  exit 1
fi

