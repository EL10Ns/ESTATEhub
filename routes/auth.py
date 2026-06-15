from flask import Blueprint, request, jsonify
import bcrypt
from db import get_connection
import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    
    if not all(k in data for k in ['name', 'email', 'password']):
        return jsonify({"error": "Missing required fields"}), 400

    name = data["name"]
    email = data["email"]
    password = data["password"]

    # Hash password
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        sql = "INSERT INTO users (first_name, email, password, role) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (name, email, hashed.decode('utf-8'), 'customer'))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "User registered successfully",
            "email": email
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    
    if not all(k in data for k in ['email', 'password']):
        return jsonify({"error": "Missing email or password"}), 400

    email = data["email"]
    password = data["password"]

    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        sql = "SELECT * FROM users WHERE email = %s"
        cursor.execute(sql, (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Generate JWT token
        payload = {
            'user_id': user['id'],
            'email': user['email'],
            'exp': datetime.utcnow() + timedelta(minutes=int(os.getenv('JWT_EXPIRY_MINUTES', 1440)))
        }
        token = jwt.encode(payload, os.getenv('JWT_SECRET', 'secret'), algorithm=os.getenv('JWT_ALGORITHM', 'HS256'))
        
        return jsonify({
            "message": "Login successful",
            "access_token": token,
            "user": {
                "id": user['id'],
                "email": user['email'],
                "name": user['first_name']
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500