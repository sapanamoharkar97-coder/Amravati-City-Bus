from flask import Blueprint, request
from db import get_db_cursor
from utils.decorators import api_response, login_required, admin_required

ticket_bp = Blueprint('ticket_bp', __name__, url_prefix='/api')

@ticket_bp.route('/tickets/<int:ticket_id>', methods=['GET'])
@login_required
def get_ticket(ticket_id):
    user = request.current_user
    user_id = user.get('user_id')
    is_admin = user.get('role') == 'admin'

    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            cursor.execute("""
                SELECT 
                    t.ticket_id, t.ticket_number, t.qr_code_data, t.issued_at, t.status AS ticket_status,
                    b.booking_id, b.booking_reference, b.booking_date, b.journey_date,
                    b.total_passengers, b.total_amount, b.booking_status, b.user_id,
                    u.full_name AS booked_by_name, u.phone AS passenger_phone, u.email AS passenger_email,
                    s.departure_time, s.arrival_time,
                    r.route_number, r.route_name,
                    bus.bus_number, bus.bus_type,
                    st_src.stop_name AS boarding_stop,
                    st_dest.stop_name AS dropoff_stop,
                    p.payment_reference, p.payment_method, p.transaction_status AS payment_status
                FROM tickets t
                INNER JOIN bookings b ON t.booking_id = b.booking_id
                INNER JOIN users u ON b.user_id = u.user_id
                INNER JOIN schedules s ON b.schedule_id = s.schedule_id
                INNER JOIN bus_routes r ON s.route_id = r.route_id
                INNER JOIN buses bus ON s.bus_id = bus.bus_id
                INNER JOIN bus_stops st_src ON b.source_stop_id = st_src.stop_id
                INNER JOIN bus_stops st_dest ON b.destination_stop_id = st_dest.stop_id
                LEFT JOIN payments p ON b.booking_id = p.booking_id
                WHERE t.ticket_id = %s;
            """, (ticket_id,))
            ticket = cursor.fetchone()

            if not ticket:
                return api_response(success=False, message="Ticket not found.", status_code=404)

            if not is_admin and ticket.get('user_id') != user_id:
                return api_response(success=False, message="Access denied to this ticket.", status_code=403)

            # Fetch passenger seat allocations
            cursor.execute("""
                SELECT seat_number, passenger_name, passenger_age, passenger_gender, fare, status
                FROM booking_seats
                WHERE booking_id = %s;
            """, (ticket.get('booking_id'),))
            seats = cursor.fetchall() or []
            ticket['seats'] = seats

            return api_response(data=ticket)
    except Exception as e:
        return api_response(success=False, message=f"Failed to fetch ticket: {str(e)}", status_code=500)

@ticket_bp.route('/tickets/booking/<int:booking_id>', methods=['GET'])
@login_required
def get_ticket_by_booking(booking_id):
    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            cursor.execute("SELECT ticket_id FROM tickets WHERE booking_id = %s;", (booking_id,))
            row = cursor.fetchone()
            if not row:
                return api_response(success=False, message="Ticket not found for this booking.", status_code=404)
            ticket_id = row.get('ticket_id') if isinstance(row, dict) else row[0]
            return get_ticket(ticket_id)
    except Exception as e:
        return api_response(success=False, message=f"Failed to fetch ticket: {str(e)}", status_code=500)

@ticket_bp.route('/payments', methods=['GET'])
@admin_required
def list_payments():
    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            cursor.execute("""
                SELECT 
                    p.payment_id, p.payment_reference, p.amount, p.payment_method, 
                    p.transaction_status, p.payment_date, p.notes,
                    b.booking_reference, b.journey_date,
                    u.full_name AS passenger_name, u.email AS passenger_email
                FROM payments p
                INNER JOIN bookings b ON p.booking_id = b.booking_id
                INNER JOIN users u ON b.user_id = u.user_id
                ORDER BY p.payment_date DESC;
            """)
            payments = cursor.fetchall() or []
            return api_response(data=payments)
    except Exception as e:
        return api_response(success=False, message=f"Failed to fetch payments: {str(e)}", status_code=500)
