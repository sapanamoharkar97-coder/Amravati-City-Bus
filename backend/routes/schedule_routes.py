from flask import Blueprint, request
from db import get_db_cursor
from utils.validators import validate_date, validate_time
from utils.decorators import api_response, admin_required

schedule_bp = Blueprint('schedule_bp', __name__, url_prefix='/api/schedules')

@schedule_bp.route('', methods=['GET'])
def list_schedules():
    journey_date = request.args.get('date')
    route_id = request.args.get('route_id')
    status = request.args.get('status')

    query = """
        SELECT 
            s.schedule_id, s.journey_date, s.departure_time, s.arrival_time, 
            s.fare, s.frequency, s.status,
            r.route_id, r.route_number, r.route_name,
            b.bus_id, b.bus_number, b.bus_type, b.capacity,
            d.full_name AS driver_name,
            c.full_name AS conductor_name,
            (SELECT COUNT(*) FROM booking_seats bs WHERE bs.schedule_id = s.schedule_id AND bs.status = 'booked') AS booked_seats,
            (b.capacity - (SELECT COUNT(*) FROM booking_seats bs WHERE bs.schedule_id = s.schedule_id AND bs.status = 'booked')) AS available_seats
        FROM schedules s
        INNER JOIN bus_routes r ON s.route_id = r.route_id
        INNER JOIN buses b ON s.bus_id = b.bus_id
        LEFT JOIN staff_assignments sa ON s.schedule_id = sa.schedule_id
        LEFT JOIN drivers d ON sa.driver_id = d.driver_id
        LEFT JOIN conductors c ON sa.conductor_id = c.conductor_id
        WHERE 1=1
    """
    params = []
    if journey_date:
        query += " AND s.journey_date = %s"
        params.append(journey_date)
    if route_id:
        query += " AND s.route_id = %s"
        params.append(route_id)
    if status:
        query += " AND s.status = %s"
        params.append(status)

    query += " ORDER BY s.journey_date DESC, s.departure_time ASC;"

    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            cursor.execute(query, tuple(params))
            schedules = cursor.fetchall() or []
            return api_response(data=schedules)
    except Exception as e:
        return api_response(success=False, message=f"Failed to fetch schedules: {str(e)}", status_code=500)

@schedule_bp.route('/search', methods=['GET'])
def search_schedules():
    """
    Passenger Schedule Search between source and destination stops for a given date.
    Calculates stage fare, halts, and available seats.
    """
    source_stop_id = request.args.get('source_stop_id', type=int)
    dest_stop_id = request.args.get('dest_stop_id', type=int)
    travel_date = request.args.get('date', '').strip()

    if not source_stop_id or not dest_stop_id:
        return api_response(success=False, message="Source and destination stop IDs are required.", status_code=400)
    if source_stop_id == dest_stop_id:
        return api_response(success=False, message="Boarding stop and destination stop cannot be the same.", status_code=400)

    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            # Query routes containing both stops in the proper sequence order
            query = """
                SELECT 
                    s.schedule_id, s.journey_date, s.departure_time, s.arrival_time, 
                    s.status AS schedule_status,
                    r.route_id, r.route_number, r.route_name, r.base_fare,
                    b.bus_id, b.bus_number, b.bus_type, b.capacity AS total_capacity,
                    st_src.stop_name AS source_stop_name,
                    st_dst.stop_name AS dest_stop_name,
                    rs_src.stop_sequence AS src_sequence,
                    rs_dst.stop_sequence AS dst_sequence,
                    rs_src.fare_from_source AS src_stage_fare,
                    rs_dst.fare_from_source AS dst_stage_fare,
                    rs_src.distance_from_source_km AS src_dist,
                    rs_dst.distance_from_source_km AS dst_dist,
                    (
                        SELECT COUNT(*) 
                        FROM booking_seats bs 
                        WHERE bs.schedule_id = s.schedule_id AND bs.status = 'booked'
                    ) AS booked_seats
                FROM schedules s
                INNER JOIN bus_routes r ON s.route_id = r.route_id
                INNER JOIN buses b ON s.bus_id = b.bus_id
                INNER JOIN route_stops rs_src ON r.route_id = rs_src.route_id AND rs_src.stop_id = %s
                INNER JOIN route_stops rs_dst ON r.route_id = rs_dst.route_id AND rs_dst.stop_id = %s
                INNER JOIN bus_stops st_src ON rs_src.stop_id = st_src.stop_id
                INNER JOIN bus_stops st_dst ON rs_dst.stop_id = st_dst.stop_id
                WHERE rs_src.stop_sequence < rs_dst.stop_sequence
                  AND s.status = 'scheduled'
                  AND b.status = 'active'
            """
            params = [source_stop_id, dest_stop_id]
            if travel_date:
                query += " AND s.journey_date = %s"
                params.append(travel_date)

            query += " ORDER BY s.journey_date ASC, s.departure_time ASC;"

            cursor.execute(query, tuple(params))
            results = cursor.fetchall() or []

            # Compute dynamic fares and remaining seats for each result
            schedules_list = []
            for row in results:
                src_fare = float(row.get('src_stage_fare', 0.0))
                dst_fare = float(row.get('dst_stage_fare', 0.0))
                base_fare = float(row.get('base_fare', 10.0))
                stage_fare = max(base_fare, abs(dst_fare - src_fare))
                
                capacity = int(row.get('total_capacity', 35))
                booked = int(row.get('booked_seats', 0))
                available = max(0, capacity - booked)

                distance = abs(float(row.get('dst_dist', 0.0)) - float(row.get('src_dist', 0.0)))

                schedules_list.append({
                    "schedule_id": row.get('schedule_id'),
                    "journey_date": str(row.get('journey_date')),
                    "departure_time": str(row.get('departure_time')),
                    "arrival_time": str(row.get('arrival_time')),
                    "route_id": row.get('route_id'),
                    "route_number": row.get('route_number'),
                    "route_name": row.get('route_name'),
                    "bus_id": row.get('bus_id'),
                    "bus_number": row.get('bus_number'),
                    "bus_type": row.get('bus_type'),
                    "total_capacity": capacity,
                    "booked_seats": booked,
                    "available_seats": available,
                    "fare": stage_fare,
                    "distance_km": distance,
                    "source_stop_name": row.get('source_stop_name'),
                    "dest_stop_name": row.get('dest_stop_name')
                })

            return api_response(data=schedules_list)
    except Exception as e:
        return api_response(success=False, message=f"Schedule search failed: {str(e)}", status_code=500)

@schedule_bp.route('/<int:schedule_id>', methods=['GET'])
def get_schedule(schedule_id):
    """Returns details and full seat map status for a schedule."""
    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            cursor.execute("""
                SELECT 
                    s.schedule_id, s.journey_date, s.departure_time, s.arrival_time, 
                    s.fare, s.frequency, s.status,
                    r.route_id, r.route_number, r.route_name,
                    b.bus_id, b.bus_number, b.bus_type, b.capacity,
                    st_start.stop_name AS start_stop_name,
                    st_end.stop_name AS end_stop_name,
                    d.full_name AS driver_name,
                    c.full_name AS conductor_name
                FROM schedules s
                INNER JOIN bus_routes r ON s.route_id = r.route_id
                INNER JOIN buses b ON s.bus_id = b.bus_id
                INNER JOIN bus_stops st_start ON r.start_stop_id = st_start.stop_id
                INNER JOIN bus_stops st_end ON r.end_stop_id = st_end.stop_id
                LEFT JOIN staff_assignments sa ON s.schedule_id = sa.schedule_id
                LEFT JOIN drivers d ON sa.driver_id = d.driver_id
                LEFT JOIN conductors c ON sa.conductor_id = c.conductor_id
                WHERE s.schedule_id = %s;
            """, (schedule_id,))
            schedule = cursor.fetchone()

            if not schedule:
                return api_response(success=False, message="Schedule not found.", status_code=404)

            # Fetch all booked seat numbers for this schedule
            cursor.execute("""
                SELECT seat_number, passenger_name, passenger_gender 
                FROM booking_seats 
                WHERE schedule_id = %s AND status = 'booked';
            """, (schedule_id,))
            booked_rows = cursor.fetchall() or []
            booked_seat_numbers = [r.get('seat_number') for r in booked_rows]

            capacity = schedule.get('capacity', 35)
            available_seat_numbers = [num for num in range(1, capacity + 1) if num not in booked_seat_numbers]

            schedule['booked_seats'] = booked_seat_numbers
            schedule['available_seats'] = available_seat_numbers
            schedule['total_available'] = len(available_seat_numbers)

            return api_response(data=schedule)
    except Exception as e:
        return api_response(success=False, message=f"Failed to fetch schedule: {str(e)}", status_code=500)

@schedule_bp.route('', methods=['POST'])
@admin_required
def create_schedule():
    data = request.get_json() or {}
    route_id = int(data.get('route_id', 0))
    bus_id = int(data.get('bus_id', 0))
    departure_time = data.get('departure_time', '').strip()
    arrival_time = data.get('arrival_time', '').strip()
    journey_date = data.get('journey_date', '').strip()
    fare = float(data.get('fare', 20.0))
    frequency = data.get('frequency', 'daily')
    status = data.get('status', 'scheduled')

    if route_id <= 0 or bus_id <= 0:
        return api_response(success=False, message="Valid route and bus are required.", status_code=400)
    if not validate_time(departure_time) or not validate_time(arrival_time):
        return api_response(success=False, message="Valid departure and arrival times required (HH:MM).", status_code=400)
    if not validate_date(journey_date):
        return api_response(success=False, message="Valid journey date required (YYYY-MM-DD).", status_code=400)

    try:
        with get_db_cursor(commit=True) as (conn, cursor):
            cursor.execute("""
                INSERT INTO schedules (
                    route_id, bus_id, departure_time, arrival_time, 
                    journey_date, fare, frequency, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, (route_id, bus_id, departure_time, arrival_time, journey_date, fare, frequency, status))
            new_id = cursor.lastrowid
            return api_response(data={"schedule_id": new_id}, message="Schedule created successfully.", status_code=201)
    except Exception as e:
        return api_response(success=False, message=f"Failed to create schedule: {str(e)}", status_code=500)

@schedule_bp.route('/<int:schedule_id>', methods=['PUT'])
@admin_required
def update_schedule(schedule_id):
    data = request.get_json() or {}
    route_id = int(data.get('route_id', 0))
    bus_id = int(data.get('bus_id', 0))
    departure_time = data.get('departure_time')
    arrival_time = data.get('arrival_time')
    journey_date = data.get('journey_date')
    fare = float(data.get('fare', 20.0))
    frequency = data.get('frequency', 'daily')
    status = data.get('status', 'scheduled')

    try:
        with get_db_cursor(commit=True) as (conn, cursor):
            cursor.execute("""
                UPDATE schedules 
                SET route_id = %s, bus_id = %s, departure_time = %s, arrival_time = %s,
                    journey_date = %s, fare = %s, frequency = %s, status = %s
                WHERE schedule_id = %s;
            """, (route_id, bus_id, departure_time, arrival_time, journey_date, fare, frequency, status, schedule_id))
            return api_response(message="Schedule updated successfully.")
    except Exception as e:
        return api_response(success=False, message=f"Failed to update schedule: {str(e)}", status_code=500)

@schedule_bp.route('/<int:schedule_id>', methods=['DELETE'])
@admin_required
def delete_schedule(schedule_id):
    try:
        with get_db_cursor(commit=True) as (conn, cursor):
            cursor.execute("SELECT COUNT(*) AS cnt FROM bookings WHERE schedule_id = %s AND booking_status = 'confirmed';", (schedule_id,))
            bk_cnt = cursor.fetchone().get('cnt', 0)
            if bk_cnt > 0:
                return api_response(
                    success=False,
                    message=f"Cannot delete schedule: It has {bk_cnt} confirmed booking(s). Change status to 'cancelled' instead.",
                    status_code=400
                )

            cursor.execute("DELETE FROM schedules WHERE schedule_id = %s;", (schedule_id,))
            return api_response(message=f"Schedule #{schedule_id} deleted successfully.")
    except Exception as e:
        return api_response(success=False, message=f"Failed to delete schedule: {str(e)}", status_code=500)
