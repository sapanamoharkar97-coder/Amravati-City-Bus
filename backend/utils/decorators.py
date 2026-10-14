import functools
import base64
import json
from flask import request, session, jsonify
from db import get_db_cursor

def api_response(data=None, message="Success", status_code=200, success=True, errors=None):
    """Generates standardized JSON response payload."""
    payload = {
        "success": success,
        "message": message,
        "data": data,
        "errors": errors
    }
    return jsonify(payload), status_code

def _resolve_authenticated_user():
    """
    Resolves the authenticated user from active session or Authorization header.
    Supports cookie sessions as well as Bearer token headers for API clients.
    """
    user_id = session.get('user_id')
    role = session.get('role')
    
    # Check Authorization header if session is not present
    if not user_id:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1].strip()
            # Demo Bearer token format: base64 encoded '{"user_id": 1, "role": "admin"}'
            try:
                decoded = base64.b64decode(token.encode('utf-8')).decode('utf-8')
                token_data = json.loads(decoded)
                user_id = token_data.get('user_id')
                role = token_data.get('role')
            except Exception:
                # Direct user ID format fallback for simplified testing
                if token.isdigit():
                    user_id = int(token)
    
    if not user_id:
        return None

    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            cursor.execute("""
                SELECT user_id, username, email, role, full_name, phone, is_active 
                FROM users 
                WHERE user_id = %s AND is_active = TRUE;
            """, (user_id,))
            user = cursor.fetchone()
            return user
    except Exception:
        return None

def login_required(f):
    """Decorator ensuring request originates from an authenticated user."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        user = _resolve_authenticated_user()
        if not user:
            return api_response(
                success=False,
                message="Authentication required. Please log in.",
                status_code=401
            )
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator ensuring request originates from an authorized administrator."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        user = _resolve_authenticated_user()
        if not user:
            return api_response(
                success=False,
                message="Authentication required. Please log in as an administrator.",
                status_code=401
            )
        if user.get('role') != 'admin':
            return api_response(
                success=False,
                message="Access denied. Administrator privileges required.",
                status_code=403
            )
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function
