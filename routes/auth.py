from flask import Blueprint, request, jsonify
import bcrypt

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    name = data["name"]
    email = data["email"]
    password = data["password"]

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    return jsonify({
        "message": "User registered",
        "name": name,
        "email": email
    })


    @auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    email = data["email"]
    password = data["password"]

    return jsonify({
        "message": "Login successful",
        "token": "dummy-jwt-token"
    })