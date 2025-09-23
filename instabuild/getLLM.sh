cd /srv/llm/models
# Q5_K_M (slightly better quality, needs ~1–2 GB more RAM)
huggingface-cli download Qwen/Qwen2.5-7B-Instruct-GGUF --include "qwen2.5-7b-instruct-q5_k_m*.gguf" --local-dir /srv/llm/models --local-dir-use-symlinks False

# ./llama-gguf-split --merge <first-split-file-path> <merged-file-path>
cd /srv/llm/models
/srv/llm/llama.cpp/build/bin/llama-gguf-split --merge qwen2.5-7b-instruct-q5_k_m-00001-of-00002.gguf qwen2.5-7b-instruct-q5_k_m.gguf

