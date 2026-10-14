-- ==============================================================================
-- City Bus Management System for Amravati (Maharashtra, India)
-- MASTER SETUP SCRIPT
-- Run this in MySQL Workbench or MySQL Command Line to set up the full database.
-- ==============================================================================
-- HOW TO RUN:
-- Option A (MySQL Workbench):
--   1. Open MySQL Workbench → Connect to your server
--   2. File → Open SQL Script → Select this file (setup_database.sql)
--   3. Click the lightning bolt (Execute) button
--
-- Option B (MySQL Command Line / Terminal):
--   mysql -u root -p < database/setup_database.sql
--
-- Option C (MySQL CLI, step by step):
--   mysql -u root -p
--   SOURCE C:/path/to/CityBusManagementSystem/database/setup_database.sql;
-- ==============================================================================

-- Load Schema
SOURCE schema.sql;

-- Load Sample/Demo Data
SOURCE sample_data.sql;

-- Load Database Views
SOURCE views.sql;

-- Load Stored Procedures
SOURCE procedures.sql;

-- Load Triggers
SOURCE triggers.sql;

-- Confirmation
SELECT 'Database setup complete! city_bus_db is ready.' AS status;
SELECT table_name, table_rows 
FROM information_schema.tables 
WHERE table_schema = 'city_bus_db' 
ORDER BY table_name;
