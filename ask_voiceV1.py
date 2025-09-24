#!/usr/bin/env python3
import os, subprocess, tempfile, json, requests, shutil

MIC_DEV = os.getenv("MIC_DEV", "hw:2,0")
RATE = int(os.getenv("RATE", "16000"))
REC_SECS = int(os.getenv("SECONDS_TO_RECORD", "5"))
WHISPER_BIN = os.getenv("WHISPER_BIN", "/srv/asr/whisper.cpp/build/bin/whisper-cli")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "/srv/asr/whisper.cpp/models/ggml-small.en.bin")
LLAMA_HOST = os.getenv("LLAMA_HOST", "http://127.0.0.1:8080")

def record_wav(path):
    def run(dev):
        cmd = ["arecord", "-D", dev, "-f", "S16_LE", "-c1", "-r", str(RATE),
               "--buffer-time=100000", "--period-time=20000", "-d", str(REC_SECS), path]
        return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=False).returncode

    # 1) prime (250ms), discard
    subprocess.run(["arecord", "-D", MIC_DEV, "-f", "S16_LE", "-c1", "-r", str(RATE),
                    "--buffer-time=100000", "--period-time=20000", "-d", "0.25"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    # 2) main attempt
    rc = run(MIC_DEV)
    if rc != 0:
        # retry once with plughw and short backoff
        alt_dev = MIC_DEV.replace("hw:", "plughw:")
        subprocess.run(["sleep", "0.25"])
        rc = run(alt_dev)
        if rc != 0:
            raise RuntimeError(f"arecord failed on {MIC_DEV} and {alt_dev}")


def transcribe(path_wav):
    cmd = [WHISPER_BIN, "-m", WHISPER_MODEL, "-f", path_wav, "-otxt"]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    txt_path = path_wav + ".txt"
    with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()

def ask_llama(user_text, n_predict=256):
    prompt = (
        "<|im_start|>system\nYou are concise and no-fluff.<|im_end|>\n"
        f"<|im_start|>user\n{user_text}<|im_end|>\n"
        "<|im_start|>assistant\n"
    )
    payload = {"prompt": prompt, "n_predict": n_predict, "cache_prompt": True}
    r = requests.post(f"{LLAMA_HOST}/completion", json=payload, timeout=300)
    r.raise_for_status()
    data = r.json()
    # server variants use different keys; try common ones
    return data.get("content") or data.get("generated_text") or data.get("response") or json.dumps(data)

def main():
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav = f.name
    try:
        print(f"🎙️ Recording {REC_SECS}s …")
        record_wav(wav)
        print("🧠 Transcribing …")
        text = transcribe(wav)
        if not text:
            print("Empty transcript.")
            return
        print("You said:", text)
        print("🤖 Asking llama-server …")
        reply = ask_llama(text)
        print("\nAssistant:\n" + reply)
    finally:
        for p in (wav, wav + ".txt"):
            try: os.remove(p)
            except FileNotFoundError: pass

if __name__ == "__main__":
    main()

