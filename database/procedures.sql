-- ==============================================================================
-- Project: City Bus Management System for Amravati
-- File: procedures.sql
-- Description: Stored Procedures for schedule search, passenger booking history,
--              and route revenue/occupancy summaries.
-- Compatible with MySQL 8.x and MySQL Workbench.
-- ==============================================================================

USE city_bus_db;

DROP PROCEDURE IF EXISTS sp_search_schedules;
DROP PROCEDURE IF EXISTS sp_get_passenger_booking_history;
DROP PROCEDURE IF EXISTS sp_route_revenue_summary;

DELIMITER $$

-- ------------------------------------------------------------------------------
-- 1. Procedure: sp_search_schedules
-- Finds direct schedules connecting source stop to destination stop on a given date.
-- Computes available seats dynamically from bus capacity and booked seats.
-- ------------------------------------------------------------------------------
CREATE PROCEDURE sp_search_schedules(
    IN p_source_stop_id INT,
    IN p_dest_stop_id INT,
    IN p_travel_date DATE
)
BEGIN
    SELECT 
        s.schedule_id,
        s.journey_date,
        s.departure_time,
        s.arrival_time,
        s.status AS schedule_status,
        r.route_id,
        r.route_number,
        r.route_name,
        b.bus_id,
        b.bus_number,
        b.bus_type,
        b.capacity AS total_capacity,
        st_src.stop_name AS source_stop_name,
        st_dst.stop_name AS dest_stop_name,
        rs_src.stop_sequence AS src_sequence,
        rs_dst.stop_sequence AS dst_sequence,
        -- Calculate partial route fare based on stage difference, or default base fare
        GREATEST(r.base_fare, ABS(rs_dst.fare_from_source - rs_src.fare_from_source)) AS calculated_fare,
        -- Compute real-time booked seats
        (
            SELECT COUNT(*)
            FROM booking_seats bs
            WHERE bs.schedule_id = s.schedule_id AND bs.status = 'booked'
        ) AS booked_seats,
        -- Compute remaining seats
        (
            b.capacity - (
                SELECT COUNT(*)
                FROM booking_seats bs
                WHERE bs.schedule_id = s.schedule_id AND bs.status = 'booked'
            )
        ) AS available_seats
    FROM schedules s
    INNER JOIN bus_routes r ON s.route_id = r.route_id
    INNER JOIN buses b ON s.bus_id = b.bus_id
    INNER JOIN route_stops rs_src ON r.route_id = rs_src.route_id AND rs_src.stop_id = p_source_stop_id
    INNER JOIN route_stops rs_dst ON r.route_id = rs_dst.route_id AND rs_dst.stop_id = p_dest_stop_id
    INNER JOIN bus_stops st_src ON rs_src.stop_id = st_src.stop_id
    INNER JOIN bus_stops st_dst ON rs_dst.stop_id = st_dst.stop_id
    WHERE rs_src.stop_sequence < rs_dst.stop_sequence -- Must be in valid travel direction
      AND (s.journey_date = p_travel_date OR p_travel_date IS NULL)
      AND s.status = 'scheduled'
      AND b.status = 'active'
    ORDER BY s.departure_time ASC;
END$$


-- ------------------------------------------------------------------------------
-- 2. Procedure: sp_get_passenger_booking_history
-- Retrieves all bookings, seat details, and payment statuses for a specific user.
-- ------------------------------------------------------------------------------
CREATE PROCEDURE sp_get_passenger_booking_history(
    IN p_user_id INT
)
BEGIN
    SELECT 
        b.booking_id,
        b.booking_reference,
        b.booking_date,
        b.journey_date,
        b.booking_status,
        b.total_passengers,
        b.total_amount,
        b.cancellation_reason,
        s.departure_time,
        s.arrival_time,
        r.route_number,
        r.route_name,
        buses.bus_number,
        buses.bus_type,
        s_src.stop_name AS boarding_stop,
        s_dst.stop_name AS destination_stop,
        t.ticket_number,
        p.transaction_status AS payment_status,
        p.payment_method
    FROM bookings b
    INNER JOIN schedules s ON b.schedule_id = s.schedule_id
    INNER JOIN bus_routes r ON s.route_id = r.route_id
    INNER JOIN buses ON s.bus_id = buses.bus_id
    INNER JOIN bus_stops s_src ON b.source_stop_id = s_src.stop_id
    INNER JOIN bus_stops s_dst ON b.destination_stop_id = s_dst.stop_id
    LEFT JOIN tickets t ON b.booking_id = t.booking_id
    LEFT JOIN payments p ON b.booking_id = p.booking_id
    WHERE b.user_id = p_user_id
    ORDER BY b.booking_date DESC;
END$$


-- ------------------------------------------------------------------------------
-- 3. Procedure: sp_route_revenue_summary
-- Generates administrative metrics on bookings, revenue, and average passenger count per route.
-- ------------------------------------------------------------------------------
CREATE PROCEDURE sp_route_revenue_summary(
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    SELECT 
        r.route_id,
        r.route_number,
        r.route_name,
        COUNT(DISTINCT s.schedule_id) AS total_schedules_run,
        COUNT(DISTINCT CASE WHEN b.booking_status = 'confirmed' THEN b.booking_id END) AS confirmed_bookings,
        COUNT(DISTINCT CASE WHEN b.booking_status = 'cancelled' THEN b.booking_id END) AS cancelled_bookings,
        COALESCE(SUM(CASE WHEN b.booking_status = 'confirmed' THEN b.total_passengers END), 0) AS total_passengers_carried,
        COALESCE(SUM(CASE WHEN b.booking_status = 'confirmed' THEN b.total_amount END), 0.00) AS total_revenue_inr
    FROM bus_routes r
    LEFT JOIN schedules s ON r.route_id = s.route_id 
        AND (s.journey_date BETWEEN p_start_date AND p_end_date OR (p_start_date IS NULL AND p_end_date IS NULL))
    LEFT JOIN bookings b ON s.schedule_id = b.schedule_id
    GROUP BY r.route_id, r.route_number, r.route_name
    ORDER BY total_revenue_inr DESC;
END$$

DELIMITER ;
