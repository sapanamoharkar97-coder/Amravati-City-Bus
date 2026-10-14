import os
import sys
import logging
from pathlib import Path
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

from config import Config
from db import test_connection, ensure_demo_accounts
from utils.decorators import api_response

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Locate Frontend Directory
FRONTEND_DIR = Path(__file__).resolve().parent.parent / 'frontend'

def create_app():
    """Application factory initializing Flask app, CORS, blueprints, and routes."""
    app = Flask(
        __name__,
        static_folder=str(FRONTEND_DIR),
        static_url_path=''
    )
    app.config.from_object(Config)

    # Enable Cross-Origin Resource Sharing
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})

    # Register Blueprints
    from routes.auth_routes import auth_bp
    from routes.admin_routes import admin_bp
    from routes.bus_routes import bus_bp
    from routes.route_routes import route_bp
    from routes.stop_routes import stop_bp
    from routes.staff_routes import staff_bp
    from routes.schedule_routes import schedule_bp
    from routes.booking_routes import booking_bp
    from routes.ticket_routes import ticket_bp
    from routes.report_routes import report_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(bus_bp)
    app.register_blueprint(route_bp)
    app.register_blueprint(stop_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(ticket_bp)
    app.register_blueprint(report_bp)

    # Health Check and Diagnostics
    @app.route('/api/health', methods=['GET'])
    def health_check():
        db_status = test_connection()
        return jsonify({
            "status": "healthy" if db_status.get("success") else "degraded",
            "app_name": "City Bus Management System for Amravati",
            "database": db_status
        }), 200 if db_status.get("success") else 500

    # Static Frontend File Serving
    @app.route('/')
    def index():
        return send_from_directory(str(FRONTEND_DIR), 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        # Check if the requested file exists in frontend folder
        file_path = FRONTEND_DIR / path
        if file_path.exists() and file_path.is_file():
            return send_from_directory(str(FRONTEND_DIR), path)
        # If accessing without .html extension, attempt appending .html
        html_path = FRONTEND_DIR / f"{path}.html"
        if html_path.exists() and html_path.is_file():
            return send_from_directory(str(FRONTEND_DIR), f"{path}.html")
        return send_from_directory(str(FRONTEND_DIR), 'index.html')

    # Global Error Handlers
    @app.errorhandler(404)
    def not_found(e):
        return api_response(success=False, message="Resource not found.", status_code=404)

    @app.errorhandler(500)
    def internal_error(e):
        return api_response(success=False, message="Internal server error.", status_code=500)

    return app

app = create_app()

if __name__ == '__main__':
    logger.info("Initializing Amravati City Bus Management System...")
    logger.info(f"Frontend Directory: {FRONTEND_DIR}")
    
    # Check Database Connectivity
    db_check = test_connection()
    if db_check.get("success"):
        logger.info(f"Connected to MySQL database '{db_check.get('database')}' (Version: {db_check.get('version')}) via {db_check.get('connector')}")
        if Config.AUTO_CREATE_DEMO_ACCOUNTS:
            ensure_demo_accounts()
    else:
        logger.warning(
            f"MySQL is not currently reachable: {db_check.get('error')}.\n"
            "Please ensure MySQL Server 8 is running and credentials in backend/.env are configured.\n"
            "The Flask server will start so you can access the frontend and setup guides."
        )

    logger.info(f"Server starting on http://{Config.HOST}:{Config.PORT}")
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
