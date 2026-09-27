"""
app.py

Flask backend for the Document AI chatbot.
Serves the chat UI and proxies chat messages to the Gemini API,
using the restricted persona/prompt defined in chatbot_config.py.
"""

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

from chatbot_config import SYSTEM_PROMPT, BOT_NAME

# Load environment variables from .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. Please add it to your .env file."
    )

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    system_instruction=SYSTEM_PROMPT,
)

app = Flask(__name__)


@app.route("/")
def index():
    """Render the chat UI."""
    return render_template("index.html", bot_name=BOT_NAME)


@app.route("/chat", methods=["POST"])
def chat():
    """Receive a user message, send it to Gemini, and return the reply."""
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "Empty message."}), 400

    try:
        response = model.generate_content(user_message)
        reply_text = (response.text or "").strip()

        if not reply_text:
            reply_text = (
                "Sorry, I couldn't generate a response. Please try again."
            )

        return jsonify({"reply": reply_text})

    except Exception as exc:  # noqa: BLE001
        app.logger.error("Gemini API error: %s", exc)
        return jsonify(
            {"error": "Something went wrong while contacting the AI model."}
        ), 500


if __name__ == "__main__":
    app.run(debug=True)
