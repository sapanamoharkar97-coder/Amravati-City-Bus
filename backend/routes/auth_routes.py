import base64
import json
from flask import Blueprint, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_cursor
from utils.validators import validate_email, validate_username, validate_phone, validate_password_strength
from utils.decorators import api_response, login_required

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api/auth')

def _verify_password(stored_hash, password):
    """
    Verifies user password with Werkzeug check_password_hash.
    Supports development fallback if plain password matches.
    """
    try:
        if check_password_hash(stored_hash, password):
            return True
    except Exception:
        pass
    return stored_hash == password

def _generate_token(user_id, role):
    payload = json.dumps({"user_id": user_id, "role": role})
    return base64.b64encode(payload.encode('utf-8')).decode('utf-8')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    phone = data.get('phone', '').strip()
    gender = data.get('gender', 'other')
    age = data.get('age', 22)
    address = data.get('address', '').strip()

    if not validate_username(username):
        return api_response(success=False, message="Username must be 3-50 alphanumeric characters.", status_code=400)
    if not validate_email(email):
        return api_response(success=False, message="Valid email address is required.", status_code=400)
    if not validate_phone(phone):
        return api_response(success=False, message="Valid 10-digit mobile number is required.", status_code=400)
    if not full_name:
        return api_response(success=False, message="Full name is required.", status_code=400)

    is_valid_pw, pw_err = validate_password_strength(password)
    if not is_valid_pw:
        return api_response(success=False, message=pw_err, status_code=400)

    try:
        with get_db_cursor(commit=True) as (conn, cursor):
            # Check unique constraints
            cursor.execute("SELECT user_id FROM users WHERE username = %s OR email = %s;", (username, email))
            existing = cursor.fetchone()
            if existing:
                return api_response(success=False, message="Username or Email already registered.", status_code=409)

            pw_hash = generate_password_hash(password)
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, full_name, phone, is_active)
                VALUES (%s, %s, %s, 'passenger', %s, %s, TRUE);
            """, (username, email, pw_hash, full_name, phone))
            user_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO passengers (user_id, gender, age, address, city, emergency_contact)
                VALUES (%s, %s, %s, %s, 'Amravati', %s);
            """, (user_id, gender, age, address, phone))

            token = _generate_token(user_id, 'passenger')
            session['user_id'] = user_id
            session['role'] = 'passenger'
            session['username'] = username

            return api_response(
                data={
                    "user_id": user_id,
                    "username": username,
                    "email": email,
                    "role": "passenger",
                    "full_name": full_name,
                    "token": token
                },
                message="Registration successful. Welcome to Amravati City Bus!",
                status_code=201
            )
    except Exception as e:
        return api_response(success=False, message=f"Registration failed: {str(e)}", status_code=500)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    identifier = data.get('username', '').strip()  # Can be username or email
    password = data.get('password', '')

    if not identifier or not password:
        return api_response(success=False, message="Username/Email and password are required.", status_code=400)

    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            cursor.execute("""
                SELECT user_id, username, email, password_hash, role, full_name, phone, is_active
                FROM users
                WHERE (username = %s OR email = %s);
            """, (identifier, identifier))
            user = cursor.fetchone()

            if not user:
                return api_response(success=False, message="Invalid username/email or password.", status_code=401)

            is_active = user.get('is_active') if isinstance(user, dict) else user[7]
            if not is_active:
                return api_response(success=False, message="This account has been deactivated.", status_code=403)

            pw_hash = user.get('password_hash') if isinstance(user, dict) else user[3]
            if not _verify_password(pw_hash, password):
                return api_response(success=False, message="Invalid username/email or password.", status_code=401)

            user_id = user.get('user_id') if isinstance(user, dict) else user[0]
            role = user.get('role') if isinstance(user, dict) else user[4]
            username = user.get('username') if isinstance(user, dict) else user[1]
            full_name = user.get('full_name') if isinstance(user, dict) else user[5]
            email = user.get('email') if isinstance(user, dict) else user[2]

            session['user_id'] = user_id
            session['role'] = role
            session['username'] = username

            token = _generate_token(user_id, role)

            return api_response(
                data={
                    "user_id": user_id,
                    "username": username,
                    "email": email,
                    "role": role,
                    "full_name": full_name,
                    "token": token
                },
                message=f"Welcome back, {full_name}!",
                status_code=200
            )
    except Exception as e:
        return api_response(success=False, message=f"Login error: {str(e)}", status_code=500)

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return api_response(message="Logged out successfully.")

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    user = request.current_user
    user_id = user.get('user_id') if isinstance(user, dict) else user[0]
    
    # Fetch passenger profile if available
    profile = {}
    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            cursor.execute("SELECT gender, age, address, city, emergency_contact FROM passengers WHERE user_id = %s;", (user_id,))
            p_data = cursor.fetchone()
            if p_data:
                profile = p_data if isinstance(p_data, dict) else {
                    "gender": p_data[0], "age": p_data[1], "address": p_data[2],
                    "city": p_data[3], "emergency_contact": p_data[4]
                }
    except Exception:
        pass

    user_info = {
        "user_id": user.get('user_id'),
        "username": user.get('username'),
        "email": user.get('email'),
        "role": user.get('role'),
        "full_name": user.get('full_name'),
        "phone": user.get('phone'),
        "profile": profile
    }
    return api_response(data=user_info)

@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    user = request.current_user
    user_id = user.get('user_id')
    data = request.get_json() or {}

    full_name = data.get('full_name', user.get('full_name')).strip()
    phone = data.get('phone', user.get('phone')).strip()
    address = data.get('address', '')
    age = data.get('age')
    gender = data.get('gender')
    emergency_contact = data.get('emergency_contact', '')

    try:
        with get_db_cursor(commit=True) as (conn, cursor):
            cursor.execute("UPDATE users SET full_name = %s, phone = %s WHERE user_id = %s;", (full_name, phone, user_id))
            cursor.execute("""
                INSERT INTO passengers (user_id, gender, age, address, city, emergency_contact)
                VALUES (%s, %s, %s, %s, 'Amravati', %s)
                ON DUPLICATE KEY UPDATE 
                    gender = VALUES(gender), age = VALUES(age), 
                    address = VALUES(address), emergency_contact = VALUES(emergency_contact);
            """, (user_id, gender, age, address, emergency_contact))

        return api_response(message="Profile updated successfully.")
    except Exception as e:
        return api_response(success=False, message=f"Failed to update profile: {str(e)}", status_code=500)
