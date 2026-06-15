import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'estate'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'cursorclass': pymysql.cursors.DictCursor
}

def get_connection():
    """Get a new database connection"""
    return pymysql.connect(**DB_CONFIG)

def init_db():
    """Initialize the database with tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Read and execute the SQL schema
    with open('flask/db.sql', 'r') as f:
        sql_statements = f.read().split(';')
        for statement in sql_statements:
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                    conn.commit()
                except pymysql.err.DatabaseError as e:
                    print(f"Database error: {e}")
                    conn.rollback()
    
    cursor.close()
    conn.close()
    print("Database initialized successfully!")
