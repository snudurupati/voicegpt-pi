# JarvisPi: Local LLM Voice Assistant

JarvisPi is an always-on Raspberry Pi project that turns your device into a **local voice assistant** using open‑source LLMs instead of cloud APIs.  
It no longer relies on OpenAI API keys — everything runs **fully offline**.

## Current Setup

- **Hardware**
  - Raspberry Pi 5 (16 GB RAM, NVMe SSD boot)
  - Poly Sync 10 (USB speaker + microphone)
- **Software**
  - [llama.cpp](https://github.com/ggerganov/llama.cpp) built with CMake and OpenBLAS
  - Qwen2.5‑7B‑Instruct (quantized GGUF, Q4_K_M or Q5_K_M)
  - Systemd service running `llama-server` on boot
  - Web interface and REST API available on LAN (`http://jarvispi.local:8080`)

## Features

- Local inference of 7B LLM (Qwen2.5) on Pi 5 — no cloud dependency
- REST API (`/completion`) and health endpoint (`/health`)
- Built‑in web chat UI accessible from any device on the LAN
- Auto‑start at boot via `systemd`
- Configurable context size, threads, quantization levels

## Installation Summary

1. **Build llama.cpp**  
   ```bash
   cd /srv/llm/llama.cpp
   cmake -B build -DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS
   cmake --build build --config Release -j$(nproc)
   ```

2. **Download & merge model (example Qwen2.5‑7B‑Instruct Q5_K_M)**  
   ```bash
   huggingface-cli download Qwen/Qwen2.5-7B-Instruct-GGUF      qwen2.5-7b-instruct-q5_k_m.gguf
   ```

3. **Test run manually**  
   ```bash
   ./build/bin/llama-cli -m /srv/llm/models/qwen2.5-7b-instruct-q5_k_m.gguf -c 4096 -t 4 -ngl 0 -i
   ```
   ```bash
   /srv/llm/llama.cpp/build/bin/llama-gguf-split --merge qwen2.5-7b-instruct-q5_k_m-00001-of-00002.gguf qwen2.5-7b-instruct-q5_k_m.gguf
	```
	
4. **Systemd service** ensures auto‑start:  
   ```ini
   [Service]
   User=snudurupati
   WorkingDirectory=/srv/llm/llama.cpp
   EnvironmentFile=/etc/default/llama-server
   ExecStart=/srv/llm/llama.cpp/build/bin/llama-server --host 0.0.0.0 --port 8080
   Restart=always
   RestartSec=2
   ```

## Usage

- Web UI: `http://jarvispi.local:8080`
- Health check:  
  ```bash
  curl -s http://jarvispi.local:8080/health
  ```
- Completion:  
  ```bash
  curl -s http://jarvispi.local:8080/completion     -H "Content-Type: application/json"     -d '{"prompt":"Say hi in one short line.","n_predict":32}'
  ```

## Next Steps

- **ASR (Automatic Speech Recognition):** integrate `whisper.cpp` or `faster-whisper` for voice input.  
- **TTS (Text to Speech):** integrate [Piper](https://github.com/rhasspy/piper) to play LLM responses aloud.  
- **Pipeline Goal:** Mic → Whisper → llama-server → Piper → Speaker.

---
Fully local. Always on. No cloud required.
