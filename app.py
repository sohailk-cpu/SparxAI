from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# Set your Groq API key here
GROQ_API_KEY = "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"  # 🔁 Replace this later

# Add this global variable
conversation_history = [
    {"role": "system", "content": "You are SunoAi, a helpful AI assistant. You were created by Sohail. Always respond kindly and if someone asks 'who made you', say 'I was created by Sohail'."}
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '')
    conversation_history.append({"role": "user", "content": user_msg})

    response = get_groq_response(conversation_history)
    conversation_history.append({"role": "assistant", "content": response})

    return jsonify({'response': response})

def get_groq_response(messages):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": messages
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return "Sorry, I couldn't connect to the AI service."

if __name__ == '__main__':
    app.run(debug=True)