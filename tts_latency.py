import time
import requests

# === CONFIGURATION ===
ELEVEN_API_KEY = "sk_7da99f405583e5d955273d78b62b06ae436612622c07663a"
VOICE_ID = "EXAVITQu4vr4xnSDxMaL"
MODEL_ID = "eleven_multilingual_v2"
CHUNK_SIZE = 1024

# === URL & HEADERS ===
url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"

headers = {
    "xi-api-key": ELEVEN_API_KEY,
    "Content-Type": "application/json"
}

payload = {
    "text": "Hello! This is a latency test using ElevenLabs streaming TTS.",
    "model_id": MODEL_ID,
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75,
        "style": 0.0,
        "use_speaker_boost": True
    }
}


def measure_latency():
    print(f"\n🔊 Measuring latency for payload: {payload['text']!r}")
    start_time = time.time()

    with requests.post(url, headers=headers, json=payload, stream=True) as resp:
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP Error: {e}")
            print("🔎 Response content:", resp.text)
            return

        first_chunk_time = None
        chunk_count = 0

        for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
            if not chunk:
                continue

            if first_chunk_time is None:
                first_chunk_time = time.time()
                latency = first_chunk_time - start_time
                print(f"⏱️ First audio chunk received in {latency:.3f} seconds")

            chunk_count += 1

        total_time = time.time() - start_time
        print(f"✅ Finished streaming {chunk_count} chunks in {total_time:.3f} seconds")


if __name__ == "__main__":
    measure_latency()
