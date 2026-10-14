-- ==============================================================================
-- Project: City Bus Management System for Amravati
-- File: reports.sql
-- Description: Analytical and management reporting SQL queries for transport operations.
-- Compatible with MySQL 8.x, MySQL Workbench, and reporting dashboards.
-- ==============================================================================

USE city_bus_db;

-- ------------------------------------------------------------------------------
-- 1. FLEET OVERVIEW: Total buses, active buses, and breakdown by fuel/bus type
-- ------------------------------------------------------------------------------
SELECT 
    COUNT(*) AS total_fleet_count,
    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) AS active_buses,
    SUM(CASE WHEN status = 'maintenance' THEN 1 ELSE 0 END) AS maintenance_buses,
    SUM(CASE WHEN status = 'retired' THEN 1 ELSE 0 END) AS retired_buses,
    SUM(CASE WHEN bus_type = 'Electric AC' THEN 1 ELSE 0 END) AS electric_buses,
    SUM(CASE WHEN bus_type = 'CNG Express' THEN 1 ELSE 0 END) AS cng_buses,
    SUM(CASE WHEN bus_type = 'Ordinary' THEN 1 ELSE 0 END) AS ordinary_buses,
    SUM(CASE WHEN bus_type = 'Mini Bus' THEN 1 ELSE 0 END) AS mini_buses
FROM buses;

-- ------------------------------------------------------------------------------
-- 2. INFRASTRUCTURE: Total routes and active bus stops
-- ------------------------------------------------------------------------------
SELECT 
    (SELECT COUNT(*) FROM bus_routes WHERE is_active = TRUE) AS active_routes_count,
    (SELECT COUNT(*) FROM bus_stops WHERE is_active = TRUE) AS total_active_stops,
    (SELECT COUNT(*) FROM drivers WHERE status = 'active') AS active_drivers,
    (SELECT COUNT(*) FROM conductors WHERE status = 'active') AS active_conductors;

-- ------------------------------------------------------------------------------
-- 3. DAILY SCHEDULES: Summary for today
-- ------------------------------------------------------------------------------
SELECT 
    s.schedule_id,
    r.route_number,
    r.route_name,
    b.bus_number,
    b.bus_type,
    s.departure_time,
    s.arrival_time,
    s.fare,
    s.status
FROM schedules s
INNER JOIN bus_routes r ON s.route_id = r.route_id
INNER JOIN buses b ON s.bus_id = b.bus_id
WHERE s.journey_date = CURDATE()
ORDER BY s.departure_time ASC;

-- ------------------------------------------------------------------------------
-- 4. BOOKINGS BREAKDOWN: Confirmed vs Pending vs Cancelled
-- ------------------------------------------------------------------------------
SELECT 
    booking_status,
    COUNT(booking_id) AS total_count,
    COALESCE(SUM(total_passengers), 0) AS total_passengers,
    COALESCE(SUM(total_amount), 0.00) AS total_value_inr,
    ROUND((COUNT(booking_id) / (SELECT COUNT(*) FROM bookings) * 100), 2) AS percentage_of_total
FROM bookings
GROUP BY booking_status;

-- ------------------------------------------------------------------------------
-- 5. POPULAR ROUTES: Ranked by booking frequency and total passengers carried
-- ------------------------------------------------------------------------------
SELECT 
    r.route_id,
    r.route_number,
    r.route_name,
    COUNT(b.booking_id) AS total_confirmed_bookings,
    COALESCE(SUM(b.total_passengers), 0) AS total_passengers_travelled,
    COALESCE(SUM(b.total_amount), 0.00) AS total_fare_revenue_inr
FROM bus_routes r
INNER JOIN schedules s ON r.route_id = s.route_id
LEFT JOIN bookings b ON s.schedule_id = b.schedule_id AND b.booking_status = 'confirmed'
GROUP BY r.route_id, r.route_number, r.route_name
ORDER BY total_confirmed_bookings DESC, total_fare_revenue_inr DESC;

-- ------------------------------------------------------------------------------
-- 6. OCCUPANCY ANALYSIS: Seat utilization per schedule
-- ------------------------------------------------------------------------------
SELECT 
    s.schedule_id,
    r.route_number,
    s.journey_date,
    s.departure_time,
    b.bus_number,
    b.capacity AS bus_capacity,
    COUNT(CASE WHEN bs.status = 'booked' THEN bs.booking_seat_id END) AS seats_booked,
    (b.capacity - COUNT(CASE WHEN bs.status = 'booked' THEN bs.booking_seat_id END)) AS seats_vacant,
    ROUND((COUNT(CASE WHEN bs.status = 'booked' THEN bs.booking_seat_id END) / b.capacity) * 100, 1) AS occupancy_rate_percent
FROM schedules s
INNER JOIN bus_routes r ON s.route_id = r.route_id
INNER JOIN buses b ON s.bus_id = b.bus_id
LEFT JOIN booking_seats bs ON s.schedule_id = bs.schedule_id
GROUP BY s.schedule_id, r.route_number, s.journey_date, s.departure_time, b.bus_number, b.capacity
ORDER BY occupancy_rate_percent DESC;

-- ------------------------------------------------------------------------------
-- 7. REVENUE REPORT: Reconciled revenue from successful demo payments by method
-- ------------------------------------------------------------------------------
SELECT 
    p.payment_method,
    COUNT(p.payment_id) AS successful_transactions_count,
    SUM(p.amount) AS total_collected_amount_inr,
    AVG(p.amount) AS avg_transaction_value_inr
FROM payments p
WHERE p.transaction_status = 'success'
GROUP BY p.payment_method
ORDER BY total_collected_amount_inr DESC;

-- ------------------------------------------------------------------------------
-- 8. UPCOMING JOURNEYS: Upcoming confirmed trips from today onward
-- ------------------------------------------------------------------------------
SELECT 
    b.booking_id,
    b.booking_reference,
    b.journey_date,
    s.departure_time,
    r.route_number,
    r.route_name,
    u.full_name AS passenger_name,
    u.phone AS passenger_phone,
    b.total_passengers,
    t.ticket_number
FROM bookings b
INNER JOIN users u ON b.user_id = u.user_id
INNER JOIN schedules s ON b.schedule_id = s.schedule_id
INNER JOIN bus_routes r ON s.route_id = r.route_id
LEFT JOIN tickets t ON b.booking_id = t.booking_id
WHERE b.journey_date >= CURDATE()
  AND b.booking_status = 'confirmed'
ORDER BY b.journey_date ASC, s.departure_time ASC;
