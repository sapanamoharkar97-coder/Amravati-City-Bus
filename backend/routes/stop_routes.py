from flask import Blueprint, request
from db import get_db_cursor
from utils.decorators import api_response, admin_required

stop_bp = Blueprint('stop_bp', __name__, url_prefix='/api/stops')

@stop_bp.route('', methods=['GET'])
def list_stops():
    search = request.args.get('search', '').strip()
    query = "SELECT stop_id, stop_name, landmark, latitude, longitude, city, is_active FROM bus_stops WHERE 1=1"
    params = []

    if search:
        query += " AND (stop_name LIKE %s OR landmark LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY stop_name ASC;"

    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            cursor.execute(query, tuple(params))
            stops = cursor.fetchall() or []
            return api_response(data=stops)
    except Exception as e:
        return api_response(success=False, message=f"Failed to fetch stops: {str(e)}", status_code=500)

@stop_bp.route('/<int:stop_id>', methods=['GET'])
def get_stop(stop_id):
    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            cursor.execute("""
                SELECT stop_id, stop_name, landmark, latitude, longitude, city, is_active 
                FROM bus_stops WHERE stop_id = %s;
            """, (stop_id,))
            stop = cursor.fetchone()
            if not stop:
                return api_response(success=False, message="Bus stop not found.", status_code=404)
            return api_response(data=stop)
    except Exception as e:
        return api_response(success=False, message=f"Failed to fetch stop: {str(e)}", status_code=500)

@stop_bp.route('', methods=['POST'])
@admin_required
def create_stop():
    data = request.get_json() or {}
    stop_name = data.get('stop_name', '').strip()
    landmark = data.get('landmark', '').strip()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    city = data.get('city', 'Amravati').strip()

    if not stop_name:
        return api_response(success=False, message="Stop name is required.", status_code=400)

    try:
        with get_db_cursor(commit=True) as (conn, cursor):
            cursor.execute("SELECT stop_id FROM bus_stops WHERE stop_name = %s;", (stop_name,))
            if cursor.fetchone():
                return api_response(success=False, message="A stop with this name already exists.", status_code=409)

            cursor.execute("""
                INSERT INTO bus_stops (stop_name, landmark, latitude, longitude, city, is_active)
                VALUES (%s, %s, %s, %s, %s, TRUE);
            """, (stop_name, landmark, latitude, longitude, city))
            new_id = cursor.lastrowid
            return api_response(data={"stop_id": new_id}, message="Bus stop created successfully.", status_code=201)
    except Exception as e:
        return api_response(success=False, message=f"Failed to create stop: {str(e)}", status_code=500)

@stop_bp.route('/<int:stop_id>', methods=['PUT'])
@admin_required
def update_stop(stop_id):
    data = request.get_json() or {}
    stop_name = data.get('stop_name', '').strip()
    landmark = data.get('landmark', '').strip()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    city = data.get('city', 'Amravati').strip()
    is_active = bool(data.get('is_active', True))

    try:
        with get_db_cursor(commit=True) as (conn, cursor):
            cursor.execute("SELECT stop_id FROM bus_stops WHERE stop_name = %s AND stop_id <> %s;", (stop_name, stop_id))
            if cursor.fetchone():
                return api_response(success=False, message="Another stop with this name exists.", status_code=409)

            cursor.execute("""
                UPDATE bus_stops
                SET stop_name = %s, landmark = %s, latitude = %s, longitude = %s, city = %s, is_active = %s
                WHERE stop_id = %s;
            """, (stop_name, landmark, latitude, longitude, city, is_active, stop_id))
            return api_response(message="Stop updated successfully.")
    except Exception as e:
        return api_response(success=False, message=f"Failed to update stop: {str(e)}", status_code=500)

@stop_bp.route('/<int:stop_id>', methods=['DELETE'])
@admin_required
def delete_stop(stop_id):
    try:
        with get_db_cursor(commit=True) as (conn, cursor):
            # Check if referenced in routes or bookings
            cursor.execute("SELECT COUNT(*) AS cnt FROM route_stops WHERE stop_id = %s;", (stop_id,))
            route_refs = cursor.fetchone().get('cnt', 0)
            if route_refs > 0:
                return api_response(
                    success=False, 
                    message=f"Cannot delete stop: It is used in {route_refs} route stop sequences.", 
                    status_code=400
                )

            cursor.execute("DELETE FROM bus_stops WHERE stop_id = %s;", (stop_id,))
            return api_response(message=f"Stop #{stop_id} deleted successfully.")
    except Exception as e:
        return api_response(success=False, message=f"Failed to delete stop: {str(e)}", status_code=500)
