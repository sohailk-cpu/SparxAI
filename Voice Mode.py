from flask import Flask, render_template, request, jsonify
import requests, os, uuid
from flask_cors import CORS

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

@app.route('/voice')
def voice_home():
    return render_template('voice.html')

@app.route('/voice-chat', methods=['POST'])
def voice_chat():
    data = request.json
    user_text = data.get('text')

    # Send to Groq for text-based response
    groq_headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
    }

    groq_data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": user_text}]
    }

    try:
        groq_response = requests.post("https://api.groq.com/openai/v1/chat/completions",
                                      headers=groq_headers, json=groq_data)
        ai_text = groq_response.json()['choices'][0]['message']['content']
    except Exception as e:
        return jsonify({"error": "Groq Error", "message": str(e)})

    # Send that response to ElevenLabs for voice
    eleven_headers = {
        "xi-api-key": "sk_c3a9d12363dc718e73a610d853b3544c520be8c95c1adb67",
        "Content-Type": "application/json"
    }

    eleven_data = {
        "text": ai_text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    try:
        tts_response = requests.post(
            "https://api.elevenlabs.io/v1/text-to-speech/LQqGm0gT4pft0DECaryn/stream",
            headers=eleven_headers,
            json=eleven_data
        )

        if tts_response.status_code == 200:
            with open("static/response.mp3", "wb") as f:
                f.write(tts_response.content)
            return jsonify({"success": True, "audio_url": "/static/response.mp3"})
        else:
            return jsonify({"error": "TTS failed", "details": tts_response.text})

    except Exception as e:
        return jsonify({"error": "TTS error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
