# Direct MySQL Database Maintenance & Administration Guide
## City Bus Management System for Amravati (`city_bus_db`)

This guide explains how to manage, inspect, edit, back up, and restore the **`city_bus_db`** database directly using **MySQL Workbench** or the **MySQL Command Line Client**.

---

## 1. Connecting via MySQL Workbench

1. Launch **MySQL Workbench** from your Windows Start Menu.
2. In the home tab, click on your local connection tile (e.g. `Local instance MySQL80` or `127.0.0.1:3306`).
3. Enter your MySQL root password (as configured during MySQL Server installation).
4. In the left **Navigator** pane, expand the **Schemas** tab.
5. Double-click **`city_bus_db`** (the schema name will become bold, indicating it is the active default database).
6. Press `Ctrl + T` to open a new SQL Query Editor tab.

---

## 2. Inspecting Tables and Running Direct SQL Queries

In your query editor tab, execute the following fundamental inspection statements:

```sql
USE city_bus_db;

-- 1. Check all tables in the database
SHOW TABLES;

-- 2. Inspect table structure, columns, and constraints
DESCRIBE buses;
DESCRIBE schedules;
DESCRIBE bookings;

-- 3. View exact DDL and foreign keys of a table
SHOW CREATE TABLE route_stops;

-- 4. Check active records
SELECT * FROM buses;
SELECT * FROM bus_routes;
SELECT * FROM schedules;
```

---

## 3. Direct Record Editing (CRUD Operations)

### 3.1 Inserting a New Record
```sql
USE city_bus_db;

INSERT INTO buses (bus_number, registration_number, bus_type, capacity, status)
VALUES ('BUS-DEMO-99', 'MH-27-TEST-999', 'Electric AC', 35, 'active');

-- Verify insertion:
SELECT * FROM buses WHERE bus_number = 'BUS-DEMO-99';
```

### 3.2 Updating a Record Safely
> [!IMPORTANT]
> **Understanding `SQL_SAFE_UPDATES`**:  
> MySQL Workbench has Safe Updates enabled by default. If you attempt an `UPDATE` without specifying a Primary Key in the `WHERE` clause, Workbench will block the query with error code 1175.
> Always target the row using its Primary Key (`bus_id`):

```sql
-- Safe update targeting primary key:
UPDATE buses
SET capacity = 40,
    status = 'active'
WHERE bus_id = 1;

-- Verify updated capacity:
SELECT bus_id, bus_number, capacity, status FROM buses WHERE bus_id = 1;
```

If you ever need to perform a batch update across multiple non-key rows, make it safe by including a primary key range or temporary session toggle:
```sql
SET SQL_SAFE_UPDATES = 0;
UPDATE buses SET status = 'active' WHERE status = 'maintenance';
SET SQL_SAFE_UPDATES = 1;
```

### 3.3 Deleting Records & Foreign Key Safety
> [!WARNING]
> Before deleting a row, check whether other tables reference its Primary Key!  
> For example, deleting a bus from `buses` that has active references in `schedules` will trigger:  
> `Error 1451: Cannot delete or update a parent row: a foreign key constraint fails`

```sql
-- 1. Check if the bus has any schedule dependencies:
SELECT COUNT(*) FROM schedules WHERE bus_id = 8;

-- 2. If count is 0, safe deletion can proceed:
DELETE FROM buses
WHERE bus_id = 8;
```

---

## 4. Testing Live Synchronization: Workbench &rarr; Web Application

Follow these steps to demonstrate that changes made directly in MySQL Workbench appear immediately in the running application:

1. Open **MySQL Workbench** and execute:
   ```sql
   USE city_bus_db;
   UPDATE buses 
   SET capacity = 48, bus_type = 'CNG Express' 
   WHERE bus_id = 3;
   ```
2. Open your web browser and navigate to `http://127.0.0.1:5000/buses.html`.
3. Notice that Bus #3 immediately displays **48 seats** and **CNG Express**!
4. **Why this works:** The Flask REST API does not cache records in memory. Every HTTP request executes a live parameterized query against the MySQL database.

---

## 5. Safe Transactions & Rollback Practices

When executing multi-statement operations manually, wrap your queries in an explicit transaction:

```sql
START TRANSACTION;

-- Perform operations:
UPDATE schedules SET fare = fare + 5.00 WHERE route_id = 1;
SELECT schedule_id, fare FROM schedules WHERE route_id = 1;

-- If satisfied with the outcome:
COMMIT;

-- If a mistake was made BEFORE committing:
-- ROLLBACK;
```

> [!CAUTION]
> **Transaction Durability Rule:**  
> Once `COMMIT` is executed, `ROLLBACK` **cannot** undo the changes. Furthermore, DDL statements (`CREATE TABLE`, `ALTER TABLE`, `DROP TABLE`, `TRUNCATE`) trigger an **implicit commit** in MySQL and cannot be rolled back!

---

## 6. Database Backup Procedures

### Method A: Using MySQL Workbench (GUI Export)
1. In MySQL Workbench, click **Server** &rarr; **Data Export** from the top menu.
2. In the left pane, check **`city_bus_db`**.
3. Under *Export Options*, select **Export to Self-Contained File**.
4. Choose a destination path, e.g. `C:\Users\Balaji\Desktop\city_bus_db_backup.sql`.
5. Under *Dump Options*, select **Dump Structure and Data**.
6. Click **Start Export**.

### Method B: Using Windows PowerShell (`mysqldump`)
Open PowerShell as an Administrator or standard user with MySQL bin on PATH:

```powershell
# Backup database structure and all records
mysqldump -u root -p city_bus_db > city_bus_db_backup.sql

# Backup only schema definitions (no records)
mysqldump -u root -p --no-data city_bus_db > city_bus_db_schema_only.sql
```

---

## 7. Database Restoration Procedures

### Method A: Using MySQL Workbench
1. In MySQL Workbench, click **Server** &rarr; **Data Import**.
2. Select **Import from Self-Contained File** and choose your `.sql` backup.
3. Select `city_bus_db` as the *Default Target Schema*.
4. Click **Start Import**.

### Method B: Using PowerShell / MySQL CLI
```powershell
# Restore entire database from backup file
mysql -u root -p city_bus_db < city_bus_db_backup.sql
```

---

## 8. Recovering from Accidental Data Loss

If records are deleted accidentally:
1. **Do not run `schema.sql` again over existing data**, as it may drop or conflict with current tables.
2. Check your latest backup file taken before the incident.
3. If only demo test data was corrupted, you can execute [`database/sample_data.sql`](file:///C:/Users/Balaji/.gemini/antigravity/scratch/CityBusManagementSystem/database/sample_data.sql) or use [`database/reset_demo_data.sql`](file:///C:/Users/Balaji/.gemini/antigravity/scratch/CityBusManagementSystem/database/reset_demo_data.sql) to re-seed clean baseline demo records.
