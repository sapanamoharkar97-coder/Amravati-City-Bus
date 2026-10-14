-- ==============================================================================
-- Project: City Bus Management System for Amravati (Maharashtra, India)
-- File: sample_data.sql
-- Description: Demonstrative fictional test records for Amravati city bus network.
--              Includes users, passengers, drivers, conductors, buses, stops,
--              routes, route_stops, schedules, assignments, bookings, seats,
--              tickets, payments, and audit logs.
-- ==============================================================================

USE city_bus_db;

-- Clear previous sample records in child-to-parent order if desired during manual testing
-- (Disabled by default to avoid accidental data loss)

-- ------------------------------------------------------------------------------
-- 1. USERS & PASSENGERS
-- Password for all demo accounts is: Admin@123 (or Passenger@123)
-- Hashes use Werkzeug pbkdf2/scrypt format with backend fallback compatibility
-- ------------------------------------------------------------------------------
INSERT INTO users (user_id, username, email, password_hash, role, full_name, phone, is_active)
VALUES 
(1, 'admin', 'admin@amravaticitybus.in', 'pbkdf2:sha256:600000$t7x8P21yQpM4k9Lj$8831b9d1073dc0cb40ff8eb0e768e16be027e02b378eb2354c2eefef19fe29d3', 'admin', 'Amravati Transport Admin', '9822011223', TRUE),
(2, 'rahul_sharma', 'rahul.sharma@example.com', 'pbkdf2:sha256:600000$t7x8P21yQpM4k9Lj$8831b9d1073dc0cb40ff8eb0e768e16be027e02b378eb2354c2eefef19fe29d3', 'passenger', 'Rahul Sharma', '9823145678', TRUE),
(3, 'priya_patil', 'priya.patil@example.com', 'pbkdf2:sha256:600000$t7x8P21yQpM4k9Lj$8831b9d1073dc0cb40ff8eb0e768e16be027e02b378eb2354c2eefef19fe29d3', 'passenger', 'Priya Patil', '9422876543', TRUE),
(4, 'amit_deshmukh', 'amit.deshmukh@example.com', 'pbkdf2:sha256:600000$t7x8P21yQpM4k9Lj$8831b9d1073dc0cb40ff8eb0e768e16be027e02b378eb2354c2eefef19fe29d3', 'passenger', 'Amit Deshmukh', '9765432109', TRUE),
(5, 'snehal_kale', 'snehal.kale@example.com', 'pbkdf2:sha256:600000$t7x8P21yQpM4k9Lj$8831b9d1073dc0cb40ff8eb0e768e16be027e02b378eb2354c2eefef19fe29d3', 'passenger', 'Snehal Kale', '9890123456', TRUE)
ON DUPLICATE KEY UPDATE full_name=VALUES(full_name);

INSERT INTO passengers (passenger_id, user_id, gender, age, address, city, emergency_contact)
VALUES 
(1, 2, 'male', 24, 'Near Rajapeth Police Station, Amravati', 'Amravati', '9823145600'),
(2, 3, 'female', 22, 'Sai Nagar, Amravati', 'Amravati', '9422876500'),
(3, 4, 'male', 29, 'Camp Road, Near Collector Office', 'Amravati', '9765432100'),
(4, 5, 'female', 21, 'Gadge Nagar, SGBAU Campus Road', 'Amravati', '9890123400')
ON DUPLICATE KEY UPDATE address=VALUES(address);

-- ------------------------------------------------------------------------------
-- 2. DRIVERS & CONDUCTORS
-- ------------------------------------------------------------------------------
INSERT INTO drivers (driver_id, license_number, full_name, phone, experience_years, status)
VALUES
(1, 'MH-27-2012-00441', 'Suresh Wankhede', '9822456781', 12, 'active'),
(2, 'MH-27-2015-00892', 'Ganesh Tayade', '9422987123', 9, 'active'),
(3, 'MH-27-2018-00331', 'Vijay Gawande', '9765123984', 6, 'active'),
(4, 'MH-27-2010-00115', 'Santosh Kale', '9890334455', 14, 'active'),
(5, 'MH-27-2020-00994', 'Anil Belsare', '9158223344', 4, 'on_leave')
ON DUPLICATE KEY UPDATE full_name=VALUES(full_name);

INSERT INTO conductors (conductor_id, badge_number, full_name, phone, status)
VALUES
(1, 'CND-AMT-101', 'Ramesh Pote', '9822778811', 'active'),
(2, 'CND-AMT-102', 'Nitin Bhagat', '9422665522', 'active'),
(3, 'CND-AMT-103', 'Pradip Thakare', '9765443311', 'active'),
(4, 'CND-AMT-104', 'Sachin Deshmukh', '9890887766', 'active'),
(5, 'CND-AMT-105', 'Manoj Ingale', '9158112233', 'on_leave')
ON DUPLICATE KEY UPDATE full_name=VALUES(full_name);

-- ------------------------------------------------------------------------------
-- 3. BUS FLEET
-- ------------------------------------------------------------------------------
INSERT INTO buses (bus_id, bus_number, registration_number, bus_type, capacity, status)
VALUES
(1, 'AMT-CITY-01', 'MH-27-X-1001', 'Electric AC', 35, 'active'),
(2, 'AMT-CITY-02', 'MH-27-X-1002', 'CNG Express', 40, 'active'),
(3, 'AMT-CITY-03', 'MH-27-X-1003', 'Ordinary', 45, 'active'),
(4, 'AMT-CITY-04', 'MH-27-X-1004', 'Electric AC', 35, 'active'),
(5, 'AMT-CITY-05', 'MH-27-X-1005', 'Ordinary', 42, 'active'),
(6, 'AMT-CITY-06', 'MH-27-X-1006', 'Mini Bus', 24, 'active'),
(7, 'AMT-CITY-07', 'MH-27-X-1007', 'CNG Express', 40, 'maintenance')
ON DUPLICATE KEY UPDATE capacity=VALUES(capacity);

-- ------------------------------------------------------------------------------
-- 4. BUS STOPS (Amravati Key Locations)
-- ------------------------------------------------------------------------------
INSERT INTO bus_stops (stop_id, stop_name, landmark, latitude, longitude, city, is_active)
VALUES
(1, 'Badnera Railway Station', 'Platform 1 Main Exit', 20.865200, 77.728900, 'Amravati', TRUE),
(2, 'Rajkamal Square', 'Rajkamal Chowk Central Point', 20.932000, 77.752300, 'Amravati', TRUE),
(3, 'Irwin Hospital Chowk', 'District General Hospital', 20.937800, 77.755400, 'Amravati', TRUE),
(4, 'Panchavati Square', 'Panchavati Chowk & Market', 20.943100, 77.761000, 'Amravati', TRUE),
(5, 'Gadge Nagar (SGBAU Gate)', 'Sant Gadge Baba Amravati University', 20.963400, 77.778500, 'Amravati', TRUE),
(6, 'Central Bus Stand (ST Stand)', 'MSRTC Bus Station Depot', 20.931200, 77.760100, 'Amravati', TRUE),
(7, 'Shivaji Nagar (HVPM)', 'HVPM Sports Complex Main Gate', 20.925500, 77.746000, 'Amravati', TRUE),
(8, 'Walgaon Road MIDC', 'MIDC Phase 1 Entry Arch', 20.985000, 77.742000, 'Amravati', TRUE),
(9, 'Camp Collector Office', 'Civil Lines / Collectorate', 20.922000, 77.771000, 'Amravati', TRUE),
(10, 'Shegaon Naka', 'Shegaon Road Octroi Post', 20.954000, 77.749000, 'Amravati', TRUE)
ON DUPLICATE KEY UPDATE landmark=VALUES(landmark);

-- ------------------------------------------------------------------------------
-- 5. BUS ROUTES
-- ------------------------------------------------------------------------------
INSERT INTO bus_routes (route_id, route_number, route_name, start_stop_id, end_stop_id, total_distance_km, estimated_duration_mins, base_fare, is_active)
VALUES
(1, 'R-101', 'Badnera Station to SGBAU University', 1, 5, 14.50, 45, 15.00, TRUE),
(2, 'R-102', 'Central Bus Stand to HVPM Sports Complex', 6, 7, 5.20, 20, 10.00, TRUE),
(3, 'R-103', 'Rajkamal Square to Walgaon MIDC', 2, 8, 9.80, 35, 12.00, TRUE),
(4, 'R-104', 'Central Bus Stand to Camp Collector Office', 6, 9, 4.50, 18, 10.00, TRUE),
(5, 'R-105', 'Panchavati Square to Shegaon Naka Loop', 4, 10, 6.00, 25, 10.00, TRUE)
ON DUPLICATE KEY UPDATE route_name=VALUES(route_name);

-- ------------------------------------------------------------------------------
-- 6. ROUTE STOPS (Sequence, Halts, Distance & Fare Stages)
-- ------------------------------------------------------------------------------
-- Route 101 Stops: Badnera -> Rajkamal -> Irwin -> Panchavati -> Gadge Nagar (SGBAU)
INSERT INTO route_stops (route_id, stop_id, stop_sequence, distance_from_source_km, fare_from_source, halt_duration_mins)
VALUES
(1, 1, 1, 0.00, 0.00, 0),
(1, 2, 2, 8.50, 15.00, 3),
(1, 3, 3, 9.80, 18.00, 2),
(1, 4, 4, 11.20, 20.00, 2),
(1, 5, 5, 14.50, 25.00, 5)
ON DUPLICATE KEY UPDATE fare_from_source=VALUES(fare_from_source);

-- Route 102 Stops: Central Bus Stand -> Rajkamal -> Shivaji Nagar (HVPM)
INSERT INTO route_stops (route_id, stop_id, stop_sequence, distance_from_source_km, fare_from_source, halt_duration_mins)
VALUES
(2, 6, 1, 0.00, 0.00, 0),
(2, 2, 2, 2.20, 10.00, 2),
(2, 7, 3, 5.20, 15.00, 3)
ON DUPLICATE KEY UPDATE fare_from_source=VALUES(fare_from_source);

-- Route 103 Stops: Rajkamal -> Irwin -> Panchavati -> Walgaon MIDC
INSERT INTO route_stops (route_id, stop_id, stop_sequence, distance_from_source_km, fare_from_source, halt_duration_mins)
VALUES
(3, 2, 1, 0.00, 0.00, 0),
(3, 3, 2, 1.30, 10.00, 2),
(3, 4, 3, 2.70, 12.00, 2),
(3, 8, 4, 9.80, 22.00, 4)
ON DUPLICATE KEY UPDATE fare_from_source=VALUES(fare_from_source);

-- Route 104 Stops: Central Bus Stand -> Rajkamal -> Camp Collector Office
INSERT INTO route_stops (route_id, stop_id, stop_sequence, distance_from_source_km, fare_from_source, halt_duration_mins)
VALUES
(4, 6, 1, 0.00, 0.00, 0),
(4, 2, 2, 1.80, 10.00, 2),
(4, 9, 3, 4.50, 15.00, 3)
ON DUPLICATE KEY UPDATE fare_from_source=VALUES(fare_from_source);

-- Route 105 Stops: Panchavati -> Gadge Nagar -> Shegaon Naka
INSERT INTO route_stops (route_id, stop_id, stop_sequence, distance_from_source_km, fare_from_source, halt_duration_mins)
VALUES
(5, 4, 1, 0.00, 0.00, 0),
(5, 5, 2, 3.30, 10.00, 2),
(5, 10, 3, 6.00, 15.00, 3)
ON DUPLICATE KEY UPDATE fare_from_source=VALUES(fare_from_source);

-- ------------------------------------------------------------------------------
-- 7. SCHEDULES (Daily and Peak Timetable)
-- ------------------------------------------------------------------------------
INSERT INTO schedules (schedule_id, route_id, bus_id, departure_time, arrival_time, journey_date, fare, frequency, status)
VALUES
(1, 1, 1, '08:00:00', '08:45:00', CURDATE(), 25.00, 'daily', 'scheduled'),
(2, 1, 2, '09:30:00', '10:15:00', CURDATE(), 25.00, 'daily', 'scheduled'),
(3, 1, 4, '11:00:00', '11:45:00', CURDATE(), 25.00, 'daily', 'scheduled'),
(4, 2, 3, '08:30:00', '08:50:00', CURDATE(), 15.00, 'daily', 'scheduled'),
(5, 2, 6, '10:00:00', '10:20:00', CURDATE(), 15.00, 'daily', 'scheduled'),
(6, 3, 5, '09:00:00', '09:35:00', CURDATE(), 22.00, 'daily', 'scheduled'),
(7, 4, 3, '14:00:00', '14:20:00', CURDATE(), 15.00, 'daily', 'scheduled'),
(8, 5, 1, '16:00:00', '16:25:00', CURDATE(), 15.00, 'daily', 'scheduled'),
(9, 1, 1, '08:00:00', '08:45:00', DATE_ADD(CURDATE(), INTERVAL 1 DAY), 25.00, 'daily', 'scheduled'),
(10, 2, 3, '09:00:00', '09:20:00', DATE_ADD(CURDATE(), INTERVAL 1 DAY), 15.00, 'daily', 'scheduled')
ON DUPLICATE KEY UPDATE status=VALUES(status);

-- ------------------------------------------------------------------------------
-- 8. STAFF ASSIGNMENTS
-- ------------------------------------------------------------------------------
INSERT INTO staff_assignments (assignment_id, schedule_id, driver_id, conductor_id, assigned_date, status)
VALUES
(1, 1, 1, 1, CURDATE(), 'assigned'),
(2, 2, 2, 2, CURDATE(), 'assigned'),
(3, 3, 3, 3, CURDATE(), 'assigned'),
(4, 4, 4, 4, CURDATE(), 'assigned'),
(5, 5, 1, 2, CURDATE(), 'assigned'),
(6, 6, 2, 1, CURDATE(), 'assigned')
ON DUPLICATE KEY UPDATE status=VALUES(status);

-- ------------------------------------------------------------------------------
-- 9. BOOKINGS & SEAT ALLOCATIONS
-- ------------------------------------------------------------------------------
-- Booking 1: Confirmed booking for Rahul Sharma (Schedule 1, 2 seats: Seat 12, 13)
INSERT INTO bookings (booking_id, booking_reference, user_id, schedule_id, source_stop_id, destination_stop_id, booking_date, journey_date, total_passengers, total_amount, booking_status)
VALUES
(1, 'AMT-BK-202610-001', 2, 1, 1, 5, NOW(), CURDATE(), 2, 50.00, 'confirmed')
ON DUPLICATE KEY UPDATE total_amount=VALUES(total_amount);

INSERT INTO booking_seats (booking_seat_id, booking_id, schedule_id, seat_number, passenger_name, passenger_age, passenger_gender, fare, status)
VALUES
(1, 1, 1, 12, 'Rahul Sharma', 24, 'male', 25.00, 'booked'),
(2, 1, 1, 13, 'Sunil Sharma', 28, 'male', 25.00, 'booked')
ON DUPLICATE KEY UPDATE passenger_name=VALUES(passenger_name);

-- Booking 2: Confirmed booking for Priya Patil (Schedule 1, 1 seat: Seat 5)
INSERT INTO bookings (booking_id, booking_reference, user_id, schedule_id, source_stop_id, destination_stop_id, booking_date, journey_date, total_passengers, total_amount, booking_status)
VALUES
(2, 'AMT-BK-202610-002', 3, 1, 2, 5, NOW(), CURDATE(), 1, 25.00, 'confirmed')
ON DUPLICATE KEY UPDATE total_amount=VALUES(total_amount);

INSERT INTO booking_seats (booking_seat_id, booking_id, schedule_id, seat_number, passenger_name, passenger_age, passenger_gender, fare, status)
VALUES
(3, 2, 1, 5, 'Priya Patil', 22, 'female', 25.00, 'booked')
ON DUPLICATE KEY UPDATE passenger_name=VALUES(passenger_name);

-- Booking 3: Cancelled demo booking for Amit Deshmukh
INSERT INTO bookings (booking_id, booking_reference, user_id, schedule_id, source_stop_id, destination_stop_id, booking_date, journey_date, total_passengers, total_amount, booking_status, cancellation_reason, cancelled_at)
VALUES
(3, 'AMT-BK-202610-003', 4, 2, 1, 4, DATE_SUB(NOW(), INTERVAL 2 HOUR), CURDATE(), 1, 20.00, 'cancelled', 'Change of travel plan', NOW())
ON DUPLICATE KEY UPDATE booking_status=VALUES(booking_status);

INSERT INTO booking_seats (booking_seat_id, booking_id, schedule_id, seat_number, passenger_name, passenger_age, passenger_gender, fare, status)
VALUES
(4, 3, 2, 8, 'Amit Deshmukh', 29, 'male', 20.00, 'cancelled')
ON DUPLICATE KEY UPDATE status=VALUES(status);

-- ------------------------------------------------------------------------------
-- 10. TICKETS
-- ------------------------------------------------------------------------------
INSERT INTO tickets (ticket_id, ticket_number, booking_id, qr_code_data, issued_at, status)
VALUES
(1, 'TKT-AMT-101-001', 1, 'AMT-TKT-REF-AMT-BK-202610-001-S1-SEATS-12-13', NOW(), 'valid'),
(2, 'TKT-AMT-101-002', 2, 'AMT-TKT-REF-AMT-BK-202610-002-S1-SEATS-5', NOW(), 'valid')
ON DUPLICATE KEY UPDATE status=VALUES(status);

-- ------------------------------------------------------------------------------
-- 11. PAYMENTS (Academic simulation payment records)
-- ------------------------------------------------------------------------------
INSERT INTO payments (payment_id, payment_reference, booking_id, amount, payment_method, transaction_status, payment_date, notes)
VALUES
(1, 'PAY-UPI-202610-9901', 1, 50.00, 'DEMO_UPI', 'success', NOW(), 'Demo UPI Transaction via GPay/PhonePe'),
(2, 'PAY-CARD-202610-9902', 2, 25.00, 'DEMO_CARD', 'success', NOW(), 'Demo Rupay/Visa Card Transaction'),
(3, 'PAY-UPI-202610-9903', 3, 20.00, 'DEMO_UPI', 'refunded', DATE_SUB(NOW(), INTERVAL 1 HOUR), 'Demo Cancellation Refund Initiated')
ON DUPLICATE KEY UPDATE notes=VALUES(notes);

-- ------------------------------------------------------------------------------
-- 12. AUDIT LOGS
-- ------------------------------------------------------------------------------
INSERT INTO audit_logs (log_id, user_id, action, table_name, record_id, details, ip_address)
VALUES
(1, 1, 'SYSTEM_INIT', 'system', NULL, 'City bus management database initialized with sample data', '127.0.0.1'),
(2, 2, 'BOOKING_CREATE', 'bookings', 1, 'Passenger Rahul Sharma booked 2 seats on Schedule 1', '127.0.0.1'),
(3, 4, 'BOOKING_CANCEL', 'bookings', 3, 'Booking cancelled by Amit Deshmukh: Change of travel plan', '127.0.0.1')
ON DUPLICATE KEY UPDATE details=VALUES(details);
