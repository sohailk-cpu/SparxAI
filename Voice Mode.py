from flask import Flask, request, jsonify, send_file
import requests
import os

app = Flask(__name__)

ELEVENLABS_API_KEY = "sk-c3a9d12363dc718e73a610d853b3544c520be8c95c1adb67"
VOICE_ID = "LQqGm0gT4pft0DECaryn"  # Hindi voice ID (change if needed)

@app.route('/speak', methods=['POST'])
def speak():
    text = request.json.get('text', '')
    
    # Optional: Use Hindi script for better pronunciation
    if not text.strip():
        return jsonify({"error": "No text received"}), 400

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.7
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            print(response.text)
            return jsonify({"error": "Failed to get audio"}), 500

        audio_path = os.path.join("static", "voice.mp3")
        with open(audio_path, "wb") as f:
            f.write(response.content)

        return jsonify({"success": True})
    
    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/audio')
def audio():
    return send_file("static/voice.mp3", mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run(port=5050)
    
