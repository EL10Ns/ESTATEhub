#!/usr/bin/env python
"""
EstateHub API Server Launcher
Run this file to start the Flask API server
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import Flask app from local flask/app.py (not from Flask package)
import importlib.util
spec = importlib.util.spec_from_file_location("app", os.path.join(os.path.dirname(__file__), "flask", "app.py"))
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)
app = app_module.app

if __name__ == '__main__':
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"""
    ╔══════════════════════════════════════════╗
    ║        EstateHub API Server              ║
    ║                                          ║
    ║  Starting on http://{host}:{port}           ║
    ║  Debug mode: {'ON' if debug else 'OFF':>26} ║
    ║                                          ║
    ║  📍 Local: http://localhost:{port:<23} ║
    ║  🌐 Network: http://your-ip:{port:<20} ║
    ║                                          ║
    ║  Press CTRL+C to stop                   ║
    ╚══════════════════════════════════════════╝
    """)
    
    app.run(host=host, port=port, debug=debug)
