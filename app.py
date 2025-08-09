from flask import Flask, request, jsonify, session, redirect, url_for
import firebase_admin
from firebase_admin import credentials, auth
from functools import wraps
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")  # Set a random secret key

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
    return "Welcome! <a href='/login'>Login</a>"

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
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Render needs this
