import os
import time
import logging
import httpx
import requests
from deepgram import Deepgram

# === ENV VARIABLES ===
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# === Azure GPT HEADERS ===
headers = {
    "api-key": AZURE_OPENAI_API_KEY,
    "Content-Type": "application/json"
}

# === Deepgram Client ===
deepgram = Deepgram(DEEPGRAM_API_KEY)

# === STT: Deepgram File Transcription ===
async def transcribe_audio(file_path: str) -> tuple[str, float]:
    try:
        start = time.time()
        with open(file_path, 'rb') as audio:
            response = await deepgram.transcription.prerecorded(
                {
                    'buffer': audio,
                    'mimetype': 'audio/wav'
                },
                {
                    'punctuate': True,
                    'language': 'en'
                }
            )
        transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
        elapsed = time.time() - start
        logging.info(f"[STT] Transcription took {elapsed:.2f}s: {transcript}")
        return transcript or "No speech detected.", elapsed
    except Exception as e:
        logging.exception("[STT] Deepgram transcription failed")
        return "Transcription failed.", 0.0

# === LLM: Azure OpenAI GPT ===
async def ask_gpt(prompt: str) -> tuple[str, float]:
    try:
        start = time.time()
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 300
        }
        url = f"{AZURE_OPENAI_ENDPOINT}openai/deployments/{AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version={AZURE_OPENAI_API_VERSION}"

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()["choices"][0]["message"]["content"]
            elapsed = time.time() - start
            logging.info(f"[GPT] GPT took {elapsed:.2f}s: {result}")
            return result, elapsed
    except Exception as e:
        logging.exception("[GPT] GPT API error")
        return "GPT failed.", 0.0

# === TTS: ElevenLabs Streaming (Requests) ===
def play_tts_stream(text: str) -> float:
    try:
        start = time.time()

        voice_id = "EXAVITQu4vr4xnSDxMaL"  # Rachel
        model_id = "eleven_multilingual_v2"

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }

        response = requests.post(url, headers=headers, json=payload, stream=True)
        response.raise_for_status()

        import pyaudio
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=22050, output=True)

        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                stream.write(chunk)

        stream.stop_stream()
        stream.close()
        p.terminate()

        elapsed = time.time() - start
        logging.info(f"[TTS] ElevenLabs TTS took {elapsed:.2f}s")
        return elapsed

    except Exception as e:
        logging.exception("[TTS] ElevenLabs streaming failed")
        return 0.0
import os
import time
import logging
import httpx
import requests
from deepgram import Deepgram

# === ENV VARIABLES ===
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# === Azure GPT HEADERS ===
headers = {
    "api-key": AZURE_OPENAI_API_KEY,
    "Content-Type": "application/json"
}

# === Deepgram Client ===
deepgram = Deepgram(DEEPGRAM_API_KEY)

# === STT: Deepgram File Transcription ===
async def transcribe_audio(file_path: str) -> tuple[str, float]:
    try:
        start = time.time()
        with open(file_path, 'rb') as audio:
            response = await deepgram.transcription.prerecorded(
                {
                    'buffer': audio,
                    'mimetype': 'audio/wav'
                },
                {
                    'punctuate': True,
                    'language': 'en'
                }
            )
        transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
        elapsed = time.time() - start
        logging.info(f"[STT] Transcription took {elapsed:.2f}s: {transcript}")
        return transcript or "No speech detected.", elapsed
    except Exception as e:
        logging.exception("[STT] Deepgram transcription failed")
        return "Transcription failed.", 0.0

# === LLM: Azure OpenAI GPT ===
async def ask_gpt(prompt: str) -> tuple[str, float]:
    try:
        start = time.time()
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 300
        }
        url = f"{AZURE_OPENAI_ENDPOINT}openai/deployments/{AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version={AZURE_OPENAI_API_VERSION}"

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()["choices"][0]["message"]["content"]
            elapsed = time.time() - start
            logging.info(f"[GPT] GPT took {elapsed:.2f}s: {result}")
            return result, elapsed
    except Exception as e:
        logging.exception("[GPT] GPT API error")
        return "GPT failed.", 0.0

# === TTS: ElevenLabs Streaming (Requests) ===
def play_tts_stream(text: str) -> float:
    try:
        start = time.time()

        voice_id = "EXAVITQu4vr4xnSDxMaL"  # Rachel
        model_id = "eleven_multilingual_v2"

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }

        response = requests.post(url, headers=headers, json=payload, stream=True)
        response.raise_for_status()

        import pyaudio
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=22050, output=True)

        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                stream.write(chunk)

        stream.stop_stream()
        stream.close()
        p.terminate()

        elapsed = time.time() - start
        logging.info(f"[TTS] ElevenLabs TTS took {elapsed:.2f}s")
        return elapsed

    except Exception as e:
        logging.exception("[TTS] ElevenLabs streaming failed")
        return 0.0
