from flask import Blueprint, request
from db import get_db_cursor
from utils.validators import validate_phone
from utils.decorators import api_response, admin_required

staff_bp = Blueprint('staff_bp', __name__, url_prefix='/api/staff')

# ------------------------------------------------------------------------------
# DRIVER ENDPOINTS
# ------------------------------------------------------------------------------
@staff_bp.route('/drivers', methods=['GET'])
def list_drivers():
    status = request.args.get('status')
    query = "SELECT driver_id, license_number, full_name, phone, experience_years, status, created_at FROM drivers WHERE 1=1"
    params = []
    if status:
        query += " AND status = %s"
        params.append(status)
    query += " ORDER BY driver_id ASC;"

    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            cursor.execute(query, tuple(params))
            drivers = cursor.fetchall() or []
            return api_response(data=drivers)
    except Exception as e:
        return api_response(success=False, message=f"Failed to fetch drivers: {str(e)}", status_code=500)

@staff_bp.route('/drivers', methods=['POST'])
@admin_required
def create_driver():
    data = request.get_json() or {}
    license_number = data.get('license_number', '').strip().upper()
    full_name = data.get('full_name', '').strip()
    phone = data.get('phone', '').strip()
    experience_years = int(data.get('experience_years', 1))
    status = data.get('status', 'active')

    if not license_number or not full_name:
        return api_response(success=False, message="License number and full name are required.", status_code=400)
    if not validate_phone(phone):
        return api_response(success=False, message="Valid 10-digit phone number is required.", status_code=400)

    try:
        with get_db_cursor(commit=True) as (conn, cursor):
            cursor.execute("SELECT driver_id FROM drivers WHERE license_number = %s;", (license_number,))
            if cursor.fetchone():
                return api_response(success=False, message="Driver license number already registered.", status_code=409)

            cursor.execute("""
                INSERT INTO drivers (license_number, full_name, phone, experience_years, status)
                VALUES (%s, %s, %s, %s, %s);
            """, (license_number, full_name, phone, experience_years, status))
            new_id = cursor.lastrowid
            return api_response(data={"driver_id": new_id}, message="Driver created successfully.", status_code=201)
    except Exception as e:
        return api_response(success=False, message=f"Failed to create driver: {str(e)}", status_code=500)

@staff_bp.route('/drivers/<int:driver_id>', methods=['PUT'])
@admin_required
def update_driver(driver_id):
    data = request.get_json() or {}
    license_number = data.get('license_number', '').strip().upper()
    full_name = data.get('full_name', '').strip()
    phone = data.get('phone', '').strip()
    experience_years = int(data.get('experience_years', 1))
    status = data.get('status', 'active')

    try:
        with get_db_cursor(commit=True) as (conn, cursor):
            cursor.execute("SELECT driver_id FROM drivers WHERE license_number = %s AND driver_id <> %s;", (license_number, driver_id))
            if cursor.fetchone():
                return api_response(success=False, message="License number already belongs to another driver.", status_code=409)

            cursor.execute("""
                UPDATE drivers 
                SET license_number = %s, full_name = %s, phone = %s, experience_years = %s, status = %s
                WHERE driver_id = %s;
            """, (license_number, full_name, phone, experience_years, status, driver_id))
            return api_response(message="Driver updated successfully.")
    except Exception as e:
        return api_response(success=False, message=f"Failed to update driver: {str(e)}", status_code=500)

@staff_bp.route('/drivers/<int:driver_id>', methods=['DELETE'])
@admin_required
def delete_driver(driver_id):
    try:
        with get_db_cursor(commit=True) as (conn, cursor):
            cursor.execute("SELECT COUNT(*) AS cnt FROM staff_assignments WHERE driver_id = %s;", (driver_id,))
            assign_cnt = cursor.fetchone().get('cnt', 0)
            if assign_cnt > 0:
                return api_response(
                    success=False, 
                    message=f"Cannot delete driver: Active in {assign_cnt} schedule assignments. Set status to inactive instead.",
                    status_code=400
                )

            cursor.execute("DELETE FROM drivers WHERE driver_id = %s;", (driver_id,))
            return api_response(message=f"Driver #{driver_id} deleted successfully.")
    except Exception as e:
        return api_response(success=False, message=f"Failed to delete driver: {str(e)}", status_code=500)

# ------------------------------------------------------------------------------
# CONDUCTOR ENDPOINTS
# ------------------------------------------------------------------------------
@staff_bp.route('/conductors', methods=['GET'])
def list_conductors():
    status = request.args.get('status')
    query = "SELECT conductor_id, badge_number, full_name, phone, status, created_at FROM conductors WHERE 1=1"
    params = []
    if status:
        query += " AND status = %s"
        params.append(status)
    query += " ORDER BY conductor_id ASC;"

    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            cursor.execute(query, tuple(params))
            conductors = cursor.fetchall() or []
            return api_response(data=conductors)
    except Exception as e:
        return api_response(success=False, message=f"Failed to fetch conductors: {str(e)}", status_code=500)

@staff_bp.route('/conductors', methods=['POST'])
@admin_required
def create_conductor():
    data = request.get_json() or {}
    badge_number = data.get('badge_number', '').strip().upper()
    full_name = data.get('full_name', '').strip()
    phone = data.get('phone', '').strip()
    status = data.get('status', 'active')

    if not badge_number or not full_name:
        return api_response(success=False, message="Badge number and full name are required.", status_code=400)
    if not validate_phone(phone):
        return api_response(success=False, message="Valid 10-digit phone number is required.", status_code=400)

    try:
        with get_db_cursor(commit=True) as (conn, cursor):
            cursor.execute("SELECT conductor_id FROM conductors WHERE badge_number = %s;", (badge_number,))
            if cursor.fetchone():
                return api_response(success=False, message="Conductor badge number already registered.", status_code=409)

            cursor.execute("""
                INSERT INTO conductors (badge_number, full_name, phone, status)
                VALUES (%s, %s, %s, %s);
            """, (badge_number, full_name, phone, status))
            new_id = cursor.lastrowid
            return api_response(data={"conductor_id": new_id}, message="Conductor created successfully.", status_code=201)
    except Exception as e:
        return api_response(success=False, message=f"Failed to create conductor: {str(e)}", status_code=500)

@staff_bp.route('/conductors/<int:conductor_id>', methods=['PUT'])
@admin_required
def update_conductor(conductor_id):
    data = request.get_json() or {}
    badge_number = data.get('badge_number', '').strip().upper()
    full_name = data.get('full_name', '').strip()
    phone = data.get('phone', '').strip()
    status = data.get('status', 'active')

    try:
        with get_db_cursor(commit=True) as (conn, cursor):
            cursor.execute("SELECT conductor_id FROM conductors WHERE badge_number = %s AND conductor_id <> %s;", (badge_number, conductor_id))
            if cursor.fetchone():
                return api_response(success=False, message="Badge number already in use by another conductor.", status_code=409)

            cursor.execute("""
                UPDATE conductors 
                SET badge_number = %s, full_name = %s, phone = %s, status = %s
                WHERE conductor_id = %s;
            """, (badge_number, full_name, phone, status, conductor_id))
            return api_response(message="Conductor updated successfully.")
    except Exception as e:
        return api_response(success=False, message=f"Failed to update conductor: {str(e)}", status_code=500)

@staff_bp.route('/conductors/<int:conductor_id>', methods=['DELETE'])
@admin_required
def delete_conductor(conductor_id):
    try:
        with get_db_cursor(commit=True) as (conn, cursor):
            cursor.execute("SELECT COUNT(*) AS cnt FROM staff_assignments WHERE conductor_id = %s;", (conductor_id,))
            assign_cnt = cursor.fetchone().get('cnt', 0)
            if assign_cnt > 0:
                return api_response(
                    success=False, 
                    message=f"Cannot delete conductor: Active in {assign_cnt} schedule assignments. Set status to inactive instead.",
                    status_code=400
                )

            cursor.execute("DELETE FROM conductors WHERE conductor_id = %s;", (conductor_id,))
            return api_response(message=f"Conductor #{conductor_id} deleted successfully.")
    except Exception as e:
        return api_response(success=False, message=f"Failed to delete conductor: {str(e)}", status_code=500)

# ------------------------------------------------------------------------------
# STAFF ASSIGNMENTS
# ------------------------------------------------------------------------------
@staff_bp.route('/assignments', methods=['GET'])
@admin_required
def list_assignments():
    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            cursor.execute("""
                SELECT 
                    sa.assignment_id, sa.schedule_id, sa.driver_id, sa.conductor_id,
                    sa.assigned_date, sa.status,
                    d.full_name AS driver_name, d.phone AS driver_phone,
                    c.full_name AS conductor_name, c.badge_number AS conductor_badge,
                    s.departure_time, s.arrival_time, s.journey_date,
                    r.route_number, r.route_name,
                    b.bus_number
                FROM staff_assignments sa
                INNER JOIN schedules s ON sa.schedule_id = s.schedule_id
                INNER JOIN bus_routes r ON s.route_id = r.route_id
                INNER JOIN buses b ON s.bus_id = b.bus_id
                INNER JOIN drivers d ON sa.driver_id = d.driver_id
                INNER JOIN conductors c ON sa.conductor_id = c.conductor_id
                ORDER BY sa.assigned_date DESC, s.departure_time ASC;
            """)
            assignments = cursor.fetchall() or []
            return api_response(data=assignments)
    except Exception as e:
        return api_response(success=False, message=f"Failed to fetch staff assignments: {str(e)}", status_code=500)

@staff_bp.route('/assignments', methods=['POST'])
@admin_required
def assign_staff():
    data = request.get_json() or {}
    schedule_id = int(data.get('schedule_id', 0))
    driver_id = int(data.get('driver_id', 0))
    conductor_id = int(data.get('conductor_id', 0))

    if schedule_id <= 0 or driver_id <= 0 or conductor_id <= 0:
        return api_response(success=False, message="Schedule, Driver, and Conductor are required.", status_code=400)

    try:
        with get_db_cursor(commit=True) as (conn, cursor):
            cursor.execute("SELECT journey_date FROM schedules WHERE schedule_id = %s;", (schedule_id,))
            sched = cursor.fetchone()
            if not sched:
                return api_response(success=False, message="Schedule not found.", status_code=404)
            journey_date = sched.get('journey_date') if isinstance(sched, dict) else sched[0]

            cursor.execute("""
                INSERT INTO staff_assignments (schedule_id, driver_id, conductor_id, assigned_date, status)
                VALUES (%s, %s, %s, %s, 'assigned')
                ON DUPLICATE KEY UPDATE 
                    driver_id = VALUES(driver_id), 
                    conductor_id = VALUES(conductor_id),
                    assigned_date = VALUES(assigned_date),
                    status = 'assigned';
            """, (schedule_id, driver_id, conductor_id, journey_date))

            return api_response(message="Staff assigned to schedule successfully.")
    except Exception as e:
        return api_response(success=False, message=f"Failed to assign staff: {str(e)}", status_code=500)
