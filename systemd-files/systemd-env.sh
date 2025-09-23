sudo tee /etc/default/llama-server >/dev/null <<'EOF'
LLAMA_ARG_MODEL=/srv/llm/models/qwen2.5-7b-instruct-q5_k_m.gguf
LLAMA_ARG_CTX_SIZE=4096
LLAMA_ARG_THREADS=4
LLAMA_ARG_NGL=0
LLAMA_SERVER_HOST=0.0.0.0
LLAMA_SERVER_PORT=8080
EOF

