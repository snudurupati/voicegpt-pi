# JarvisPi: Always-On Local Voice Assistant

This project turns a Raspberry Pi 5 into a **voice-only assistant** (Jarvis-style), powered by local open-source models.  
No OpenAI API or cloud dependency required.

---

## Features

- 🎙️ **Voice input** with `arecord`  
  - Works with USB mics/speakerphones (tested on Poly Sync 10).  
  - Prime + retry logic ensures reliable capture.

- 🧠 **Speech-to-Text (STT)** via [whisper.cpp](https://github.com/ggerganov/whisper.cpp)  
  - Converts captured audio into text locally.

- 🤖 **Local LLM** with [llama.cpp](https://github.com/ggerganov/llama.cpp)  
  - Runs models like `qwen2.5-7b-instruct` in server mode.  
  - Reachable via REST API (`http://jarvispi.local:8080`).

- 🔊 **Text-to-Speech (TTS)** via [piper](https://github.com/rhasspy/piper)  
  - Natural-sounding voices, runs fully on-device.  
  - Patched to handle sample-rate quirks.  
  - Added **priming + prepended silence** so the first word isn’t clipped.

- ⚡ **Configurable via environment variables** (mic device, sample rate, TTS timings, etc.)

---

## Workflow

1. **Record audio** → USB mic with `arecord`  
2. **Transcribe** → Whisper model (tiny/small recommended on RPi5)  
3. **LLM completion** → POST transcript to `llama-server`  
4. **TTS synthesis** → Piper generates speech  
5. **Playback** → Audio routed back to speakerphone

---

## Install Summary

1. **Clone repos & build**  
   - `llama.cpp` (for local LLM)  
   - `whisper.cpp` (for STT)  
   - `piper` (for TTS)

2. **Run llama-server** (systemd unit provided):
   ```bash
   curl http://jarvispi.local:8080/health
   ```

3. **Set up voices** (Piper):
   ```bash
   # example
   voices/en_US-amy-medium.onnx
   voices/en_US-amy-medium.onnx.json
   ```

4. **Symlink espeak-ng data** (fix missing phontab):
   ```bash
   sudo ln -s /usr/lib/aarch64-linux-gnu/espeak-ng-data /usr/share/espeak-ng-data
   ```

5. **Run the voice loop**:
   ```bash
   ./ask_voice.py
   ```

---

## Config (Environment Variables)

| Variable         | Default                     | Purpose |
|------------------|-----------------------------|---------|
| `MIC_DEV`        | `hw:2,0`                   | ALSA device for mic capture |
| `RATE`           | `16000`                    | Capture sample rate |
| `SECONDS_TO_RECORD` | `5`                     | Recording duration |
| `WHISPER_BIN`    | `/srv/asr/whisper.cpp/build/bin/whisper-cli` | Path to whisper binary |
| `WHISPER_MODEL`  | `/srv/asr/whisper.cpp/models/ggml-small.en.bin` | STT model |
| `LLAMA_HOST`     | `http://127.0.0.1:8080`    | llama-server REST endpoint |
| `N_PREDICT`      | `256`                      | Tokens to predict |
| `PIPER_BIN`      | `/srv/tts/piper/build/piper` | Path to piper binary |
| `PIPER_MODEL`    | `/srv/tts/voices/en_US-amy-medium.onnx` | TTS voice model |
| `PIPER_CONFIG`   | `$PIPER_MODEL.json`        | Voice config JSON |
| `SPEAKER_DEV`    | `plughw:2,0`               | ALSA device for playback |
| `TTS_PAD_MS`     | `400`                      | Prepend silence (ms) to WAV |
| `TTS_PRIME_SEC`  | `0.30`                     | Duration of ALSA `/dev/zero` prime |
| `TTS_SETTLE_SEC` | `0.20`                     | Wait after prime before playback |

---

## What Works Today

✅ End-to-end local pipeline (record → Whisper → llama-server → Piper → speaker)  
✅ No cloud dependencies (fully offline)  
✅ Fix for clipped first words in audio playback  
✅ Configurable timings for different hardware  
✅ Web access to LLM via `http://jarvispi.local:8080`

---

## Next Steps

- Add **wake-word** (e.g. with [openWakeWord](https://github.com/dscripka/openWakeWord))  
- Continuous VAD-based listening  
- Auto-start `ask_voice.py` as a systemd service  
- Explore lightweight voices & smaller STT models for faster runtime

---

## License

MIT — free to use, hack, and extend.
