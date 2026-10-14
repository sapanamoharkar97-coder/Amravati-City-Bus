import csv
import io
from flask import Blueprint, request, make_response
from db import get_db_cursor
from utils.decorators import api_response, admin_required

report_bp = Blueprint('report_bp', __name__, url_prefix='/api/reports')

@report_bp.route('/revenue', methods=['GET'])
@admin_required
def report_revenue():
    """Returns revenue grouped by date, payment method, and route."""
    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            # Revenue by payment method
            cursor.execute("""
                SELECT 
                    payment_method,
                    COUNT(payment_id) AS transaction_count,
                    COALESCE(SUM(amount), 0.00) AS total_revenue
                FROM payments
                WHERE transaction_status = 'success'
                GROUP BY payment_method;
            """)
            by_method = cursor.fetchall() or []

            # Revenue by date (Last 7 days or all demo records)
            cursor.execute("""
                SELECT 
                    DATE(payment_date) AS txn_date,
                    COUNT(payment_id) AS transactions_count,
                    COALESCE(SUM(amount), 0.00) AS daily_revenue
                FROM payments
                WHERE transaction_status = 'success'
                GROUP BY DATE(payment_date)
                ORDER BY txn_date ASC;
            """)
            by_date = cursor.fetchall() or []

            return api_response(data={
                "by_method": by_method,
                "by_date": by_date
            })
    except Exception as e:
        return api_response(success=False, message=f"Failed to generate revenue report: {str(e)}", status_code=500)

@report_bp.route('/popular-routes', methods=['GET'])
@admin_required
def report_popular_routes():
    """Rank routes by booking count, passenger volume, and revenue."""
    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            cursor.execute("""
                SELECT 
                    r.route_id,
                    r.route_number,
                    r.route_name,
                    COUNT(b.booking_id) AS total_bookings,
                    COALESCE(SUM(b.total_passengers), 0) AS total_passengers,
                    COALESCE(SUM(b.total_amount), 0.00) AS total_revenue
                FROM bus_routes r
                LEFT JOIN schedules s ON r.route_id = s.route_id
                LEFT JOIN bookings b ON s.schedule_id = b.schedule_id AND b.booking_status = 'confirmed'
                GROUP BY r.route_id, r.route_number, r.route_name
                ORDER BY total_bookings DESC, total_revenue DESC;
            """)
            popular = cursor.fetchall() or []
            return api_response(data=popular)
    except Exception as e:
        return api_response(success=False, message=f"Failed to generate popular routes report: {str(e)}", status_code=500)

@report_bp.route('/bus-occupancy', methods=['GET'])
@admin_required
def report_bus_occupancy():
    """Returns bus occupancy percentages from view v_bus_occupancy."""
    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            cursor.execute("""
                SELECT 
                    schedule_id, journey_date, departure_time,
                    route_number, route_name, bus_number, bus_type,
                    total_capacity, booked_seats, available_seats, occupancy_percentage
                FROM v_bus_occupancy
                ORDER BY occupancy_percentage DESC;
            """)
            occupancy = cursor.fetchall() or []
            return api_response(data=occupancy)
    except Exception as e:
        return api_response(success=False, message=f"Failed to generate occupancy report: {str(e)}", status_code=500)

@report_bp.route('/export-csv', methods=['GET'])
@admin_required
def export_csv_report():
    """Exports specified dataset to CSV format for Excel/reporting."""
    report_type = request.args.get('type', 'routes')
    output = io.StringIO()
    writer = csv.writer(output)

    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            if report_type == 'revenue':
                writer.writerow(['Payment ID', 'Reference', 'Amount (INR)', 'Method', 'Status', 'Date', 'Booking Reference'])
                cursor.execute("""
                    SELECT p.payment_id, p.payment_reference, p.amount, p.payment_method, 
                           p.transaction_status, p.payment_date, b.booking_reference
                    FROM payments p
                    INNER JOIN bookings b ON p.booking_id = b.booking_id;
                """)
                for row in cursor.fetchall():
                    writer.writerow([row['payment_id'], row['payment_reference'], row['amount'], row['payment_method'],
                                     row['transaction_status'], row['payment_date'], row['booking_reference']])
                filename = "amravati_bus_revenue_report.csv"

            elif report_type == 'occupancy':
                writer.writerow(['Schedule ID', 'Date', 'Time', 'Route', 'Bus Number', 'Type', 'Capacity', 'Booked', 'Available', 'Occupancy %'])
                cursor.execute("SELECT * FROM v_bus_occupancy;")
                for row in cursor.fetchall():
                    writer.writerow([row['schedule_id'], row['journey_date'], row['departure_time'],
                                     row['route_number'], row['bus_number'], row['bus_type'],
                                     row['total_capacity'], row['booked_seats'], row['available_seats'],
                                     row['occupancy_percentage']])
                filename = "amravati_bus_occupancy_report.csv"

            else:  # Default to popular routes
                writer.writerow(['Route Number', 'Route Name', 'Confirmed Bookings', 'Passengers Carried', 'Revenue (INR)'])
                cursor.execute("""
                    SELECT r.route_number, r.route_name, COUNT(b.booking_id) AS bk_cnt,
                           COALESCE(SUM(b.total_passengers), 0) AS pax_cnt,
                           COALESCE(SUM(b.total_amount), 0.00) AS rev
                    FROM bus_routes r
                    LEFT JOIN schedules s ON r.route_id = s.route_id
                    LEFT JOIN bookings b ON s.schedule_id = b.schedule_id AND b.booking_status = 'confirmed'
                    GROUP BY r.route_id, r.route_number, r.route_name;
                """)
                for row in cursor.fetchall():
                    writer.writerow([row['route_number'], row['route_name'], row['bk_cnt'], row['pax_cnt'], row['rev']])
                filename = "amravati_bus_popular_routes_report.csv"

        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        response.headers["Content-type"] = "text/csv"
        return response
    except Exception as e:
        return api_response(success=False, message=f"Failed to export CSV: {str(e)}", status_code=500)
