import base64
import json
import os
from functools import wraps

from flask import Flask, jsonify, request, session
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
CORS(app)  # Enable CORS for all routes

# Initialize Firebase Admin SDK
def initialize_firebase():
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(
                json.loads(
                    base64.b64decode(
                        os.getenv("FIREBASE_CREDENTIALS_BASE64")
                    ).decode('utf-8')
                )
            )
            firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Firebase initialization failed: {str(e)}")
        raise

initialize_firebase()

# Auth decorator
def firebase_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return {"error": "Unauthorized"}, 401
        return f(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    return "Backend is running! Use the frontend to interact."

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or 'token' not in data:
        return jsonify({"error": "Token missing"}), 400
        
    try:
        decoded_token = auth.verify_id_token(data['token'])
        session['user'] = decoded_token
        return jsonify({
            "status": "success",
            "user": {
                "uid": decoded_token['uid'],
                "email": decoded_token.get('email')
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@app.route("/profile")
@firebase_required
def profile():
    return jsonify({"user": session['user']})

@app.route("/logout")
def logout():
    session.pop('user', None)
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))