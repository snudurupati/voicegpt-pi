#!/usr/bin/env bash
# Usage: ./bench.sh /path/to/model.gguf [tokens]
MODEL="${1:?usage: $0 MODEL.gguf [TOKENS] }"
TOKENS="${2:-128}"
BIN="/srv/llm/llama.cpp/build/bin/llama-cli"

# quiet run, no warmup, discard output
/usr/bin/time -f "%e" -o /tmp/llama_bench_secs.txt \
  "$BIN" -m "$MODEL" -c 4096 -t 4 -ngl 0 --no-warmup -n "$TOKENS" \
  -p "Write a terse 3-sentence summary of Transformers." >/dev/null 2>&1

secs=$(cat /tmp/llama_bench_secs.txt)
awk -v t="$TOKENS" -v s="$secs" 'BEGIN { printf "tokens=%d  seconds=%.2f  tok/s=%.2f\n", t, s, t/s }'

