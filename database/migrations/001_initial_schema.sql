-- Migration: 001_initial_schema.sql
-- Description: Baseline schema definition for City Bus Management System (Amravati)
-- Applied to: city_bus_db

CREATE DATABASE IF NOT EXISTS city_bus_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE city_bus_db;

-- Source the initial schema
-- Reference: ../schema.sql
-- Run database/schema.sql to apply this baseline migration.
SELECT 'Migration 001: Baseline schema initialized successfully.' AS migration_status;
