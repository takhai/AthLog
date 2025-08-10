import base64
from flask import Flask, json, request, jsonify, session, redirect, url_for
import firebase_admin
from firebase_admin import credentials, auth
from functools import wraps
import os
from dotenv import load_dotenv
from flask_cors import CORS  # For handling CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")  # Use consistent env var name


# Initialize Firebase Admin SDK (Backend)
cred = credentials.Certificate(
    json.loads(base64.b64decode(
        os.getenv("FIREBASE_CREDENTIALS_BASE64")
    ).decode()
)

firebase_admin.initialize_app(cred)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")  # Set a random secret key
CORS(app)  # Enable CORS for all routes

# 🔒 Decorator to protect routes (require login)
def firebase_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return {"error": "Unauthorized"}, 401
        return f(*args, **kwargs)
    return wrapper

# 🏠 Homepage (Public)
@app.route("/")
def home():
    return "Backend is running! Use the frontend to interact."

# 🔑 Login (Verify Firebase Token)
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    id_token = data.get("token")
    
    try:
        decoded_token = auth.verify_id_token(id_token)
        session['user'] = decoded_token  # Store user in session
        return jsonify({"status": "success", "user": decoded_token})
    except Exception as e:
        return jsonify({"error": str(e)}), 401

# 🔒 Protected Route (Requires Login)
@app.route("/profile")
@firebase_required
def profile():
    return jsonify({"user": session['user']})

# 🚪 Logout
@app.route("/logout")
def logout():
    session.pop('user', None)
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))