-- ==============================================================================
-- Project: City Bus Management System for Amravati
-- File: reset_demo_data.sql
-- ==============================================================================
-- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
-- WARNING: DESTRUCTIVE MANUAL OPERATION
-- This script safely truncates/deletes transactional demo data in city_bus_db.
-- It resets bookings, booking seats, tickets, payments, staff assignments,
-- schedules, and audit logs while preserving master routes, stops, buses,
-- and administrative user accounts.
-- 
-- DO NOT RUN AUTOMATICALLY IN PRODUCTION OR DURING BACKEND STARTUP.
-- To execute manually in MySQL Workbench or MySQL CLI:
-- 1. Ensure you have taken a backup if you need existing booking records.
-- 2. Open this file in MySQL Workbench.
-- 3. Execute queries sequentially or run the full script.
-- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

USE city_bus_db;

-- Temporarily disable foreign key checks to allow safe child-parent cleanup
SET @OLD_FOREIGN_KEY_CHECKS = @@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS = 0;

-- Clean transactional and dynamic operational tables
TRUNCATE TABLE payments;
TRUNCATE TABLE tickets;
TRUNCATE TABLE booking_seats;
TRUNCATE TABLE bookings;
TRUNCATE TABLE staff_assignments;
TRUNCATE TABLE audit_logs;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = @OLD_FOREIGN_KEY_CHECKS;

-- Insert audit record recording the manual reset
INSERT INTO audit_logs (user_id, action, table_name, details, ip_address)
VALUES (1, 'MANUAL_DEMO_RESET', 'all_transactional', 'Transactional demo records reset via reset_demo_data.sql', '127.0.0.1');

SELECT 'city_bus_db demo transactional records successfully reset. Master buses, stops, and routes preserved.' AS status_message;
