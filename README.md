# voicegpt-pi

Always-on, **voice-only** ChatGPT device on **Raspberry Pi 5**.  
Directly uses OpenAI APIs (no extra server): **record → STT → LLM → TTS → play**.

## Hardware

- Raspberry Pi 5 (16GB)
- Official Pi 27W USB-C PSU
- Case with active cooler (e.g., CanaKit)
- **Plantronics Poly Sync 10 USB** (mic + speaker, one cable)
- NVMe SSD (256–512GB) + **52Pi P33 M.2 NVMe M-Key PoE Hat**
- microSD (16–32GB) for first boot/recovery only
- (Optional) Mini-HDMI → HDMI, keyboard/mouse for first setup

## TL;DR

```bash
# 0) Headless Pi 5 booting from NVMe (you already did this)
# 1) Update + reboot
sudo apt update && sudo apt full-upgrade -y
sudo rpi-eeprom-update -a
sudo reboot

# 2) Audio tools
sudo apt install -y alsa-utils pulseaudio

# 3) Verify Poly Sync appears (note the card,device)
arecord -l
aplay   -l

# 4) Create venv
sudo apt install -y python3-venv python3-pip
python3 -m venv ~/voicebot && source ~/voicebot/bin/activate

# 5) Install deps
pip install openai sounddevice numpy

# 6) Run the demo (set your key each shell or use .env)
OPENAI_API_KEY=sk-... python3 voicebot.py
```

## Repo structure

```
voicegpt-pi/
├─ README.md
├─ voicebot.py               # 5s record → STT → Chat → TTS → playback (Poly Sync)
├─ .env.example              # place your OPENAI_API_KEY here
├─ scripts/
│  ├─ audio_test.sh          # quick arecord/aplay sanity checks
│  └─ install_deps.sh        # installs system + python deps
└─ systemd/
   └─ voicegpt.service       # optional: run on boot
```

## Configuration

Create `.env` (copy from `.env.example`):

```env
OPENAI_API_KEY=sk-your-key
# ALSA device index for Poly Sync (from arecord -l / aplay -l)
VOICEGPT_DEVICE_INDEX=2
# Record length for the simple demo
VOICEGPT_RECORD_SECONDS=5
```

## Usage

### 1) Audio sanity checks

```bash
arecord -l        # find your mic card,device (e.g., 2,0)
aplay -l          # find your speaker card,device (often same 2,0)

# Record 3s and play it back (replace 2,0 if different)
arecord -D plughw:2,0 -f cd -d 3 test.wav
aplay   -D plughw:2,0 test.wav
```

### 2) Run the demo

`voicebot.py` (included) does:

- 5s record @16k mono  
- `audio.transcriptions.create` → text  
- `chat.completions.create` → reply  
- `audio.speech.create` → 24k PCM  
- playback via Poly Sync

```bash
source ~/voicebot/bin/activate
export $(grep -v '^#' .env | xargs)   # load env vars
python3 voicebot.py
```

## Systemd (run on boot)

`systemd/voicegpt.service` (example):

```ini
[Unit]
Description=VoiceGPT Pi (OpenAI voice loop)
After=network-online.target sound.target
Wants=network-online.target

[Service]
Type=simple
EnvironmentFile=/home/pi/voicegpt-pi/.env
WorkingDirectory=/home/pi/voicegpt-pi
ExecStart=/home/pi/voicebot/bin/python3 /home/pi/voicegpt-pi/voicebot.py
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Install:

```bash
sudo cp systemd/voicegpt.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable voicegpt
sudo systemctl start voicegpt
sudo systemctl status voicegpt
```

## Troubleshooting

- **“Device busy / not found”**: recheck indices with `arecord -l`, `aplay -l`. Use `plughw:X,Y` not `hw:` if format conversion is needed.  
- **No audio out**: test with `aplay -D plughw:2,0 /usr/share/sounds/alsa/Front_Center.wav`.  
- **Choppy playback**: ensure active cooler is working; `top` for CPU; try wired Ethernet; reduce TTS length.  
- **Latency feels high**: this simple demo batches 5s. Next step is streaming (wake-word + VAD + partials).  

## Next steps (optional)

- Replace fixed recording window with **wake word + VAD** loop (openWakeWord + webrtcvad).  
- Use **streaming Responses API** and stream TTS chunks for near-realtime barge-in.  
- Add LED states (listening / thinking / speaking) with a USB status light.

## License

MIT (or your choice).
