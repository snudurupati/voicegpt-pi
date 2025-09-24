#!/usr/bin/env python3
import os, subprocess, tempfile, json, time, glob, sys
import wave
import contextlib
import time
import subprocess
import os
import tempfile

# ====== Config via env (with sane defaults) ======
MIC_DEV        = os.getenv("MIC_DEV", "hw:2,0")  # Poly Sync capture
RATE           = int(os.getenv("RATE", "16000"))
REC_SECS       = int(os.getenv("SECONDS_TO_RECORD", "5"))

WHISPER_BIN    = os.getenv("WHISPER_BIN", "/srv/asr/whisper.cpp/build/bin/whisper-cli")
WHISPER_MODEL  = os.getenv("WHISPER_MODEL", "/srv/asr/whisper.cpp/models/ggml-small.en.bin")

LLAMA_HOST     = os.getenv("LLAMA_HOST", "http://127.0.0.1:8080")
N_PREDICT      = int(os.getenv("N_PREDICT", "256"))

PIPER_BIN      = os.getenv("PIPER_BIN", "/srv/tts/piper/build/piper")
PIPER_MODEL    = os.getenv("PIPER_MODEL", "/srv/tts/voices/en/en_US/danny/low/en_US-danny-low.onnx")
PIPER_CONFIG   = os.getenv("PIPER_CONFIG", PIPER_MODEL + ".json")

SPEAKER_DEV    = os.getenv("SPEAKER_DEV", "plughw:2,0")

ESPEAK_DATA    = os.getenv("ESPEAKNG_DATA_PATH", "/usr/lib/aarch64-linux-gnu/espeak-ng-data")
LD_LIB_PATH    = "/srv/tts/piper/build"

# ====== Helpers ======
def _read_wav_meta(path):
    with contextlib.closing(wave.open(path, 'rb')) as w:
        params = w.getparams()  # nchannels, sampwidth, framerate, nframes, comptype, compname
        return {
            "channels": params.nchannels,
            "sampwidth": params.sampwidth,  # bytes per sample
            "rate": params.framerate,
            "frames": params.nframes,
        }

def prepend_silence(in_wav, out_wav, ms=250):
    meta = _read_wav_meta(in_wav)
    n_silence = int(meta["rate"] * ms / 1000.0)
    silence_frame = b"\x00" * (meta["sampwidth"] * meta["channels"])
    with contextlib.closing(wave.open(in_wav, 'rb')) as r, \
         contextlib.closing(wave.open(out_wav, 'wb')) as w:
        w.setnchannels(meta["channels"])
        w.setsampwidth(meta["sampwidth"])
        w.setframerate(meta["rate"])
        # write leading silence
        w.writeframes(silence_frame * n_silence)
        # copy original audio
        w.writeframes(r.readframes(meta["frames"]))
    return meta  # return original meta so we can prime correctly

def play_wav_with_prime_same_rate(wav_path, device):
    meta = _read_wav_meta(wav_path)
    # 1) prime with silence at the SAME rate / channels
    #    use /dev/zero as 16-bit signed PCM; aplay will format it
    subprocess.run(
        ["aplay",
         "-D", device,
         "-f", "S16_LE",
         "-r", str(meta["rate"]),
         "-c", str(meta["channels"]),
         "-d", "0.15", "/dev/zero"],
        stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
    )
    # 2) small settle delay
    time.sleep(0.08)
    # 3) play with cushier buffers
    subprocess.run(
        ["aplay",
         "-D", device,
         "--buffer-time", "200000",
         "--period-time", "50000",
         wav_path],
        check=True
    )

def run(*args, check=True, **kw):
    return subprocess.run(args, check=check, **kw)

def arecord_prime_and_capture(wav_path):
    """Prime the device to avoid first-run failure, then record; retry once with plughw."""
    # prime 250ms, ignore errors
    subprocess.run(
        ["arecord", "-D", MIC_DEV, "-f", "S16_LE", "-c1", "-r", str(RATE), "-d", "0.25",
         "--buffer-time=100000", "--period-time=20000"],
        stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
    )
    # main attempt
    cmd = ["arecord", "-D", MIC_DEV, "-f", "S16_LE", "-c1", "-r", str(RATE),
           "--buffer-time=100000", "--period-time=20000", "-d", str(REC_SECS), wav_path]
    rc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT).returncode
    if rc != 0:
        # retry with plughw and small backoff
        alt = MIC_DEV.replace("hw:", "plughw:")
        time.sleep(0.25)
        cmd = ["arecord", "-D", alt, "-f", "S16_LE", "-c1", "-r", str(RATE),
               "--buffer-time=100000", "--period-time=20000", "-d", str(REC_SECS), wav_path]
        run(*cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

def whisper_transcribe(wav_path):
    """Run whisper-cli and return transcript text."""
    cmd = [WHISPER_BIN, "-m", WHISPER_MODEL, "-f", wav_path, "-otxt"]
    run(*cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    with open(wav_path + ".txt", "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()

def ask_llama(user_text):
    """POST to llama-server and return assistant text."""
    prompt = (
        "<|im_start|>system\nYou are concise and no-fluff.<|im_end|>\n"
        f"<|im_start|>user\n{user_text}<|im_end|>\n"
        "<|im_start|>assistant\n"
    )
    payload = {"prompt": prompt, "n_predict": N_PREDICT, "cache_prompt": True}
    import requests
    r = requests.post(f"{LLAMA_HOST}/completion", json=payload, timeout=300)
    r.raise_for_status()
    data = r.json()
    return data.get("content") or data.get("generated_text") or data.get("response") or json.dumps(data)

def play_wav_with_prime(wav_path):
    # 1) Prime the device with 100 ms of silence (raw 16 kHz mono)
    subprocess.run(
            ["aplay", "-D", SPEAKER_DEV, "-f", "S16_LE", "-r", "16000", "-c", "1", "-d", "0.35", "/dev/zero"],
        stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
    )

    # 2) Give hardware a moment to settle (50 ms is usually enough)
    time.sleep(0.2)

    # 3) Play the real WAV with a cushier buffer
    subprocess.run(
        ["aplay", "-D", SPEAKER_DEV, "--buffer-time", "200000", "--period-time", "50000", wav_path],
        check=True
    )


def piper_say(text):
    """
    Your Piper build ignores -o and prints the absolute WAV path on stdout,
    while writing the audio file into the current working directory.
    We run in /tmp, parse the printed path, then play the file.
    """
    env = os.environ.copy()
    env["ESPEAKNG_DATA_PATH"] = ESPEAK_DATA
    env["LD_LIBRARY_PATH"] = LD_LIB_PATH + (":" + env["LD_LIBRARY_PATH"] if env.get("LD_LIBRARY_PATH") else "")

    cwd = "/tmp"
    t0 = time.time()

    # Call Piper WITHOUT -o (your build will print the output path)
    proc = subprocess.run(
        [PIPER_BIN, "-m", PIPER_MODEL, "-c", PIPER_CONFIG, "-s", "0"],
        input=text, text=True, capture_output=True, env=env, cwd=cwd
    )
    if proc.returncode != 0:
        raise RuntimeError(f"piper failed: {proc.stderr or proc.stdout}")

    # parse .wav path from stdout (last non-empty absolute path ending with .wav)
    wav_path = None
    for line in (proc.stdout or "").splitlines()[::-1]:
        line = line.strip()
        if line.endswith(".wav") and os.path.isabs(line) and os.path.exists(line):
            wav_path = line
            break

    # fallback: newest .wav in /tmp since t0
    if not wav_path:
        candidates = [p for p in glob.glob(os.path.join(cwd, "*.wav")) if os.path.getmtime(p) >= t0 - 1]
        wav_path = max(candidates, key=os.path.getmtime) if candidates else None

    if not wav_path or not os.path.exists(wav_path):
        raise FileNotFoundError(f"Could not locate Piper WAV. stdout:\n{proc.stdout}")

    # NEW: prepend 250 ms silence, then prime/play at the same sample rate
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as fpad:
        padded = fpad.name
    prepend_silence(wav_path, padded, ms=500)
    try:
        play_wav_with_prime_same_rate(padded, SPEAKER_DEV)
    finally:
        try:
            os.remove(padded)
        except Exception:
            pass

    # cleanup
    try: os.remove(wav_path)
    except Exception: pass

def main():
    # 1) record
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav = f.name
    try:
        print(f"🎙️ Recording {REC_SECS}s …")
        arecord_prime_and_capture(wav)

        # 2) transcribe
        print("🧠 Transcribing …")
        text = whisper_transcribe(wav)
        if not text:
            print("Empty transcript.")
            return
        print("You said:", text)

        # 3) ask LLM
        print("🤖 Asking llama-server …")
        reply = ask_llama(text)
        print("\nAssistant:\n" + reply)

        # 4) TTS
        print("🔊 Speaking …")
        piper_say(reply)

    finally:
        for p in (wav, wav + ".txt"):
            try: os.remove(p)
            except FileNotFoundError: pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(130)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

