-- ==============================================================================
-- Project: City Bus Management System for Amravati
-- File: crud_queries.sql
-- Description: Practical and comprehensive SQL demonstrations adapted directly
--              to city_bus_db schema. Includes CRUD, advanced filters, pattern
--              matching, aggregate operations, joins, group by, having, and subqueries.
-- Suitable for DBMS practical lab evaluations, viva demonstrations, and testing.
-- ==============================================================================

USE city_bus_db;

-- ==============================================================================
-- 1. BASIC CRUD OPERATIONS
-- ==============================================================================

-- 1.1 INSERT: Add a new bus to the Amravati fleet
INSERT INTO buses (bus_number, registration_number, bus_type, capacity, status)
VALUES ('AMT-CITY-08', 'MH-27-X-1008', 'Electric AC', 35, 'active');

-- 1.2 SELECT: View all registered active buses
SELECT bus_id, bus_number, registration_number, bus_type, capacity, status
FROM buses
WHERE status = 'active';

-- 1.3 UPDATE: Update bus capacity safely using Primary Key
-- (Notice: always specify primary key in WHERE clause to satisfy MySQL SQL_SAFE_UPDATES)
UPDATE buses
SET capacity = 38,
    status = 'active'
WHERE bus_id = 8;

-- 1.4 DELETE: Remove test bus safely using primary key
DELETE FROM buses
WHERE bus_id = 8;


-- ==============================================================================
-- 2. SEARCHING, SORTING, AND FILTERING
-- ==============================================================================

-- 2.1 Pattern Matching with LIKE: Search stops containing 'Nagar' or 'Square'
SELECT stop_id, stop_name, landmark, city
FROM bus_stops
WHERE stop_name LIKE '%Square%' OR stop_name LIKE '%Nagar%'
ORDER BY stop_name ASC;

-- 2.2 Range query with BETWEEN: Find schedules with fares between Rs 15 and Rs 25
SELECT schedule_id, route_id, departure_time, arrival_time, fare, status
FROM schedules
WHERE fare BETWEEN 15.00 AND 25.00
ORDER BY fare DESC;

-- 2.3 Membership check with IN: Find buses of specific eco-friendly types
SELECT bus_id, bus_number, registration_number, bus_type, capacity
FROM buses
WHERE bus_type IN ('Electric AC', 'CNG Express')
ORDER BY capacity DESC;

-- 2.4 Multi-column Sorting: View all schedules sorted by journey date and departure time
SELECT schedule_id, journey_date, departure_time, arrival_time, fare, status
FROM schedules
ORDER BY journey_date ASC, departure_time ASC;


-- ==============================================================================
-- 3. AGGREGATE FUNCTIONS & METRICS
-- ==============================================================================

-- 3.1 COUNT, SUM, AVG, MIN, MAX over bookings and fares
SELECT 
    COUNT(booking_id) AS total_bookings_count,
    SUM(total_amount) AS gross_revenue_inr,
    AVG(total_amount) AS average_booking_value_inr,
    MIN(total_amount) AS lowest_ticket_price_inr,
    MAX(total_amount) AS highest_ticket_price_inr
FROM bookings
WHERE booking_status = 'confirmed';


-- ==============================================================================
-- 4. RELATIONAL JOINS (INNER & LEFT JOINS)
-- ==============================================================================

-- 4.1 INNER JOIN: Get complete route details with Start and Destination Stop Names
SELECT 
    r.route_id,
    r.route_number,
    r.route_name,
    s_start.stop_name AS start_stop,
    s_end.stop_name AS destination_stop,
    r.total_distance_km,
    r.estimated_duration_mins,
    r.base_fare
FROM bus_routes r
INNER JOIN bus_stops s_start ON r.start_stop_id = s_start.stop_id
INNER JOIN bus_stops s_end ON r.end_stop_id = s_end.stop_id
WHERE r.is_active = TRUE;

-- 4.2 MULTI-TABLE INNER JOIN: Detailed schedule view with assigned Bus, Route, Driver & Conductor
SELECT 
    s.schedule_id,
    r.route_number,
    r.route_name,
    b.bus_number,
    b.bus_type,
    s.journey_date,
    s.departure_time,
    s.arrival_time,
    s.fare,
    d.full_name AS driver_name,
    c.full_name AS conductor_name
FROM schedules s
INNER JOIN bus_routes r ON s.route_id = r.route_id
INNER JOIN buses b ON s.bus_id = b.bus_id
LEFT JOIN staff_assignments sa ON s.schedule_id = sa.schedule_id
LEFT JOIN drivers d ON sa.driver_id = d.driver_id
LEFT JOIN conductors c ON sa.conductor_id = c.conductor_id
ORDER BY s.journey_date ASC, s.departure_time ASC;

-- 4.3 LEFT JOIN: Find all buses and check if they currently have schedules assigned
SELECT 
    b.bus_id,
    b.bus_number,
    b.bus_type,
    b.capacity,
    COUNT(s.schedule_id) AS total_assigned_trips
FROM buses b
LEFT JOIN schedules s ON b.bus_id = s.bus_id
GROUP BY b.bus_id, b.bus_number, b.bus_type, b.capacity
ORDER BY total_assigned_trips DESC;


-- ==============================================================================
-- 5. GROUP BY & HAVING CLAUSES
-- ==============================================================================

-- 5.1 GROUP BY: Route-wise booking count and total collections
SELECT 
    r.route_id,
    r.route_number,
    r.route_name,
    COUNT(b.booking_id) AS total_confirmed_bookings,
    SUM(b.total_amount) AS route_revenue_inr
FROM bus_routes r
INNER JOIN schedules s ON r.route_id = s.route_id
INNER JOIN bookings b ON s.schedule_id = b.schedule_id
WHERE b.booking_status = 'confirmed'
GROUP BY r.route_id, r.route_number, r.route_name;

-- 5.2 GROUP BY with HAVING: Find routes generating revenue exceeding Rs 20.00
SELECT 
    r.route_number,
    r.route_name,
    COUNT(b.booking_id) AS bookings_count,
    SUM(b.total_amount) AS total_revenue
FROM bus_routes r
INNER JOIN schedules s ON r.route_id = s.route_id
INNER JOIN bookings b ON s.schedule_id = b.schedule_id
WHERE b.booking_status = 'confirmed'
GROUP BY r.route_id, r.route_number, r.route_name
HAVING SUM(b.total_amount) >= 20.00
ORDER BY total_revenue DESC;


-- ==============================================================================
-- 6. SUBQUERIES (Scalar, In-Clause, Correlated)
-- ==============================================================================

-- 6.1 Subquery with IN: Find passengers who have booked seats on Electric AC buses
SELECT user_id, full_name, email, phone
FROM users
WHERE user_id IN (
    SELECT b.user_id
    FROM bookings b
    INNER JOIN schedules s ON b.schedule_id = s.schedule_id
    INNER JOIN buses bus ON s.bus_id = bus.bus_id
    WHERE bus.bus_type = 'Electric AC'
);

-- 6.2 Scalar Subquery: Find schedules where the fare is greater than the average fare
SELECT schedule_id, route_id, bus_id, fare
FROM schedules
WHERE fare > (SELECT AVG(fare) FROM schedules);

-- 6.3 Correlated Subquery: Count booked seats per schedule without joining entire seat table
SELECT 
    s.schedule_id,
    s.journey_date,
    s.departure_time,
    b.capacity,
    (
        SELECT COUNT(*)
        FROM booking_seats bs
        WHERE bs.schedule_id = s.schedule_id AND bs.status = 'booked'
    ) AS seats_booked,
    (
        b.capacity - (
            SELECT COUNT(*)
            FROM booking_seats bs
            WHERE bs.schedule_id = s.schedule_id AND bs.status = 'booked'
        )
    ) AS seats_remaining
FROM schedules s
INNER JOIN buses b ON s.bus_id = b.bus_id;
