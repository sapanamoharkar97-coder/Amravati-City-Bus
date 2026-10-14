from flask import Blueprint, request
from db import get_db_cursor
from utils.decorators import api_response, admin_required

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/api/admin')

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard_metrics():
    """
    Returns aggregated KPIs, fleet status, financial metrics,
    and recent activity for the administrator console.
    """
    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            # Fleet statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) AS total_buses,
                    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) AS active_buses,
                    SUM(CASE WHEN status = 'maintenance' THEN 1 ELSE 0 END) AS maintenance_buses
                FROM buses;
            """)
            fleet = cursor.fetchone() or {}

            # Infrastructure & Crew
            cursor.execute("SELECT COUNT(*) AS total_routes FROM bus_routes WHERE is_active = TRUE;")
            routes_cnt = cursor.fetchone() or {}
            
            cursor.execute("SELECT COUNT(*) AS total_stops FROM bus_stops WHERE is_active = TRUE;")
            stops_cnt = cursor.fetchone() or {}

            cursor.execute("SELECT COUNT(*) AS active_drivers FROM drivers WHERE status = 'active';")
            drivers_cnt = cursor.fetchone() or {}

            cursor.execute("SELECT COUNT(*) AS active_conductors FROM conductors WHERE status = 'active';")
            conductors_cnt = cursor.fetchone() or {}

            # Bookings & Revenue
            cursor.execute("""
                SELECT 
                    COUNT(booking_id) AS total_bookings,
                    SUM(CASE WHEN booking_status = 'confirmed' THEN 1 ELSE 0 END) AS confirmed_bookings,
                    SUM(CASE WHEN booking_status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_bookings,
                    COALESCE(SUM(CASE WHEN booking_status = 'confirmed' THEN total_amount ELSE 0 END), 0.00) AS total_revenue
                FROM bookings;
            """)
            bookings_stats = cursor.fetchone() or {}

            # Today's schedules count
            cursor.execute("SELECT COUNT(*) AS today_schedules FROM schedules WHERE journey_date = CURDATE();")
            sched_cnt = cursor.fetchone() or {}

            # Recent 6 Bookings
            cursor.execute("""
                SELECT 
                    b.booking_id, b.booking_reference, b.booking_date, b.journey_date,
                    b.total_passengers, b.total_amount, b.booking_status,
                    u.full_name AS passenger_name, r.route_number, bus.bus_number
                FROM bookings b
                INNER JOIN users u ON b.user_id = u.user_id
                INNER JOIN schedules s ON b.schedule_id = s.schedule_id
                INNER JOIN bus_routes r ON s.route_id = r.route_id
                INNER JOIN buses bus ON s.bus_id = bus.bus_id
                ORDER BY b.booking_id DESC
                LIMIT 6;
            """)
            recent_bookings = cursor.fetchall() or []

            # Recent Audit Logs
            cursor.execute("""
                SELECT log_id, action, table_name, details, ip_address, created_at
                FROM audit_logs
                ORDER BY log_id DESC
                LIMIT 6;
            """)
            recent_audit = cursor.fetchall() or []

            metrics = {
                "total_buses": fleet.get('total_buses', 0),
                "active_buses": fleet.get('active_buses', 0),
                "maintenance_buses": fleet.get('maintenance_buses', 0),
                "total_routes": routes_cnt.get('total_routes', 0),
                "total_stops": stops_cnt.get('total_stops', 0),
                "active_drivers": drivers_cnt.get('active_drivers', 0),
                "active_conductors": conductors_cnt.get('active_conductors', 0),
                "today_schedules": sched_cnt.get('today_schedules', 0),
                "total_bookings": bookings_stats.get('total_bookings', 0),
                "confirmed_bookings": bookings_stats.get('confirmed_bookings', 0),
                "cancelled_bookings": bookings_stats.get('cancelled_bookings', 0),
                "total_revenue": float(bookings_stats.get('total_revenue', 0.00)),
                "recent_bookings": recent_bookings,
                "recent_audit": recent_audit
            }

            return api_response(data=metrics)
    except Exception as e:
        return api_response(success=False, message=f"Failed to fetch dashboard data: {str(e)}", status_code=500)

@admin_bp.route('/audit-logs', methods=['GET'])
@admin_required
def get_audit_logs():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    offset = (page - 1) * limit

    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            cursor.execute("SELECT COUNT(*) AS total FROM audit_logs;")
            total_count = cursor.fetchone().get('total', 0)

            cursor.execute("""
                SELECT log_id, user_id, action, table_name, record_id, details, ip_address, created_at
                FROM audit_logs
                ORDER BY log_id DESC
                LIMIT %s OFFSET %s;
            """, (limit, offset))
            logs = cursor.fetchall() or []

            return api_response(data={
                "logs": logs,
                "total": total_count,
                "page": page,
                "limit": limit
            })
    except Exception as e:
        return api_response(success=False, message=f"Failed to retrieve audit logs: {str(e)}", status_code=500)
