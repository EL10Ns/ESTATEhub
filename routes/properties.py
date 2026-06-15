from flask import Blueprint, request, jsonify
from db import get_connection
import os
from datetime import datetime
from functools import wraps
import jwt

prop_bp = Blueprint("properties", __name__)

# Ensure uploads directory exists
UPLOAD_DIR = 'uploads/properties'
os.makedirs(UPLOAD_DIR, exist_ok=True)

def token_required(f):
    """Decorator to require JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split(" ")[1]
            except IndexError:
                return jsonify({"error": "Invalid token format"}), 401
        
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        
        try:
            jwt.decode(token, os.getenv('JWT_SECRET', 'secret'), algorithms=[os.getenv('JWT_ALGORITHM', 'HS256')])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    return decorated

@prop_bp.route("/", methods=["GET"])
def get_properties():
    """Get all properties"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM properties ORDER BY created_at DESC")
        data = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@prop_bp.route("/<int:property_id>", methods=["GET"])
def get_property(property_id):
    """Get a single property"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM properties WHERE id = %s", (property_id,))
        data = cursor.fetchone()
        cursor.close()
        conn.close()

        if not data:
            return jsonify({"error": "Property not found"}), 404

        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@prop_bp.route("/", methods=["POST"])
@token_required
def create_property():
    """Create a new property (requires authentication)"""
    try:
        data = request.form
        files = request.files.getlist('files')

        if not all(k in data for k in ['title', 'price', 'city']):
            return jsonify({"error": "Missing required fields"}), 400

        conn = get_connection()
        cursor = conn.cursor()

        sql = """
        INSERT INTO properties (agent_id, title, price, city, description, address, bedrooms, bathrooms, area, property_type, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(sql, (
            data.get('agent_id', 1),
            data['title'],
            data['price'],
            data['city'],
            data.get('description', ''),
            data.get('address', ''),
            data.get('bedrooms', 0),
            data.get('bathrooms', 0),
            data.get('area', 0),
            data.get('property_type', 'house'),
            data.get('status', 'available')
        ))
        
        property_id = cursor.lastrowid
        conn.commit()

        # Handle image uploads
        if files:
            for file in files:
                if file and file.filename:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = timestamp + file.filename
                    filepath = os.path.join(UPLOAD_DIR, filename)
                    file.save(filepath)
                    
                    # Save image path to database
                    img_sql = "INSERT INTO property_images (property_id, image_path) VALUES (%s, %s)"
                    cursor.execute(img_sql, (property_id, f'/uploads/properties/{filename}'))
            
            conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "message": "Property created successfully",
            "property_id": property_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@prop_bp.route("/<int:property_id>", methods=["PUT"])
@token_required
def update_property(property_id):
    """Update a property (requires authentication)"""
    try:
        data = request.form

        conn = get_connection()
        cursor = conn.cursor()

        # Check if property exists
        cursor.execute("SELECT * FROM properties WHERE id = %s", (property_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Property not found"}), 404

        # Update property
        update_fields = []
        values = []
        for key in ['title', 'price', 'city', 'description', 'address', 'bedrooms', 'bathrooms', 'area', 'property_type', 'status']:
            if key in data:
                update_fields.append(f"{key} = %s")
                values.append(data[key])

        if update_fields:
            values.append(property_id)
            sql = f"UPDATE properties SET {', '.join(update_fields)} WHERE id = %s"
            cursor.execute(sql, values)
            conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Property updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@prop_bp.route("/<int:property_id>", methods=["DELETE"])
@token_required
def delete_property(property_id):
    """Delete a property (requires authentication)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Delete images first
        cursor.execute("SELECT image_path FROM property_images WHERE property_id = %s", (property_id,))
        images = cursor.fetchall()
        for img in images:
            img_path = img['image_path'].lstrip('/')
            if os.path.exists(img_path):
                os.remove(img_path)
        
        # Delete from database
        cursor.execute("DELETE FROM property_images WHERE property_id = %s", (property_id,))
        cursor.execute("DELETE FROM properties WHERE id = %s", (property_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Property deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500