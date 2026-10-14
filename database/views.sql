-- ==============================================================================
-- Project: City Bus Management System for Amravati
-- File: views.sql
-- Description: MySQL Views providing simplified relational abstraction,
--              reporting summaries, and consolidated queries for the frontend.
-- Compatible with MySQL 8.x and MySQL Workbench.
-- ==============================================================================

USE city_bus_db;

-- ------------------------------------------------------------------------------
-- 1. View: v_route_stop_details
-- Denormalized stop sequence for every active route, including halts and distance.
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_route_stop_details AS
SELECT 
    rs.route_stop_id,
    r.route_id,
    r.route_number,
    r.route_name,
    rs.stop_sequence,
    s.stop_id,
    s.stop_name,
    s.landmark,
    rs.distance_from_source_km,
    rs.fare_from_source,
    rs.halt_duration_mins
FROM route_stops rs
INNER JOIN bus_routes r ON rs.route_id = r.route_id
INNER JOIN bus_stops s ON rs.stop_id = s.stop_id
ORDER BY r.route_id ASC, rs.stop_sequence ASC;

-- ------------------------------------------------------------------------------
-- 2. View: v_schedule_details
-- Timetable view with route names, start/end stops, bus details, and driver/conductor.
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_schedule_details AS
SELECT 
    s.schedule_id,
    s.journey_date,
    s.departure_time,
    s.arrival_time,
    s.fare,
    s.frequency,
    s.status AS schedule_status,
    r.route_id,
    r.route_number,
    r.route_name,
    st_start.stop_name AS origin_stop,
    st_end.stop_name AS destination_stop,
    r.total_distance_km,
    r.estimated_duration_mins,
    b.bus_id,
    b.bus_number,
    b.registration_number,
    b.bus_type,
    b.capacity AS total_capacity,
    sa.driver_id,
    d.full_name AS driver_name,
    d.phone AS driver_phone,
    sa.conductor_id,
    c.full_name AS conductor_name,
    c.badge_number AS conductor_badge
FROM schedules s
INNER JOIN bus_routes r ON s.route_id = r.route_id
INNER JOIN bus_stops st_start ON r.start_stop_id = st_start.stop_id
INNER JOIN bus_stops st_end ON r.end_stop_id = st_end.stop_id
INNER JOIN buses b ON s.bus_id = b.bus_id
LEFT JOIN staff_assignments sa ON s.schedule_id = sa.schedule_id
LEFT JOIN drivers d ON sa.driver_id = d.driver_id
LEFT JOIN conductors c ON sa.conductor_id = c.conductor_id;

-- ------------------------------------------------------------------------------
-- 3. View: v_booking_details
-- Complete view of passenger bookings with schedule, passenger, and ticket details.
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_booking_details AS
SELECT 
    b.booking_id,
    b.booking_reference,
    b.booking_date,
    b.journey_date,
    b.total_passengers,
    b.total_amount,
    b.booking_status,
    b.cancellation_reason,
    b.cancelled_at,
    u.user_id,
    u.username,
    u.full_name AS booked_by_name,
    u.email AS user_email,
    u.phone AS user_phone,
    s.schedule_id,
    s.departure_time,
    s.arrival_time,
    r.route_number,
    r.route_name,
    bus.bus_number,
    bus.bus_type,
    st_src.stop_name AS boarding_stop,
    st_dest.stop_name AS dropoff_stop,
    t.ticket_id,
    t.ticket_number,
    t.status AS ticket_status,
    p.payment_id,
    p.payment_reference,
    p.payment_method,
    p.transaction_status AS payment_status
FROM bookings b
INNER JOIN users u ON b.user_id = u.user_id
INNER JOIN schedules s ON b.schedule_id = s.schedule_id
INNER JOIN bus_routes r ON s.route_id = r.route_id
INNER JOIN buses bus ON s.bus_id = bus.bus_id
INNER JOIN bus_stops st_src ON b.source_stop_id = st_src.stop_id
INNER JOIN bus_stops st_dest ON b.destination_stop_id = st_dest.stop_id
LEFT JOIN tickets t ON b.booking_id = t.booking_id
LEFT JOIN payments p ON b.booking_id = p.booking_id;

-- ------------------------------------------------------------------------------
-- 4. View: v_bus_occupancy
-- Real-time capacity utilization, booked seats count, and remaining seats.
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_bus_occupancy AS
SELECT 
    s.schedule_id,
    s.journey_date,
    s.departure_time,
    r.route_number,
    r.route_name,
    b.bus_id,
    b.bus_number,
    b.bus_type,
    b.capacity AS total_capacity,
    COALESCE(COUNT(CASE WHEN bs.status = 'booked' THEN bs.booking_seat_id END), 0) AS booked_seats,
    (b.capacity - COALESCE(COUNT(CASE WHEN bs.status = 'booked' THEN bs.booking_seat_id END), 0)) AS available_seats,
    ROUND((COALESCE(COUNT(CASE WHEN bs.status = 'booked' THEN bs.booking_seat_id END), 0) / b.capacity) * 100, 2) AS occupancy_percentage
FROM schedules s
INNER JOIN bus_routes r ON s.route_id = r.route_id
INNER JOIN buses b ON s.bus_id = b.bus_id
LEFT JOIN booking_seats bs ON s.schedule_id = bs.schedule_id
GROUP BY 
    s.schedule_id,
    s.journey_date,
    s.departure_time,
    r.route_number,
    r.route_name,
    b.bus_id,
    b.bus_number,
    b.bus_type,
    b.capacity;
