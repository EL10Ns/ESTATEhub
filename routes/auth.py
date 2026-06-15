from flask import Blueprint, request, jsonify, g
from functools import wraps
import bcrypt
from db import get_connection
import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

auth_bp = Blueprint("auth", __name__)


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
TOKEN_EXP_HOURS = int(os.getenv("TOKEN_EXP_HOURS", 24))


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("user_id")
            if not user_id:
                return jsonify({"error": "Invalid token payload"}), 401

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, first_name, last_name, role FROM users WHERE id=%s", (user_id,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if not user:
                return jsonify({"error": "User not found"}), 401

            g.current_user = user
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except Exception as e:
            return jsonify({"error": "Token is invalid", "details": str(e)}), 401

        return f(*args, **kwargs)

    return decorated


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json or {}

    first_name = data.get("first_name") or data.get("name")
    last_name = data.get("last_name", "")
    email = data.get("email")
    password = data.get("password")
    phone = data.get("phone")
    role = data.get("role", "customer")

    if not first_name or not email or not password:
        return jsonify({"error": "first_name, email and password are required"}), 400

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Check existing email
        cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            return jsonify({"error": "Email already registered"}), 409

        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        cursor.execute(
            "INSERT INTO users (first_name, last_name, email, password, phone, role) VALUES (%s,%s,%s,%s,%s,%s)",
            (first_name, last_name, email, hashed, phone, role),
        )
        conn.commit()
        user_id = cursor.lastrowid

        return jsonify({"message": "User registered", "user_id": user_id, "email": email}), 201
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        if conn:
            conn.close()


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        stored_pw = user.get("password")
        if not stored_pw or not bcrypt.checkpw(password.encode("utf-8"), stored_pw.encode("utf-8")):
            return jsonify({"error": "Invalid credentials"}), 401

        payload = {
            "user_id": user.get("id"),
            "email": email,
            "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXP_HOURS),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)

        return jsonify({"message": "Login successful", "token": token}), 200
    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        if conn:
            conn.close()