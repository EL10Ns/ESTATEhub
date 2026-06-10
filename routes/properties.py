from flask import Blueprint, request, jsonify
from db import get_connection

prop_bp = Blueprint("properties", __name__)

@prop_bp.route("/", methods=["GET"])
def get_properties():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM properties")
    data = cursor.fetchall()

    return jsonify(data)

@prop_bp.route("/", methods=["POST"])
def create_property():
    data = request.json

    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO properties (agent_id, title, price, city, description)
    VALUES (%s, %s, %s, %s, %s)
    """

    cursor.execute(sql, (
        data["agent_id"],
        data["title"],
        data["price"],
        data["city"],
        data["description"]
    ))

    conn.commit()

    return jsonify({"message": "Property created"})