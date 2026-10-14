from flask import Blueprint, request
from db import get_db_cursor
from utils.decorators import api_response, admin_required

route_bp = Blueprint('route_bp', __name__, url_prefix='/api/routes')

@route_bp.route('', methods=['GET'])
def list_routes():
    search = request.args.get('search', '').strip()
    query = """
        SELECT 
            r.route_id, r.route_number, r.route_name, r.start_stop_id, r.end_stop_id,
            r.total_distance_km, r.estimated_duration_mins, r.base_fare, r.is_active,
            s_start.stop_name AS start_stop_name,
            s_end.stop_name AS end_stop_name,
            (SELECT COUNT(*) FROM route_stops rs WHERE rs.route_id = r.route_id) AS total_halts
        FROM bus_routes r
        INNER JOIN bus_stops s_start ON r.start_stop_id = s_start.stop_id
        INNER JOIN bus_stops s_end ON r.end_stop_id = s_end.stop_id
        WHERE 1=1
    """
    params = []
    if search:
        query += " AND (r.route_number LIKE %s OR r.route_name LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY r.route_id ASC;"

    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            cursor.execute(query, tuple(params))
            routes = cursor.fetchall() or []
            return api_response(data=routes)
    except Exception as e:
        return api_response(success=False, message=f"Failed to fetch routes: {str(e)}", status_code=500)

@route_bp.route('/<int:route_id>', methods=['GET'])
def get_route(route_id):
    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            cursor.execute("""
                SELECT 
                    r.route_id, r.route_number, r.route_name, r.start_stop_id, r.end_stop_id,
                    r.total_distance_km, r.estimated_duration_mins, r.base_fare, r.is_active,
                    s_start.stop_name AS start_stop_name,
                    s_end.stop_name AS end_stop_name
                FROM bus_routes r
                INNER JOIN bus_stops s_start ON r.start_stop_id = s_start.stop_id
                INNER JOIN bus_stops s_end ON r.end_stop_id = s_end.stop_id
                WHERE r.route_id = %s;
            """, (route_id,))
            route = cursor.fetchone()
            if not route:
                return api_response(success=False, message="Route not found.", status_code=404)

            # Fetch ordered intermediate halts
            cursor.execute("""
                SELECT 
                    rs.route_stop_id, rs.stop_id, s.stop_name, s.landmark,
                    rs.stop_sequence, rs.distance_from_source_km, 
                    rs.fare_from_source, rs.halt_duration_mins
                FROM route_stops rs
                INNER JOIN bus_stops s ON rs.stop_id = s.stop_id
                WHERE rs.route_id = %s
                ORDER BY rs.stop_sequence ASC;
            """, (route_id,))
            halts = cursor.fetchall() or []
            route['halts'] = halts

            return api_response(data=route)
    except Exception as e:
        return api_response(success=False, message=f"Failed to fetch route: {str(e)}", status_code=500)

@route_bp.route('', methods=['POST'])
@admin_required
def create_route():
    data = request.get_json() or {}
    route_number = data.get('route_number', '').strip().upper()
    route_name = data.get('route_name', '').strip()
    start_stop_id = int(data.get('start_stop_id', 0))
    end_stop_id = int(data.get('end_stop_id', 0))
    total_distance_km = float(data.get('total_distance_km', 10.0))
    estimated_duration_mins = int(data.get('estimated_duration_mins', 30))
    base_fare = float(data.get('base_fare', 10.0))
    halts = data.get('halts', [])  # List of {stop_id, sequence, distance, fare, halt_mins}

    if not route_number or not route_name:
        return api_response(success=False, message="Route number and name are required.", status_code=400)
    if start_stop_id <= 0 or end_stop_id <= 0 or start_stop_id == end_stop_id:
        return api_response(success=False, message="Distinct start and end stops are required.", status_code=400)

    try:
        with get_db_cursor(commit=True) as (conn, cursor):
            cursor.execute("SELECT route_id FROM bus_routes WHERE route_number = %s;", (route_number,))
            if cursor.fetchone():
                return api_response(success=False, message="Route number already exists.", status_code=409)

            cursor.execute("""
                INSERT INTO bus_routes (
                    route_number, route_name, start_stop_id, end_stop_id, 
                    total_distance_km, estimated_duration_mins, base_fare, is_active
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE);
            """, (route_number, route_name, start_stop_id, end_stop_id, total_distance_km, estimated_duration_mins, base_fare))
            route_id = cursor.lastrowid

            # If halts provided, insert them into route_stops
            if halts and isinstance(halts, list):
                for h in halts:
                    cursor.execute("""
                        INSERT INTO route_stops (route_id, stop_id, stop_sequence, distance_from_source_km, fare_from_source, halt_duration_mins)
                        VALUES (%s, %s, %s, %s, %s, %s);
                    """, (
                        route_id, int(h['stop_id']), int(h['stop_sequence']),
                        float(h.get('distance_from_source_km', 0.0)),
                        float(h.get('fare_from_source', 0.0)),
                        int(h.get('halt_duration_mins', 2))
                    ))
            else:
                # Default endpoints as sequence 1 and 2
                cursor.execute("""
                    INSERT INTO route_stops (route_id, stop_id, stop_sequence, distance_from_source_km, fare_from_source, halt_duration_mins)
                    VALUES 
                    (%s, %s, 1, 0.0, 0.0, 0),
                    (%s, %s, 2, %s, %s, 5);
                """, (route_id, start_stop_id, route_id, end_stop_id, total_distance_km, base_fare))

            return api_response(data={"route_id": route_id}, message="Route created successfully.", status_code=201)
    except Exception as e:
        return api_response(success=False, message=f"Failed to create route: {str(e)}", status_code=500)

@route_bp.route('/<int:route_id>', methods=['PUT'])
@admin_required
def update_route(route_id):
    data = request.get_json() or {}
    route_number = data.get('route_number', '').strip().upper()
    route_name = data.get('route_name', '').strip()
    start_stop_id = int(data.get('start_stop_id', 0))
    end_stop_id = int(data.get('end_stop_id', 0))
    total_distance_km = float(data.get('total_distance_km', 10.0))
    estimated_duration_mins = int(data.get('estimated_duration_mins', 30))
    base_fare = float(data.get('base_fare', 10.0))
    is_active = bool(data.get('is_active', True))
    halts = data.get('halts')

    try:
        with get_db_cursor(commit=True) as (conn, cursor):
            cursor.execute("SELECT route_id FROM bus_routes WHERE route_id = %s;", (route_id,))
            if not cursor.fetchone():
                return api_response(success=False, message="Route not found.", status_code=404)

            cursor.execute("SELECT route_id FROM bus_routes WHERE route_number = %s AND route_id <> %s;", (route_number, route_id))
            if cursor.fetchone():
                return api_response(success=False, message="Another route with this number exists.", status_code=409)

            cursor.execute("""
                UPDATE bus_routes 
                SET route_number = %s, route_name = %s, start_stop_id = %s, end_stop_id = %s,
                    total_distance_km = %s, estimated_duration_mins = %s, base_fare = %s, is_active = %s
                WHERE route_id = %s;
            """, (route_number, route_name, start_stop_id, end_stop_id, total_distance_km, estimated_duration_mins, base_fare, is_active, route_id))

            if halts is not None and isinstance(halts, list):
                cursor.execute("DELETE FROM route_stops WHERE route_id = %s;", (route_id,))
                for h in halts:
                    cursor.execute("""
                        INSERT INTO route_stops (route_id, stop_id, stop_sequence, distance_from_source_km, fare_from_source, halt_duration_mins)
                        VALUES (%s, %s, %s, %s, %s, %s);
                    """, (
                        route_id, int(h['stop_id']), int(h['stop_sequence']),
                        float(h.get('distance_from_source_km', 0.0)),
                        float(h.get('fare_from_source', 0.0)),
                        int(h.get('halt_duration_mins', 2))
                    ))

            return api_response(message="Route updated successfully.")
    except Exception as e:
        return api_response(success=False, message=f"Failed to update route: {str(e)}", status_code=500)

@route_bp.route('/<int:route_id>', methods=['DELETE'])
@admin_required
def delete_route(route_id):
    try:
        with get_db_cursor(commit=True) as (conn, cursor):
            cursor.execute("SELECT COUNT(*) AS cnt FROM schedules WHERE route_id = %s;", (route_id,))
            sched_cnt = cursor.fetchone().get('cnt', 0)
            if sched_cnt > 0:
                return api_response(
                    success=False,
                    message=f"Cannot delete route: It is referenced by {sched_cnt} schedules. Mark as inactive instead.",
                    status_code=400
                )

            cursor.execute("DELETE FROM bus_routes WHERE route_id = %s;", (route_id,))
            return api_response(message=f"Route #{route_id} deleted successfully.")
    except Exception as e:
        return api_response(success=False, message=f"Failed to delete route: {str(e)}", status_code=500)
