from flask import Blueprint, request
from db import get_db_cursor
from utils.validators import validate_bus_registration
from utils.decorators import api_response, admin_required

bus_bp = Blueprint('bus_bp', __name__, url_prefix='/api/buses')

@bus_bp.route('', methods=['GET'])
def list_buses():
    """List buses with optional status and type filtering."""
    status_filter = request.args.get('status')
    bus_type = request.args.get('bus_type')
    search = request.args.get('search', '').strip()

    query = "SELECT bus_id, bus_number, registration_number, bus_type, capacity, status, created_at FROM buses WHERE 1=1"
    params = []

    if status_filter:
        query += " AND status = %s"
        params.append(status_filter)
    if bus_type:
        query += " AND bus_type = %s"
        params.append(bus_type)
    if search:
        query += " AND (bus_number LIKE %s OR registration_number LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY bus_id ASC;"

    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            cursor.execute(query, tuple(params))
            buses = cursor.fetchall() or []
            return api_response(data=buses)
    except Exception as e:
        return api_response(success=False, message=f"Failed to fetch buses: {str(e)}", status_code=500)

@bus_bp.route('/<int:bus_id>', methods=['GET'])
def get_bus(bus_id):
    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            cursor.execute("""
                SELECT bus_id, bus_number, registration_number, bus_type, capacity, status, created_at 
                FROM buses WHERE bus_id = %s;
            """, (bus_id,))
            bus = cursor.fetchone()
            if not bus:
                return api_response(success=False, message="Bus not found.", status_code=404)
            return api_response(data=bus)
    except Exception as e:
        return api_response(success=False, message=f"Failed to fetch bus: {str(e)}", status_code=500)

@bus_bp.route('', methods=['POST'])
@admin_required
def create_bus():
    data = request.get_json() or {}
    bus_number = data.get('bus_number', '').strip()
    registration_number = data.get('registration_number', '').strip().upper()
    bus_type = data.get('bus_type', 'Ordinary')
    capacity = int(data.get('capacity', 35))
    status = data.get('status', 'active')

    if not bus_number or not registration_number:
        return api_response(success=False, message="Bus number and registration number are required.", status_code=400)
    if capacity < 10 or capacity > 100:
        return api_response(success=False, message="Bus capacity must be between 10 and 100.", status_code=400)
    if bus_type not in ('Ordinary', 'CNG Express', 'Electric AC', 'Mini Bus'):
        return api_response(success=False, message="Invalid bus type.", status_code=400)
    if status not in ('active', 'maintenance', 'retired'):
        return api_response(success=False, message="Invalid status value.", status_code=400)

    try:
        with get_db_cursor(commit=True) as (conn, cursor):
            cursor.execute("SELECT bus_id FROM buses WHERE bus_number = %s OR registration_number = %s;", 
                           (bus_number, registration_number))
            if cursor.fetchone():
                return api_response(success=False, message="Bus number or registration number already exists.", status_code=409)

            cursor.execute("""
                INSERT INTO buses (bus_number, registration_number, bus_type, capacity, status)
                VALUES (%s, %s, %s, %s, %s);
            """, (bus_number, registration_number, bus_type, capacity, status))
            new_id = cursor.lastrowid

            return api_response(data={"bus_id": new_id}, message="Bus created successfully.", status_code=201)
    except Exception as e:
        return api_response(success=False, message=f"Failed to create bus: {str(e)}", status_code=500)

@bus_bp.route('/<int:bus_id>', methods=['PUT'])
@admin_required
def update_bus(bus_id):
    data = request.get_json() or {}
    bus_number = data.get('bus_number', '').strip()
    registration_number = data.get('registration_number', '').strip().upper()
    bus_type = data.get('bus_type')
    capacity = int(data.get('capacity', 35))
    status = data.get('status')

    try:
        with get_db_cursor(commit=True) as (conn, cursor):
            cursor.execute("SELECT bus_id FROM buses WHERE bus_id = %s;", (bus_id,))
            if not cursor.fetchone():
                return api_response(success=False, message="Bus not found.", status_code=404)

            # Check unique constraint collision with other buses
            cursor.execute("""
                SELECT bus_id FROM buses 
                WHERE (bus_number = %s OR registration_number = %s) AND bus_id <> %s;
            """, (bus_number, registration_number, bus_id))
            if cursor.fetchone():
                return api_response(success=False, message="Another bus with this number or registration exists.", status_code=409)

            cursor.execute("""
                UPDATE buses 
                SET bus_number = %s, registration_number = %s, bus_type = %s, capacity = %s, status = %s
                WHERE bus_id = %s;
            """, (bus_number, registration_number, bus_type, capacity, status, bus_id))

            return api_response(message="Bus updated successfully.")
    except Exception as e:
        return api_response(success=False, message=f"Failed to update bus: {str(e)}", status_code=500)

@bus_bp.route('/<int:bus_id>', methods=['DELETE'])
@admin_required
def delete_bus(bus_id):
    try:
        with get_db_cursor(commit=True) as (conn, cursor):
            cursor.execute("SELECT bus_id, bus_number FROM buses WHERE bus_id = %s;", (bus_id,))
            bus = cursor.fetchone()
            if not bus:
                return api_response(success=False, message="Bus not found.", status_code=404)

            # Check if assigned to any schedules
            cursor.execute("SELECT COUNT(*) AS cnt FROM schedules WHERE bus_id = %s;", (bus_id,))
            sched_count = cursor.fetchone().get('cnt', 0)
            if sched_count > 0:
                return api_response(
                    success=False, 
                    message=f"Cannot delete bus: It is assigned to {sched_count} schedule(s). Set status to 'retired' instead.",
                    status_code=400
                )

            cursor.execute("DELETE FROM buses WHERE bus_id = %s;", (bus_id,))
            return api_response(message=f"Bus #{bus_id} deleted successfully.")
    except Exception as e:
        return api_response(success=False, message=f"Failed to delete bus: {str(e)}", status_code=500)
