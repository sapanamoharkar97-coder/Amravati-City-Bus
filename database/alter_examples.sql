-- ==============================================================================
-- Project: City Bus Management System for Amravati
-- File: alter_examples.sql
-- Description: Educational and practical ALTER TABLE demonstrations for MySQL 8.x.
--              Includes column additions, modifications, renames, index operations,
--              constraint modifications, and data backfill queries.
--
-- NOTE: These queries are for demonstration, schema evolution, and DBMS viva.
-- They are NOT automatically executed during application setup.
-- ==============================================================================

USE city_bus_db;

-- ------------------------------------------------------------------------------
-- 1. ADDING A COLUMN
-- Example: Add a wheelchair accessibility flag to the buses table
-- ------------------------------------------------------------------------------
-- Query:
ALTER TABLE buses 
ADD COLUMN is_wheelchair_accessible BOOLEAN NOT NULL DEFAULT FALSE 
AFTER capacity;

-- Backfill / Update records after adding column:
UPDATE buses 
SET is_wheelchair_accessible = TRUE 
WHERE bus_type IN ('Electric AC', 'CNG Express');

-- Verify change:
-- DESCRIBE buses;
-- SELECT bus_id, bus_number, capacity, is_wheelchair_accessible FROM buses;


-- ------------------------------------------------------------------------------
-- 2. MODIFYING A COLUMN
-- Example: Expand passenger emergency contact phone field to support international formats
-- ------------------------------------------------------------------------------
ALTER TABLE passengers 
MODIFY COLUMN emergency_contact VARCHAR(30) NULL;


-- ------------------------------------------------------------------------------
-- 3. RENAMING A COLUMN (MySQL 8.x standard syntax)
-- Example: Rename notes to remarks in payments table
-- ------------------------------------------------------------------------------
ALTER TABLE payments 
RENAME COLUMN notes TO remarks;

-- Revert back to maintain application compatibility:
ALTER TABLE payments 
RENAME COLUMN remarks TO notes;


-- ------------------------------------------------------------------------------
-- 4. CREATING AND DROPPING AN INDEX
-- Example: Optimize searches on schedules by departure time
-- ------------------------------------------------------------------------------
-- Create new non-unique composite index:
CREATE INDEX idx_schedule_time_status 
ON schedules (departure_time, status);

-- Drop the created index safely when no longer needed:
DROP INDEX idx_schedule_time_status 
ON schedules;


-- ------------------------------------------------------------------------------
-- 5. ADDING AND DROPPING A CHECK CONSTRAINT (MySQL 8.0.16+)
-- Example: Ensure bus fare cannot be set below minimum threshold of Rs 5.00
-- ------------------------------------------------------------------------------
ALTER TABLE bus_routes 
ADD CONSTRAINT chk_min_base_fare 
CHECK (base_fare >= 5.00);

-- Drop the constraint if fares policy changes:
ALTER TABLE bus_routes 
DROP CHECK chk_min_base_fare;


-- ------------------------------------------------------------------------------
-- 6. ADDING AND DROPPING A FOREIGN KEY (Safe migration practice)
-- ------------------------------------------------------------------------------
-- Example: Adding optional preferred bus stop reference to passengers table
ALTER TABLE passengers 
ADD COLUMN preferred_stop_id INT NULL,
ADD CONSTRAINT fk_passenger_pref_stop 
FOREIGN KEY (preferred_stop_id) REFERENCES bus_stops (stop_id) 
ON DELETE SET NULL ON UPDATE CASCADE;

-- Safely remove foreign key and column if reverting:
ALTER TABLE passengers 
DROP FOREIGN KEY fk_passenger_pref_stop;

ALTER TABLE passengers 
DROP COLUMN preferred_stop_id;


-- ------------------------------------------------------------------------------
-- 7. CLEANUP / REVERT FOR ALTER SAMPLES
-- (Revert wheelchair column if test environment needs original schema)
-- ------------------------------------------------------------------------------
-- ALTER TABLE buses DROP COLUMN is_wheelchair_accessible;
