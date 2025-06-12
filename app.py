import os
import asyncio
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from voice_logic import ask_gpt, play_tts_stream, transcribe_audio

# === Load environment variables ===
load_dotenv()

# === Setup Flask app and CORS ===
app = Flask(__name__)
CORS(app)

# === Setup logger ===
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

@app.route("/api/text", methods=["POST"])
def handle_text():
    data = request.json
    prompt = data.get("prompt", "")

    logging.info(f"[TEXT] Received prompt: {prompt}")
    try:
        total_start = asyncio.get_event_loop().time()

        response, llm_time = asyncio.run(ask_gpt(prompt))
        logging.info(f"[TEXT] GPT response: {response}")

        tts_time = play_tts_stream(response)
        total_time = asyncio.get_event_loop().time() - total_start

        return jsonify({
            "response": response,
            "timing": {
                "stt": 0.0,
                "llm": round(llm_time, 2),
                "tts": round(tts_time, 2),
                "total": round(total_time, 2)
            }
        })
    except Exception as e:
        logging.exception("[TEXT] Error during text prompt processing")
        return jsonify({"error": str(e)}), 500


@app.route("/api/audio", methods=["POST"])
def handle_audio():
    audio_file = request.files["audio"]
    audio_path = "temp.wav"
    audio_file.save(audio_path)
    logging.info(f"[AUDIO] Received audio and saved to {audio_path}")

    try:
        total_start = asyncio.get_event_loop().time()

        # === STT
        transcript, stt_time = asyncio.run(transcribe_audio(audio_path))
        logging.info(f"[AUDIO] Transcription: {transcript}")

        # === LLM
        gpt_response, llm_time = asyncio.run(ask_gpt(transcript))
        logging.info(f"[AUDIO] GPT response: {gpt_response}")

        # === TTS
        tts_time = play_tts_stream(gpt_response)

        total_time = asyncio.get_event_loop().time() - total_start

        return jsonify({
            "transcript": transcript,
            "response": gpt_response,
            "timing": {
                "stt": round(stt_time, 2),
                "llm": round(llm_time, 2),
                "tts": round(tts_time, 2),
                "total": round(total_time, 2)
            }
        })

    except Exception as e:
        logging.exception("[AUDIO] Error during audio processing")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    logging.info("🚀 Starting Flask server...")
    app.run(debug=True)
