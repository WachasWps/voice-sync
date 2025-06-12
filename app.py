import os
import asyncio
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from voice_logic import ask_gpt, play_tts_stream

# Load environment variables
load_dotenv()

# Setup Flask app and CORS
app = Flask(__name__)
CORS(app)

# Setup logger
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
        response = asyncio.run(ask_gpt(prompt))
        logging.info(f"[TEXT] GPT response: {response}")
        play_tts_stream(response)
        return jsonify({"response": response})
    except Exception as e:
        logging.exception("[TEXT] Error during processing")
        return jsonify({"error": str(e)}), 500


@app.route("/api/audio", methods=["POST"])
def handle_audio():
    audio_file = request.files["audio"]
    audio_path = "temp.wav"
    audio_file.save(audio_path)
    logging.info(f"[AUDIO] Received audio and saved to {audio_path}")

    try:
        # TODO: Add actual Deepgram STT logic here
        prompt = "Hello from audio!"  # Replace with transcription later
        logging.info(f"[AUDIO] Transcribed prompt (mock): {prompt}")
        
        response = asyncio.run(ask_gpt(prompt))
        logging.info(f"[AUDIO] GPT response: {response}")
        play_tts_stream(response)
        return jsonify({"response": response})
    except Exception as e:
        logging.exception("[AUDIO] Error during audio processing")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    logging.info("Starting Flask server...")
    app.run(debug=True)
