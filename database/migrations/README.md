# Database Migrations Guide

## Overview
This directory tracks version-controlled SQL migration scripts for the **City Bus Management System for Amravati (`city_bus_db`)**.

In real-world engineering and DBMS projects, manual `ALTER TABLE` statements applied directly to production environments risk data loss and inconsistencies. Migrations provide an ordered, reproducible ledger of changes to database structure and reference data.

## Migration Naming Convention
Migrations follow sequential zero-padded prefixes:
```
<version_number>_<description>.sql
```
Examples:
- `001_initial_schema.sql` - Base DDL creating core tables and constraints.
- `002_add_accessibility_feature.sql` - Adding `is_wheelchair_accessible` to buses.
- `003_add_cancellation_refund_column.sql` - Adding refund reference to payments.

## How to Apply Migrations

### 1. In MySQL Workbench
1. Open MySQL Workbench and connect to `localhost:3306`.
2. Open File -> Open SQL Script (`Ctrl + O`).
3. Select the next unapplied migration file in numerical sequence.
4. Execute with `Ctrl + Shift + Enter`.

### 2. In MySQL Command Line Client / PowerShell
```powershell
mysql -u root -p city_bus_db < database\migrations\001_initial_schema.sql
```

## Migration Safety Rules
1. **Never alter an already applied migration**: Create a new sequentially numbered script to amend changes.
2. **Always backup before executing schema changes**:
   ```powershell
   mysqldump -u root -p city_bus_db > backup_before_migration.sql
   ```
3. **Use transactions for DDL where supported** or test scripts on a local staging database first.
4. **Update Backend Models**: Whenever a column is added or modified in a migration, update:
   - Corresponding Flask route query or serializer (`backend/routes/`).
   - Frontend HTML table headers/forms (`frontend/`).
   - JavaScript data binding (`frontend/js/`).
