# Comprehensive DBMS Viva Voce Guide & Practical SQL Queries
## City Bus Management System for Amravati

This guide prepares engineering students for university oral examinations, viva voce, project defense, and technical interviews.

---

## Part 1: 35 Core DBMS & Architectural Viva Questions

### 1. What is a DBMS, and why did you choose MySQL 8.x for this system?
**Answer:** A Database Management System (DBMS) is software that facilitates defining, creating, querying, and managing relational data while enforcing integrity constraints and concurrency control. MySQL 8.x was selected because:
- It supports the **InnoDB storage engine**, providing true ACID transactions and row-level locking.
- It provides native SQL:2016 features including Window Functions, Common Table Expressions (CTEs), and supported `CHECK` constraints.
- It offers high throughput, mature connection pooling, and universal compatibility with tools like MySQL Workbench and Python drivers.

### 2. What is a Primary Key? Identify three in your project.
**Answer:** A Primary Key (PK) is a minimal set of one or more attributes that uniquely identifies every tuple in a relation. It enforces both uniqueness and non-nullity (`NOT NULL`).
- `user_id` in `users`
- `bus_id` in `buses`
- `schedule_id` in `schedules`

### 3. What is a Foreign Key, and what referential actions did you implement?
**Answer:** A Foreign Key (FK) is an attribute in a child table whose values must match the candidate/primary key of a parent table or be null, maintaining referential integrity.
- `ON DELETE CASCADE`: Used between `bookings` and `booking_seats`, so deleting a booking removes its seats.
- `ON DELETE RESTRICT`: Used in `route_stops.stop_id` referencing `bus_stops.stop_id`, preventing accidental deletion of a bus stop while active transit routes still use it.
- `ON DELETE SET NULL`: Used in `audit_logs.user_id`, so administrative history is preserved even if a user account is removed.

### 4. What is a Candidate Key? Give an example from your database.
**Answer:** A Candidate Key is an attribute or minimal set of attributes that satisfies uniqueness and non-nullity, making it eligible to be chosen as the primary key. In our `buses` table:
- `bus_id` is chosen as the synthetic Primary Key.
- `bus_number` and `registration_number` are Candidate Keys enforced by `UNIQUE` constraints.

### 5. What is a Composite Key? Where is it applied in your schema?
**Answer:** A Composite Key consists of two or more columns that together guarantee uniqueness. In `route_stops`, the composite candidate key `(route_id, stop_sequence)` prevents two stops on the same route from having the exact same stop sequence order.

### 6. What is Database Normalization and why is it necessary?
**Answer:** Normalization is the systematic decomposition of relations to minimize data redundancy and eliminate update, insertion, and deletion anomalies.

### 7. Explain First Normal Form (1NF) with respect to your schema.
**Answer:** A relation is in 1NF if every attribute contains only atomic (indivisible) values, and there are no repeating groups. In our project, passenger seat numbers are not stored as a comma-separated string like `"12, 13"` in `bookings`. Instead, each seat has a distinct row in `booking_seats`.

### 8. Explain Second Normal Form (2NF) with respect to your schema.
**Answer:** A relation is in 2NF if it is in 1NF and contains no partial dependencies (every non-prime attribute depends on the whole candidate key, not a proper subset). In `route_stops`, attributes `fare_from_source` and `distance_from_source_km` depend on the composite pair `(route_id, stop_sequence)` together.

### 9. Explain Third Normal Form (3NF) with respect to your schema.
**Answer:** A relation is in 3NF if it is in 2NF and contains no transitive dependencies (non-prime attributes must not depend on other non-prime attributes). For example, passenger demographics (`age`, `gender`, `address`) are stored in `passengers`, not duplicated in `bookings`. `bookings` only stores `user_id`.

### 10. What is Boyce-Codd Normal Form (BCNF)?
**Answer:** BCNF is a stricter version of 3NF stating that for every functional dependency $X \rightarrow Y$, $X$ must be a superkey. In our design, all determinants (such as `username`, `email`, `bus_number`) are superkeys enforced by unique constraints.

### 11. What are ACID properties? How do they apply to bus seat booking?
**Answer:**
- **Atomicity:** All-or-nothing execution. When booking 2 seats, either both seats, the ticket, and payment record are inserted, or none are.
- **Consistency:** Database transitions from one valid state to another, respecting seat capacity, unique constraints, and foreign keys.
- **Isolation:** Concurrent booking attempts execute independently without dirty reads or phantom updates via row locks (`FOR UPDATE`).
- **Durability:** Once committed, seat bookings and financial logs persist even across power failures or crashes.

### 12. How did you prevent double booking / race conditions during seat selection?
**Answer:** In `backend/services/booking_service.py`, we execute a transaction with pessimistic row-level locking:
```sql
SELECT s.schedule_id, b.capacity 
FROM schedules s 
JOIN buses b ON s.bus_id = b.bus_id 
WHERE s.schedule_id = %s FOR UPDATE;
```
Following this, we lock and inspect existing bookings:
```sql
SELECT seat_number 
FROM booking_seats 
WHERE schedule_id = %s AND status = 'booked' AND seat_number IN (...) FOR UPDATE;
```
If any seat is already booked, the transaction raises an exception and rolls back immediately, guaranteeing that two concurrent users cannot reserve the same seat.

### 13. What is the difference between Pessimistic Locking and Optimistic Locking?
**Answer:**
- **Pessimistic Locking:** Locks database rows immediately using `SELECT ... FOR UPDATE` before writing, preventing other transactions from modifying them until commit. Ideal for high-contention scenarios like seat reservations.
- **Optimistic Locking:** Allows reads without locks and checks a version number or timestamp before committing. If altered, the transaction aborts and retries.

### 14. What is a Database View? Mention the views in your project.
**Answer:** A View is a virtual table defined by a stored SQL query. It simplifies complex joins, enhances security by restricting raw table access, and optimizes reuse.
- `v_route_stop_details`: Joins routes and stops in sequence.
- `v_schedule_details`: Combines timetable with buses, routes, drivers, and conductors.
- `v_booking_details`: Consolidates passenger, schedule, and ticket details.
- `v_bus_occupancy`: Calculates real-time occupancy percentages per schedule.

### 15. What is a Stored Procedure? What procedures are created in `procedures.sql`?
**Answer:** A Stored Procedure is a compiled set of SQL statements stored on the database server.
- `sp_search_schedules`: Searches valid schedules between two stops for a specific date and calculates remaining seat counts.
- `sp_get_passenger_booking_history`: Returns a user's reservations, tickets, and payment statuses.
- `sp_route_revenue_summary`: Computes aggregate revenue and passenger volumes by corridor.

### 16. What is a Database Trigger? What triggers did you implement?
**Answer:** A Trigger is a procedural SQL block executed automatically in response to DML operations (`INSERT`, `UPDATE`, `DELETE`) on a table.
- `trg_after_booking_insert_audit`: Automatically inserts an audit trail entry into `audit_logs` whenever a new booking is created.
- `trg_after_booking_status_update`: Automatically synchronizes child records when a booking is cancelled: sets child seats to `'cancelled'` and invalidates tickets.
- `trg_after_bus_status_change`: Logs vehicle status modifications (e.g., active to maintenance).

### 17. What is an Index? How does it improve performance?
**Answer:** An Index is an auxiliary B-Tree data structure that enables the database engine to find tuples quickly without scanning every block in the table (Full Table Scan). We indexed `users(email)`, `buses(bus_number)`, `schedules(journey_date, route_id)`, and `booking_seats(schedule_id, seat_number, status)`.

### 18. What is the difference between Clustered and Secondary Indexes in MySQL InnoDB?
**Answer:**
- **Clustered Index:** The physical table data is sorted and stored directly in the leaf pages of the index (the Primary Key).
- **Secondary Index:** The leaf pages store the indexed column value and a pointer to the clustered index (Primary Key).

### 19. What is a SQL JOIN? Differentiate INNER JOIN and LEFT JOIN.
**Answer:**
- **INNER JOIN:** Returns only matching rows that satisfy the join condition in both tables. Example: Joining `schedules` with `bus_routes`.
- **LEFT JOIN:** Returns all rows from the left table and matching rows from the right table. If no match exists, NULL values are returned. Example: Listing all buses and their schedules (`buses LEFT JOIN schedules`).

### 20. What is a Subquery? Give an example from your project.
**Answer:** A subquery is a nested query within an outer `SELECT`, `INSERT`, `UPDATE`, or `DELETE`.
Example (correlated subquery): Calculating vacant seats directly inside the `schedules` query:
```sql
SELECT s.schedule_id, b.capacity - (
    SELECT COUNT(*) FROM booking_seats bs 
    WHERE bs.schedule_id = s.schedule_id AND bs.status = 'booked'
) AS available_seats
FROM schedules s JOIN buses b ON s.bus_id = b.bus_id;
```

### 21. What is the difference between `WHERE` and `HAVING` clauses?
**Answer:**
- `WHERE` filters individual rows **before** aggregation and grouping.
- `HAVING` filters aggregated groups **after** the `GROUP BY` clause has been computed (e.g. `HAVING SUM(b.total_amount) >= 20.00`).

### 22. What is `SQL_SAFE_UPDATES` in MySQL, and how do you handle it?
**Answer:** MySQL Workbench enables `SQL_SAFE_UPDATES` by default to prevent accidental data loss. It rejects `UPDATE` and `DELETE` statements that do not specify a key column (like the Primary Key) in the `WHERE` clause or omit a `LIMIT` clause. In our application, all updates and deletes strictly target the primary key (e.g. `WHERE bus_id = 1`).

### 23. Why did you use Werkzeug password hashing instead of storing plain text?
**Answer:** Storing plain text passwords creates severe security vulnerabilities if the database is breached. Werkzeug utilizes `pbkdf2:sha256` or `scrypt`, which combine unique cryptographic salts with computationally intensive key stretching, preventing rainbow table attacks.

### 24. How is role-based access control (RBAC) enforced?
**Answer:** We implement server-side decorators in Python (`@login_required` and `@admin_required` in `utils/decorators.py`). Even if a passenger bypasses client-side buttons, the Flask server inspects the session role and rejects unauthorized requests with HTTP 403 Forbidden.

### 25. What is a REST API?
**Answer:** Representational State Transfer (REST) is a software architectural style that uses standard HTTP methods (`GET` for retrieval, `POST` for creation, `PUT` for updates, `DELETE` for removal) to exchange JSON payloads between frontend clients and the backend server.

### 26. What happens if MySQL Server disconnects while Flask is running?
**Answer:** Our `backend/db.py` uses connection functions and context managers that handle disconnects cleanly. When a query fails, the context manager catches the exception, rolls back uncommitted transactions, logs the error, and returns a graceful HTTP 500 JSON response explaining that the MySQL server is unreachable.

### 27. How does the frontend stay synchronized with MySQL Workbench edits?
**Answer:** The frontend does not hardcode data. Every time a page is loaded or the "Refresh" button is clicked, an asynchronous JavaScript `fetch()` request calls the Flask REST endpoint, which queries MySQL live and renders the fresh records.

### 28. What is the difference between `CHAR` and `VARCHAR`?
**Answer:** `CHAR(n)` is fixed-length and pads unused spaces up to $n$ characters. `VARCHAR(n)` is variable-length and only stores the actual characters plus length prefix bytes, conserving disk space. We used `VARCHAR` for names, emails, and addresses.

### 29. Why is `DECIMAL(10,2)` used for currency instead of `FLOAT`?
**Answer:** `FLOAT` and `DOUBLE` are approximate numeric data types that introduce binary floating-point rounding errors (e.g. $0.1 + 0.2 = 0.30000000000000004$). `DECIMAL` is an exact numeric type storing exact decimal digits, essential for fares and financial ledgers.

### 30. What is an Entity-Relationship (ER) model?
**Answer:** An abstract conceptual data model describing real-world entities (e.g. Bus, Route, Passenger), their attributes (e.g. Capacity, Fare), and their structural relationships (e.g. operates, reserves).

### 31. What is referential integrity?
**Answer:** A database state where all foreign key references are valid, meaning every foreign key value either refers to an existing primary key value in the parent relation or is null.

### 32. What is a transaction log (WAL / Redo Log)?
**Answer:** In InnoDB, Write-Ahead Logging (WAL) ensures changes are recorded in the redo log on disk before data pages are flushed. If the system crashes, unwritten changes are recovered during startup, guaranteeing Durability.

### 33. How does your system support ticket printing?
**Answer:** In `tickets.html`, we utilize standard CSS `@media print` rules in `print.css` to hide headers, sidebars, and action buttons, isolating the boarding pass layout and QR verification code for clean physical printing or PDF export.

### 34. What is SQL injection, and how does your backend prevent it?
**Answer:** SQL injection occurs when malicious user input is concatenated into raw SQL strings, altering query semantics. We prevent this by using parameterized queries with `%s` placeholders across all routes, delegating parameter escaping to `mysql-connector-python`.

### 35. Can a committed transaction be undone using `ROLLBACK`?
**Answer:** No. Once a transaction issues `COMMIT`, its changes are permanent and durable on disk. Reversing the changes requires executing a compensating transaction (e.g., our cancellation flow, which issues a new update changing status to `'cancelled'`).

---

## Part 2: 10 Practical SQL Viva Voce Questions with Queries & Expected Outputs

### Query 1: Find the top 3 routes by total passenger volume
```sql
SELECT r.route_number, r.route_name, SUM(b.total_passengers) AS total_riders
FROM bus_routes r
JOIN schedules s ON r.route_id = s.route_id
JOIN bookings b ON s.schedule_id = b.schedule_id
WHERE b.booking_status = 'confirmed'
GROUP BY r.route_number, r.route_name
ORDER BY total_riders DESC
LIMIT 3;
```
**Expected Output:**
| route_number | route_name | total_riders |
|---|---|---|
| R-101 | Badnera Station to SGBAU University | 3 |

---

### Query 2: List all stops on Route R-101 in sequence order
```sql
SELECT rs.stop_sequence, s.stop_name, rs.distance_from_source_km, rs.fare_from_source
FROM route_stops rs
JOIN bus_stops s ON rs.stop_id = s.stop_id
JOIN bus_routes r ON rs.route_id = r.route_id
WHERE r.route_number = 'R-101'
ORDER BY rs.stop_sequence ASC;
```
**Expected Output:**
| stop_sequence | stop_name | distance_from_source_km | fare_from_source |
|---|---|---|---|
| 1 | Badnera Railway Station | 0.00 | 0.00 |
| 2 | Rajkamal Square | 8.50 | 15.00 |
| 3 | Irwin Hospital Chowk | 9.80 | 18.00 |
| 4 | Panchavati Square | 11.20 | 20.00 |
| 5 | Gadge Nagar (SGBAU Gate) | 14.50 | 25.00 |

---

### Query 3: Calculate total revenue collected grouped by payment method
```sql
SELECT payment_method, COUNT(payment_id) AS transactions, SUM(amount) AS total_revenue
FROM payments
WHERE transaction_status = 'success'
GROUP BY payment_method;
```
**Expected Output:**
| payment_method | transactions | total_revenue |
|---|---|---|
| DEMO_UPI | 1 | 50.00 |
| DEMO_CARD | 1 | 25.00 |

---

### Query 4: Identify buses that have NOT operated any schedules
```sql
SELECT b.bus_id, b.bus_number, b.bus_type, b.status
FROM buses b
LEFT JOIN schedules s ON b.bus_id = s.bus_id
WHERE s.schedule_id IS NULL;
```
**Expected Output:**
| bus_id | bus_number | bus_type | status |
|---|---|---|---|
| 7 | AMT-CITY-07 | CNG Express | maintenance |

---

### Query 5: Find the drivers assigned to today's bus schedules
```sql
SELECT d.full_name AS driver, d.phone, s.schedule_id, r.route_number, b.bus_number, s.departure_time
FROM staff_assignments sa
JOIN drivers d ON sa.driver_id = d.driver_id
JOIN schedules s ON sa.schedule_id = s.schedule_id
JOIN bus_routes r ON s.route_id = r.route_id
JOIN buses b ON s.bus_id = b.bus_id
WHERE sa.assigned_date = CURDATE();
```
**Expected Output:**
Returns the active assignments linking drivers like Suresh Wankhede and Ganesh Tayade to today's departures.

---

### Query 6: Display the seat numbers and passengers booked for Schedule #1
```sql
SELECT bs.seat_number, bs.passenger_name, bs.passenger_gender, bs.fare, bs.status
FROM booking_seats bs
WHERE bs.schedule_id = 1
ORDER BY bs.seat_number ASC;
```
**Expected Output:**
| seat_number | passenger_name | passenger_gender | fare | status |
|---|---|---|---|---|
| 5 | Priya Patil | female | 25.00 | booked |
| 12 | Rahul Sharma | male | 25.00 | booked |
| 13 | Sunil Sharma | male | 25.00 | booked |

---

### Query 7: Query available capacity and occupancy rate for all active schedules
```sql
SELECT * FROM v_bus_occupancy;
```
**Expected Output:**
Returns tabular view of schedule IDs, route numbers, bus capacity, booked seats, and occupancy percentages calculated via view `v_bus_occupancy`.

---

### Query 8: Find passengers who have booked tickets exceeding the average ticket price
```sql
SELECT b.booking_reference, u.full_name, b.total_amount
FROM bookings b
JOIN users u ON b.user_id = u.user_id
WHERE b.total_amount > (SELECT AVG(total_amount) FROM bookings WHERE booking_status = 'confirmed');
```
**Expected Output:**
| booking_reference | full_name | total_amount |
|---|---|---|
| AMT-BK-202610-001 | Rahul Sharma | 50.00 |

---

### Query 9: Retrieve audit logs for booking events
```sql
SELECT log_id, action, record_id, details, created_at
FROM audit_logs
WHERE table_name = 'bookings'
ORDER BY log_id DESC;
```
**Expected Output:**
Returns records logged by our automated triggers and booking service actions.

---

### Query 10: Find routes with more than 3 intermediate stops
```sql
SELECT r.route_number, r.route_name, COUNT(rs.stop_id) AS total_halts
FROM bus_routes r
JOIN route_stops rs ON r.route_id = rs.route_id
GROUP BY r.route_number, r.route_name
HAVING COUNT(rs.stop_id) > 3;
```
**Expected Output:**
| route_number | route_name | total_halts |
|---|---|---|
| R-101 | Badnera Station to SGBAU University | 5 |
| R-103 | Rajkamal Square to Walgaon MIDC | 4 |
