/srv/llm/llama.cpp/build/bin/llama-cli \
  -m /srv/llm/models/qwen2.5-7b-instruct-q5_k_m.gguf \
  -c 8192 -t $(nproc) -ngl 0 -i

