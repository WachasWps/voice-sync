import os
import httpx
import logging
from elevenlabs import stream, Voice, VoiceSettings

# Load environment variables
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# GPT Request Headers
headers = {
    "api-key": AZURE_OPENAI_API_KEY,
    "Content-Type": "application/json"
}


async def ask_gpt(prompt):
    logging.info(f"[GPT] Sending prompt to Azure: {prompt}")
    
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
        logging.info(f"[GPT] Received response: {result}")
        return result


def play_tts_stream(text):
    logging.info(f"[TTS] Speaking text: {text}")
    try:
        stream(
            text,
            api_key=ELEVENLABS_API_KEY,
            voice=Voice(
                voice_id="EXAVITQu4vr4xnSDxMaL",  # Replace with your voice ID
                settings=VoiceSettings(stability=0.4, similarity_boost=0.75)
            )
        )
        logging.info("[TTS] Streaming playback finished")
    except Exception as e:
        logging.exception("[TTS] Error during streaming TTS")
