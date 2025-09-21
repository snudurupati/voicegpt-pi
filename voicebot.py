import sounddevice as sd
import numpy as np
from openai import OpenAI
import io, wave, os

# Load API key from env variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ALSA device index for mic/speaker (set in .env)
DEVICE_INDEX = int(os.getenv("VOICEGPT_DEVICE_INDEX", 2))
RECORD_SECONDS = int(os.getenv("VOICEGPT_RECORD_SECONDS", 5))

def record(seconds=RECORD_SECONDS, samplerate=16000):
    print("🎙️ Recording...")
    audio = sd.rec(int(seconds*samplerate), samplerate=samplerate,
                   channels=1, dtype='int16', device=DEVICE_INDEX)
    sd.wait()
    return audio, samplerate

def to_wav(audio, samplerate):
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio.tobytes())
    buf.seek(0)
    return buf

while True:
    audio, sr = record()
    wav = to_wav(audio, sr)

    # Speech-to-text
    transcript = client.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe",
        file=("speech.wav", wav)
    )
    user_text = transcript.text.strip()
    print("You said:", user_text)
    if not user_text:
        continue

    # Chat response
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_text}]
    )
    reply = resp.choices[0].message.content
    print("Assistant:", reply)

    # Text-to-speech
    speech = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=reply
    )

    audio_out = np.frombuffer(speech.read(), dtype=np.int16)
    sd.play(audio_out, samplerate=24000, device=DEVICE_INDEX)
    sd.wait()
