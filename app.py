from flask import Flask, render_template, request, jsonify, session
import requests
import os
import uuid
from flask_cors import CORS
import datetime  # ✅ Yeh line zaroori hai

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'your-secret-key'
CORS(app)

user_memory = {}

@app.route('/')
def home():
    return render_template('index.html')

def get_session_id():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return session['user_id']

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '')
    user_id = get_session_id()
    reply = get_groq_response(user_msg, user_id)
    return jsonify({'response': reply})

def get_groq_response(message, user_id):
    message = message.lower()

    # 🔍 Local date detection
    if any(word in message for word in ["date", "day today", "aaj ka din", "aaj kya din", "aaj kya din h", "aaj kya hai", "aaj ka din kya hai", "today date", "what day today"]):
        now = datetime.datetime.now()
        formatted_date = now.strftime("%A, %d %B %Y")  # e.g., Saturday, 13 July 2025
        return f"Aaj ka din hai: {formatted_date}"

    # Normal AI call
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": "Bearer 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",  # ✅ API key yahan daal
        "Content-Type": "application/json"
    }

    memory = user_memory.get(user_id, [])
    memory.append({"role": "user", "content": message})

    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "system", "content": "You are SunoAi, a helpful assistant created by Sohail."}] + memory[-5:]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        content = result['choices'][0]['message']['content']
        memory.append({"role": "assistant", "content": content})
        user_memory[user_id] = memory
        return content
    except Exception as e:
        print("❌ Error:", e)
        return "Sorry, I couldn't connect to the AI service."

if __name__ == "__main__":
    app.run(debug=True)
