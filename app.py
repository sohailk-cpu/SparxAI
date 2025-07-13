from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests, os, uuid, datetime, json
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'super-secret-key'
CORS(app)

login_manager = LoginManager()
login_manager.init_app(app)

# ---------------------- User Storage ----------------------
USERS_FILE = 'users.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users_data):
    with open(USERS_FILE, 'w') as f:
        json.dump(users_data, f)

users = load_users()

# ---------------------- Flask-Login Setup ----------------------
class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    file_users = load_users()
    if user_id in file_users:
        return User(user_id)
    return None

# ---------------------- Routes ----------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/voice')
def voice_chat():
    return render_template('voice.html')

@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    users = load_users()
    if username in users:
        return jsonify({"success": False, "error": "Username already exists"})

    if not username or not password:
        return jsonify({"success": False, "error": "Username or password missing"})

    users[username] = {'password': password}
    save_users(users)
    return jsonify({"success": True})

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    users = load_users()  # ✅ JSON file se fresh users laa raha hai

    print("🔍 All users from file:", users)  # 🐞 Debug print

    if username in users and users[username]['password'] == password:
        user = User(username)
        login_user(user)
        return jsonify({"success": True})

    return jsonify({"success": False, "error": "Invalid credentials"})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route('/history')
@login_required
def history():
    user_id = current_user.id
    history = user_memory.get(user_id, [])
    return render_template("history.html", history=history)

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '')
    if current_user.is_authenticated:
        user_id = current_user.id
    else:
        user_id = session.get('user_id') or str(uuid.uuid4())
        session['user_id'] = user_id

    reply = get_groq_response(user_msg, user_id)
    return jsonify({'response': reply})

# ---------------------- AI Response ----------------------
user_memory = {}

def get_groq_response(message, user_id):
    message = message.lower()

    if any(word in message for word in ["date", "day today", "aaj ka din", "aaj kya din", "aaj kya hai", "today date", "what day today"]):
        now = datetime.datetime.now()
        return f"Aaj ka din hai: {now.strftime('%A, %d %B %Y')}"

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
    }

    memory = user_memory.get(user_id, [])
    memory.append({"role": "user", "content": message})

    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "system", "content": "You are TalkGPT, a helpful assistant created by Sohail."}] + memory[-5:]
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        result = response.json()
        print("🔍 Groq response:", result)

        if "choices" not in result:
            return "⚠️ AI response not received. Check your API key."

        content = result['choices'][0]['message']['content']
        memory.append({"role": "assistant", "content": content})
        user_memory[user_id] = memory
        return content
    except Exception as e:
        print("❌ Error:", e)
        return "Sorry, I couldn't connect to the AI service."

if __name__ == "__main__":
    app.run(debug=True)
