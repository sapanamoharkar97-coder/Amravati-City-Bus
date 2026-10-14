-- ==============================================================================
-- Project: City Bus Management System for Amravati (Maharashtra, India)
-- Database Name: city_bus_db
-- Description: DDL Schema creation script with normalized 3NF tables,
--              Primary Keys, Foreign Keys, Unique Keys, Checks, and Indexes.
-- Compatible with MySQL 8.x, MySQL Workbench, and MySQL CLI.
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS city_bus_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE city_bus_db;

-- ------------------------------------------------------------------------------
-- 1. Table: users
-- Core authentication table for administrators and passengers.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'passenger') NOT NULL DEFAULT 'passenger',
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_role (role),
    INDEX idx_user_email (email)
) ENGINE=InnoDB;

-- ------------------------------------------------------------------------------
-- 2. Table: passengers
-- Extended profile data for passenger users (1:1 with users table).
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS passengers (
    passenger_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    gender ENUM('male', 'female', 'other') DEFAULT 'other',
    age INT CHECK (age >= 1 AND age <= 120),
    address VARCHAR(255),
    city VARCHAR(50) DEFAULT 'Amravati',
    emergency_contact VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_passengers_user FOREIGN KEY (user_id)
        REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------------------------
-- 3. Table: drivers
-- Driver records and state management.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS drivers (
    driver_id INT AUTO_INCREMENT PRIMARY KEY,
    license_number VARCHAR(50) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    experience_years INT NOT NULL DEFAULT 1 CHECK (experience_years >= 0),
    status ENUM('active', 'on_leave', 'inactive') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_driver_status (status)
) ENGINE=InnoDB;

-- ------------------------------------------------------------------------------
-- 4. Table: conductors
-- Conductor records and credentials.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS conductors (
    conductor_id INT AUTO_INCREMENT PRIMARY KEY,
    badge_number VARCHAR(50) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    status ENUM('active', 'on_leave', 'inactive') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_conductor_status (status)
) ENGINE=InnoDB;

-- ------------------------------------------------------------------------------
-- 5. Table: buses
-- Bus fleet assets.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS buses (
    bus_id INT AUTO_INCREMENT PRIMARY KEY,
    bus_number VARCHAR(30) NOT NULL UNIQUE,
    registration_number VARCHAR(30) NOT NULL UNIQUE,
    bus_type ENUM('Ordinary', 'CNG Express', 'Electric AC', 'Mini Bus') NOT NULL DEFAULT 'Ordinary',
    capacity INT NOT NULL CHECK (capacity BETWEEN 10 AND 100),
    status ENUM('active', 'maintenance', 'retired') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_bus_status (status),
    INDEX idx_bus_type (bus_type)
) ENGINE=InnoDB;

-- ------------------------------------------------------------------------------
-- 6. Table: bus_stops
-- Amravati city transit stops / halts.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bus_stops (
    stop_id INT AUTO_INCREMENT PRIMARY KEY,
    stop_name VARCHAR(100) NOT NULL UNIQUE,
    landmark VARCHAR(150),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    city VARCHAR(50) NOT NULL DEFAULT 'Amravati',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_stop_name (stop_name)
) ENGINE=InnoDB;

-- ------------------------------------------------------------------------------
-- 7. Table: bus_routes
-- Transit corridors linking source and destination stops.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bus_routes (
    route_id INT AUTO_INCREMENT PRIMARY KEY,
    route_number VARCHAR(30) NOT NULL UNIQUE,
    route_name VARCHAR(150) NOT NULL,
    start_stop_id INT NOT NULL,
    end_stop_id INT NOT NULL,
    total_distance_km DECIMAL(6, 2) NOT NULL CHECK (total_distance_km > 0),
    estimated_duration_mins INT NOT NULL CHECK (estimated_duration_mins > 0),
    base_fare DECIMAL(8, 2) NOT NULL DEFAULT 10.00 CHECK (base_fare >= 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_route_start_stop FOREIGN KEY (start_stop_id)
        REFERENCES bus_stops (stop_id) ON UPDATE CASCADE,
    CONSTRAINT fk_route_end_stop FOREIGN KEY (end_stop_id)
        REFERENCES bus_stops (stop_id) ON UPDATE CASCADE,
    INDEX idx_route_number (route_number)
) ENGINE=InnoDB;

-- ------------------------------------------------------------------------------
-- 8. Table: route_stops
-- Many-to-many relationship defining ordered halts, distances, and fares.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS route_stops (
    route_stop_id INT AUTO_INCREMENT PRIMARY KEY,
    route_id INT NOT NULL,
    stop_id INT NOT NULL,
    stop_sequence INT NOT NULL CHECK (stop_sequence >= 1),
    distance_from_source_km DECIMAL(6, 2) NOT NULL DEFAULT 0.00 CHECK (distance_from_source_km >= 0),
    fare_from_source DECIMAL(8, 2) NOT NULL DEFAULT 0.00 CHECK (fare_from_source >= 0),
    halt_duration_mins INT NOT NULL DEFAULT 2 CHECK (halt_duration_mins >= 0),
    CONSTRAINT fk_route_stops_route FOREIGN KEY (route_id)
        REFERENCES bus_routes (route_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_route_stops_stop FOREIGN KEY (stop_id)
        REFERENCES bus_stops (stop_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    UNIQUE KEY uk_route_sequence (route_id, stop_sequence),
    UNIQUE KEY uk_route_stop (route_id, stop_id),
    INDEX idx_route_stop_order (route_id, stop_sequence)
) ENGINE=InnoDB;

-- ------------------------------------------------------------------------------
-- 9. Table: schedules
-- Operational bus timetable linked to route, bus, date, and time.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS schedules (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    route_id INT NOT NULL,
    bus_id INT NOT NULL,
    departure_time TIME NOT NULL,
    arrival_time TIME NOT NULL,
    journey_date DATE NOT NULL,
    fare DECIMAL(8, 2) NOT NULL CHECK (fare > 0),
    frequency ENUM('daily', 'weekdays', 'weekends', 'custom') NOT NULL DEFAULT 'daily',
    status ENUM('scheduled', 'in_transit', 'completed', 'cancelled') NOT NULL DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_schedules_route FOREIGN KEY (route_id)
        REFERENCES bus_routes (route_id) ON UPDATE CASCADE,
    CONSTRAINT fk_schedules_bus FOREIGN KEY (bus_id)
        REFERENCES buses (bus_id) ON UPDATE CASCADE,
    INDEX idx_schedule_date (journey_date),
    INDEX idx_schedule_status (status),
    INDEX idx_schedule_route (route_id, journey_date)
) ENGINE=InnoDB;

-- ------------------------------------------------------------------------------
-- 10. Table: staff_assignments
-- Crew assignment (Driver + Conductor) per bus schedule.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS staff_assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    schedule_id INT NOT NULL UNIQUE,
    driver_id INT NOT NULL,
    conductor_id INT NOT NULL,
    assigned_date DATE NOT NULL,
    status ENUM('assigned', 'completed', 'reassigned') NOT NULL DEFAULT 'assigned',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_assignment_schedule FOREIGN KEY (schedule_id)
        REFERENCES schedules (schedule_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_assignment_driver FOREIGN KEY (driver_id)
        REFERENCES drivers (driver_id) ON UPDATE CASCADE,
    CONSTRAINT fk_assignment_conductor FOREIGN KEY (conductor_id)
        REFERENCES conductors (conductor_id) ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------------------------
-- 11. Table: bookings
-- Master booking record created by passenger for a journey.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_reference VARCHAR(30) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    schedule_id INT NOT NULL,
    source_stop_id INT NOT NULL,
    destination_stop_id INT NOT NULL,
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    journey_date DATE NOT NULL,
    total_passengers INT NOT NULL CHECK (total_passengers >= 1),
    total_amount DECIMAL(10, 2) NOT NULL CHECK (total_amount >= 0),
    booking_status ENUM('pending', 'confirmed', 'cancelled') NOT NULL DEFAULT 'confirmed',
    cancellation_reason VARCHAR(255) NULL,
    cancelled_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_bookings_user FOREIGN KEY (user_id)
        REFERENCES users (user_id) ON UPDATE CASCADE,
    CONSTRAINT fk_bookings_schedule FOREIGN KEY (schedule_id)
        REFERENCES schedules (schedule_id) ON UPDATE CASCADE,
    CONSTRAINT fk_bookings_source_stop FOREIGN KEY (source_stop_id)
        REFERENCES bus_stops (stop_id) ON UPDATE CASCADE,
    CONSTRAINT fk_bookings_dest_stop FOREIGN KEY (destination_stop_id)
        REFERENCES bus_stops (stop_id) ON UPDATE CASCADE,
    INDEX idx_booking_user (user_id),
    INDEX idx_booking_schedule (schedule_id),
    INDEX idx_booking_status (booking_status)
) ENGINE=InnoDB;

-- ------------------------------------------------------------------------------
-- 12. Table: booking_seats
-- Specific individual seat allocations for each passenger in a booking.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS booking_seats (
    booking_seat_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    schedule_id INT NOT NULL,
    seat_number INT NOT NULL CHECK (seat_number >= 1),
    passenger_name VARCHAR(100) NOT NULL,
    passenger_age INT NOT NULL CHECK (passenger_age BETWEEN 1 AND 120),
    passenger_gender ENUM('male', 'female', 'other') NOT NULL,
    fare DECIMAL(8, 2) NOT NULL CHECK (fare >= 0),
    status ENUM('booked', 'cancelled') NOT NULL DEFAULT 'booked',
    CONSTRAINT fk_booking_seats_booking FOREIGN KEY (booking_id)
        REFERENCES bookings (booking_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_booking_seats_schedule FOREIGN KEY (schedule_id)
        REFERENCES schedules (schedule_id) ON UPDATE CASCADE,
    INDEX idx_booking_seats_schedule (schedule_id, seat_number, status)
) ENGINE=InnoDB;

-- ------------------------------------------------------------------------------
-- 13. Table: tickets
-- Ticket artifact generated once a booking is confirmed.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_number VARCHAR(40) NOT NULL UNIQUE,
    booking_id INT NOT NULL UNIQUE,
    qr_code_data VARCHAR(255) NOT NULL,
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('valid', 'used', 'cancelled') NOT NULL DEFAULT 'valid',
    CONSTRAINT fk_tickets_booking FOREIGN KEY (booking_id)
        REFERENCES bookings (booking_id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_ticket_number (ticket_number)
) ENGINE=InnoDB;

-- ------------------------------------------------------------------------------
-- 14. Table: payments
-- Demonstration payment transaction records linked to bookings.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    payment_reference VARCHAR(50) NOT NULL UNIQUE,
    booking_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL CHECK (amount >= 0),
    payment_method ENUM('DEMO_UPI', 'DEMO_CARD', 'DEMO_CASH', 'DEMO_NETBANKING') NOT NULL DEFAULT 'DEMO_UPI',
    transaction_status ENUM('success', 'pending', 'failed', 'refunded') NOT NULL DEFAULT 'success',
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes VARCHAR(255) DEFAULT 'Fictional Academic Simulation Payment',
    CONSTRAINT fk_payments_booking FOREIGN KEY (booking_id)
        REFERENCES bookings (booking_id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_payment_booking (booking_id),
    INDEX idx_payment_status (transaction_status)
) ENGINE=InnoDB;

-- ------------------------------------------------------------------------------
-- 15. Table: audit_logs
-- Tracks administrative actions, booking status changes, and critical operations.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(50) NOT NULL,
    record_id INT NULL,
    details TEXT,
    ip_address VARCHAR(45) DEFAULT '127.0.0.1',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_user FOREIGN KEY (user_id)
        REFERENCES users (user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_audit_action (action),
    INDEX idx_audit_created_at (created_at)
) ENGINE=InnoDB;
