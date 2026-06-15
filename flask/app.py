from flask import Flask
from flask_cors import CORS
import os
import sys

# Add parent directory to path so we can import from root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = Flask(__name__)
CORS(app)

# Import routes after adding path
from routes import auth, properties

# Register blueprints
app.register_blueprint(auth.auth_bp, url_prefix="/api/auth")
app.register_blueprint(properties.prop_bp, url_prefix="/api/properties")

@app.route('/', methods=['GET'])
def health():
    return {"message": "Real Estate API is running"}, 200

if __name__ == '__main__':
    app.run(
        host=os.getenv('API_HOST', '0.0.0.0'),
        port=int(os.getenv('API_PORT', 5001)),
        debug=os.getenv('FLASK_DEBUG', True)
    )