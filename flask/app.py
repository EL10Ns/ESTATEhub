from flask import Flask
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)

from routes import auth, properties


app.register_blueprint(auth.auth_bp, url_prefix="/api/auth")
app.register_blueprint(properties.prop_bp, url_prefix="/api/properties")

def get_db():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="estate",
        cursorclass=pymysql.cursors.DictCursor
    )