import re
from datetime import datetime

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
PHONE_REGEX = re.compile(r'^[6-9]\d{9}$')  # Standard 10-digit Indian Mobile Number
REGISTRATION_REGEX = re.compile(r'^[A-Z]{2}[-\s]?\d{2}[-\s]?[A-Z]{1,2}[-\s]?\d{4}$', re.IGNORECASE)

def validate_email(email: str) -> bool:
    """Validates email format."""
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))

def validate_phone(phone: str) -> bool:
    """Validates 10-digit mobile phone number."""
    if not phone or not isinstance(phone, str):
        return False
    cleaned = re.sub(r'[\s\-\+]', '', phone.strip())
    if cleaned.startswith('91') and len(cleaned) == 12:
        cleaned = cleaned[2:]
    return bool(PHONE_REGEX.match(cleaned))

def validate_username(username: str) -> bool:
    """Validates username length and allowed characters (alphanumeric, underscore)."""
    if not username or not isinstance(username, str):
        return False
    username = username.strip()
    return 3 <= len(username) <= 50 and re.match(r'^[a-zA-Z0-9_]+$', username) is not None

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Ensures password meets minimum security standards."""
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""

def validate_bus_registration(reg_no: str) -> bool:
    """Validates Indian vehicle registration format (e.g. MH-27-X-1001)."""
    if not reg_no or not isinstance(reg_no, str):
        return False
    return len(reg_no.strip()) >= 5

def validate_date(date_str: str) -> bool:
    """Validates YYYY-MM-DD date string."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except (ValueError, TypeError):
        return False

def validate_time(time_str: str) -> bool:
    """Validates HH:MM or HH:MM:SS time string."""
    for fmt in ('%H:%M:%S', '%H:%M'):
        try:
            datetime.strptime(time_str, fmt)
            return True
        except (ValueError, TypeError):
            pass
    return False
