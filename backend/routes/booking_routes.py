from flask import Blueprint, request
from db import get_db_cursor
from services.booking_service import BookingService
from utils.decorators import api_response, login_required

booking_bp = Blueprint('booking_bp', __name__, url_prefix='/api/bookings')

@booking_bp.route('', methods=['POST'])
@login_required
def create_booking():
    user = request.current_user
    user_id = user.get('user_id')
    data = request.get_json() or {}

    schedule_id = int(data.get('schedule_id', 0))
    source_stop_id = int(data.get('source_stop_id', 0))
    dest_stop_id = int(data.get('dest_stop_id', 0))
    seats = data.get('seats', [])
    payment_method = data.get('payment_method', 'DEMO_UPI')

    if schedule_id <= 0 or source_stop_id <= 0 or dest_stop_id <= 0:
        return api_response(success=False, message="Valid schedule, source stop, and destination stop are required.", status_code=400)
    if not seats or not isinstance(seats, list):
        return api_response(success=False, message="At least one seat must be selected.", status_code=400)

    try:
        booking_result = BookingService.create_booking(
            user_id=user_id,
            schedule_id=schedule_id,
            source_stop_id=source_stop_id,
            dest_stop_id=dest_stop_id,
            seats=seats,
            payment_method=payment_method
        )
        return api_response(
            data=booking_result,
            message="Booking confirmed successfully! Ticket generated.",
            status_code=201
        )
    except ValueError as ve:
        return api_response(success=False, message=str(ve), status_code=400)
    except Exception as e:
        return api_response(success=False, message=f"Booking transaction error: {str(e)}", status_code=500)

@booking_bp.route('', methods=['GET'])
@login_required
def list_bookings():
    user = request.current_user
    user_id = user.get('user_id')
    is_admin = user.get('role') == 'admin'

    status_filter = request.args.get('status')
    search = request.args.get('search', '').strip()

    query = """
        SELECT 
            b.booking_id, b.booking_reference, b.booking_date, b.journey_date,
            b.total_passengers, b.total_amount, b.booking_status, b.cancellation_reason,
            u.full_name AS passenger_name, u.email AS passenger_email, u.phone AS passenger_phone,
            s.departure_time, s.arrival_time,
            r.route_number, r.route_name,
            bus.bus_number, bus.bus_type,
            st_src.stop_name AS boarding_stop,
            st_dest.stop_name AS dropoff_stop,
            t.ticket_id, t.ticket_number, t.status AS ticket_status,
            p.payment_reference, p.payment_method, p.transaction_status AS payment_status
        FROM bookings b
        INNER JOIN users u ON b.user_id = u.user_id
        INNER JOIN schedules s ON b.schedule_id = s.schedule_id
        INNER JOIN bus_routes r ON s.route_id = r.route_id
        INNER JOIN buses bus ON s.bus_id = bus.bus_id
        INNER JOIN bus_stops st_src ON b.source_stop_id = st_src.stop_id
        INNER JOIN bus_stops st_dest ON b.destination_stop_id = st_dest.stop_id
        LEFT JOIN tickets t ON b.booking_id = t.booking_id
        LEFT JOIN payments p ON b.booking_id = p.booking_id
        WHERE 1=1
    """
    params = []

    # Non-admin passengers can ONLY see their own bookings
    if not is_admin:
        query += " AND b.user_id = %s"
        params.append(user_id)

    if status_filter:
        query += " AND b.booking_status = %s"
        params.append(status_filter)

    if search:
        query += " AND (b.booking_reference LIKE %s OR u.full_name LIKE %s OR r.route_number LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    query += " ORDER BY b.booking_date DESC;"

    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            cursor.execute(query, tuple(params))
            bookings = cursor.fetchall() or []
            return api_response(data=bookings)
    except Exception as e:
        return api_response(success=False, message=f"Failed to fetch bookings: {str(e)}", status_code=500)

@booking_bp.route('/<int:booking_id>', methods=['GET'])
@login_required
def get_booking(booking_id):
    user = request.current_user
    user_id = user.get('user_id')
    is_admin = user.get('role') == 'admin'

    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            cursor.execute("""
                SELECT 
                    b.booking_id, b.booking_reference, b.booking_date, b.journey_date,
                    b.total_passengers, b.total_amount, b.booking_status, b.cancellation_reason, b.cancelled_at,
                    b.user_id, u.full_name AS passenger_name, u.email AS passenger_email, u.phone AS passenger_phone,
                    s.schedule_id, s.departure_time, s.arrival_time,
                    r.route_number, r.route_name,
                    bus.bus_number, bus.bus_type,
                    st_src.stop_name AS boarding_stop,
                    st_dest.stop_name AS dropoff_stop,
                    t.ticket_id, t.ticket_number, t.qr_code_data, t.issued_at, t.status AS ticket_status,
                    p.payment_id, p.payment_reference, p.payment_method, p.transaction_status AS payment_status
                FROM bookings b
                INNER JOIN users u ON b.user_id = u.user_id
                INNER JOIN schedules s ON b.schedule_id = s.schedule_id
                INNER JOIN bus_routes r ON s.route_id = r.route_id
                INNER JOIN buses bus ON s.bus_id = bus.bus_id
                INNER JOIN bus_stops st_src ON b.source_stop_id = st_src.stop_id
                INNER JOIN bus_stops st_dest ON b.destination_stop_id = st_dest.stop_id
                LEFT JOIN tickets t ON b.booking_id = t.booking_id
                LEFT JOIN payments p ON b.booking_id = p.booking_id
                WHERE b.booking_id = %s;
            """, (booking_id,))
            booking = cursor.fetchone()

            if not booking:
                return api_response(success=False, message="Booking not found.", status_code=404)

            # Access control check
            if not is_admin and booking.get('user_id') != user_id:
                return api_response(success=False, message="Access denied to this booking.", status_code=403)

            # Fetch individual seats
            cursor.execute("""
                SELECT booking_seat_id, seat_number, passenger_name, passenger_age, passenger_gender, fare, status
                FROM booking_seats
                WHERE booking_id = %s;
            """, (booking_id,))
            seats = cursor.fetchall() or []
            booking['seats'] = seats

            return api_response(data=booking)
    except Exception as e:
        return api_response(success=False, message=f"Failed to fetch booking: {str(e)}", status_code=500)

@booking_bp.route('/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    user = request.current_user
    user_id = user.get('user_id')
    is_admin = user.get('role') == 'admin'
    data = request.get_json() or {}
    reason = data.get('reason', 'Passenger cancellation request').strip()

    try:
        res = BookingService.cancel_booking(
            booking_id=booking_id,
            user_id=user_id,
            is_admin=is_admin,
            reason=reason
        )
        return api_response(data=res, message="Booking successfully cancelled.")
    except PermissionError as pe:
        return api_response(success=False, message=str(pe), status_code=403)
    except ValueError as ve:
        return api_response(success=False, message=str(ve), status_code=400)
    except Exception as e:
        return api_response(success=False, message=f"Cancellation error: {str(e)}", status_code=500)
