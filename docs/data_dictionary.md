# Data Dictionary
## City Bus Management System for Amravati (`city_bus_db`)

The Data Dictionary defines every table, column, data type, key status, nullability, default value, and domain description in the MySQL database.

---

### 1. Table: `users`
Stores core user authentication credentials and roles.

| Column | Data Type | Nullable | Key | Default | Description |
|---|---|---|---|---|---|
| `user_id` | INT | NO | PK | AUTO_INCREMENT | Unique identifier for system user |
| `username` | VARCHAR(50) | NO | UK | None | Unique login name (alphanumeric) |
| `email` | VARCHAR(100) | NO | UK | None | Unique primary email address |
| `password_hash` | VARCHAR(255) | NO | - | None | Secure Werkzeug password hash |
| `role` | ENUM('admin', 'passenger') | NO | - | 'passenger' | System authorization role |
| `full_name` | VARCHAR(100) | NO | - | None | User's legal full name |
| `phone` | VARCHAR(20) | NO | - | None | 10-digit mobile contact number |
| `is_active` | BOOLEAN | NO | - | TRUE | Account active flag |
| `created_at` | TIMESTAMP | YES | - | CURRENT_TIMESTAMP | Account creation timestamp |
| `updated_at` | TIMESTAMP | YES | - | ON UPDATE CURRENT_TIMESTAMP | Last record modification timestamp |

---

### 2. Table: `passengers`
Stores extended passenger demographic and profile data.

| Column | Data Type | Nullable | Key | Default | Description |
|---|---|---|---|---|---|
| `passenger_id` | INT | NO | PK | AUTO_INCREMENT | Unique passenger record identifier |
| `user_id` | INT | NO | FK, UK | None | References `users(user_id)` (1:1) |
| `gender` | ENUM('male', 'female', 'other') | YES | - | 'other' | Gender classification |
| `age` | INT | YES | - | None | Passenger age (1 to 120) |
| `address` | VARCHAR(255) | YES | - | None | Residential street address |
| `city` | VARCHAR(50) | YES | - | 'Amravati' | Residential city |
| `emergency_contact` | VARCHAR(20) | YES | - | None | Emergency phone contact number |
| `created_at` | TIMESTAMP | YES | - | CURRENT_TIMESTAMP | Profile creation timestamp |

---

### 3. Table: `drivers`
Maintains records of municipal bus drivers.

| Column | Data Type | Nullable | Key | Default | Description |
|---|---|---|---|---|---|
| `driver_id` | INT | NO | PK | AUTO_INCREMENT | Unique driver identifier |
| `license_number` | VARCHAR(50) | NO | UK | None | Commercial Heavy Driving License No. |
| `full_name` | VARCHAR(100) | NO | - | None | Driver full name |
| `phone` | VARCHAR(20) | NO | - | None | Mobile phone number |
| `experience_years`| INT | NO | - | 1 | Professional driving experience |
| `status` | ENUM('active', 'on_leave', 'inactive') | NO | - | 'active' | Operational duty availability |
| `created_at` | TIMESTAMP | YES | - | CURRENT_TIMESTAMP | Record registration timestamp |

---

### 4. Table: `conductors`
Maintains bus ticket conductors and credentials.

| Column | Data Type | Nullable | Key | Default | Description |
|---|---|---|---|---|---|
| `conductor_id` | INT | NO | PK | AUTO_INCREMENT | Unique conductor identifier |
| `badge_number` | VARCHAR(50) | NO | UK | None | Official transport authority badge number |
| `full_name` | VARCHAR(100) | NO | - | None | Conductor full name |
| `phone` | VARCHAR(20) | NO | - | None | Mobile phone number |
| `status` | ENUM('active', 'on_leave', 'inactive') | NO | - | 'active' | Roster duty status |
| `created_at` | TIMESTAMP | YES | - | CURRENT_TIMESTAMP | Registration timestamp |

---

### 5. Table: `buses`
Inventory of municipal bus fleet assets.

| Column | Data Type | Nullable | Key | Default | Description |
|---|---|---|---|---|---|
| `bus_id` | INT | NO | PK | AUTO_INCREMENT | Unique fleet asset ID |
| `bus_number` | VARCHAR(30) | NO | UK | None | Fleet fleet serial code (e.g. AMT-CITY-01) |
| `registration_number` | VARCHAR(30) | NO | UK | None | RTO registration number (e.g. MH-27-X-1001) |
| `bus_type` | ENUM('Ordinary', 'CNG Express', 'Electric AC', 'Mini Bus') | NO | - | 'Ordinary' | Vehicle category and fuel type |
| `capacity` | INT | NO | - | None | Seating capacity (10 to 100) |
| `status` | ENUM('active', 'maintenance', 'retired') | NO | - | 'active' | Physical vehicle condition |
| `created_at` | TIMESTAMP | YES | - | CURRENT_TIMESTAMP | Asset entry date |

---

### 6. Table: `bus_stops`
Geographic transit nodes and passenger pickup points in Amravati.

| Column | Data Type | Nullable | Key | Default | Description |
|---|---|---|---|---|---|
| `stop_id` | INT | NO | PK | AUTO_INCREMENT | Unique stop identifier |
| `stop_name` | VARCHAR(100) | NO | UK | None | Name of the stop / square |
| `landmark` | VARCHAR(150) | YES | - | None | Prominent nearby landmark |
| `latitude` | DECIMAL(10, 8) | YES | - | None | GPS latitude coordinate |
| `longitude` | DECIMAL(11, 8) | YES | - | None | GPS longitude coordinate |
| `city` | VARCHAR(50) | NO | - | 'Amravati' | City name |
| `is_active` | BOOLEAN | NO | - | TRUE | Whether buses halt at this stop |
| `created_at` | TIMESTAMP | YES | - | CURRENT_TIMESTAMP | Stop creation timestamp |

---

### 7. Table: `bus_routes`
Master transit corridors linking origin and destination points.

| Column | Data Type | Nullable | Key | Default | Description |
|---|---|---|---|---|---|
| `route_id` | INT | NO | PK | AUTO_INCREMENT | Unique route identifier |
| `route_number` | VARCHAR(30) | NO | UK | None | Public route code (e.g. R-101) |
| `route_name` | VARCHAR(150) | NO | - | None | Route title description |
| `start_stop_id` | INT | NO | FK | None | References `bus_stops(stop_id)` |
| `end_stop_id` | INT | NO | FK | None | References `bus_stops(stop_id)` |
| `total_distance_km` | DECIMAL(6, 2) | NO | - | None | Total corridor distance in km |
| `estimated_duration_mins` | INT | NO | - | None | Estimated one-way trip duration |
| `base_fare` | DECIMAL(8, 2) | NO | - | 10.00 | Minimum stage fare |
| `is_active` | BOOLEAN | NO | - | TRUE | Route operational flag |
| `created_at` | TIMESTAMP | YES | - | CURRENT_TIMESTAMP | Route establishment timestamp |

---

### 8. Table: `route_stops`
Associative table defining ordered sequence of stops on each route.

| Column | Data Type | Nullable | Key | Default | Description |
|---|---|---|---|---|---|
| `route_stop_id` | INT | NO | PK | AUTO_INCREMENT | Unique link identifier |
| `route_id` | INT | NO | FK, UK(1) | None | References `bus_routes(route_id)` |
| `stop_id` | INT | NO | FK, UK(2) | None | References `bus_stops(stop_id)` |
| `stop_sequence` | INT | NO | UK(1) | None | Sequence position (1, 2, 3...) |
| `distance_from_source_km` | DECIMAL(6, 2) | NO | - | 0.00 | Cumulative distance from start |
| `fare_from_source` | DECIMAL(8, 2) | NO | - | 0.00 | Stage fare from start stop |
| `halt_duration_mins` | INT | NO | - | 2 | Scheduled halt time at stop |

---

### 9. Table: `schedules`
Operational bus timetables.

| Column | Data Type | Nullable | Key | Default | Description |
|---|---|---|---|---|---|
| `schedule_id` | INT | NO | PK | AUTO_INCREMENT | Unique schedule trip identifier |
| `route_id` | INT | NO | FK | None | References `bus_routes(route_id)` |
| `bus_id` | INT | NO | FK | None | References `buses(bus_id)` |
| `departure_time` | TIME | NO | - | None | Departure time from origin |
| `arrival_time` | TIME | NO | - | None | Expected arrival time at destination |
| `journey_date` | DATE | NO | - | None | Operating date of the trip |
| `fare` | DECIMAL(8, 2) | NO | - | None | End-to-end full route fare |
| `frequency` | ENUM('daily', 'weekdays', 'weekends', 'custom') | NO | - | 'daily' | Trip recurrence pattern |
| `status` | ENUM('scheduled', 'in_transit', 'completed', 'cancelled') | NO | - | 'scheduled' | Current trip state |
| `created_at` | TIMESTAMP | YES | - | CURRENT_TIMESTAMP | Schedule creation timestamp |

---

### 10. Table: `staff_assignments`
Staff roster links assigning Driver and Conductor to each schedule.

| Column | Data Type | Nullable | Key | Default | Description |
|---|---|---|---|---|---|
| `assignment_id` | INT | NO | PK | AUTO_INCREMENT | Unique assignment ID |
| `schedule_id` | INT | NO | FK, UK | None | References `schedules(schedule_id)` (1:1) |
| `driver_id` | INT | NO | FK | None | References `drivers(driver_id)` |
| `conductor_id` | INT | NO | FK | None | References `conductors(conductor_id)` |
| `assigned_date` | DATE | NO | - | None | Duty assignment date |
| `status` | ENUM('assigned', 'completed', 'reassigned') | NO | - | 'assigned' | Assignment status |
| `created_at` | TIMESTAMP | YES | - | CURRENT_TIMESTAMP | Assignment creation timestamp |

---

### 11. Table: `bookings`
Master passenger journey booking records.

| Column | Data Type | Nullable | Key | Default | Description |
|---|---|---|---|---|---|
| `booking_id` | INT | NO | PK | AUTO_INCREMENT | Unique booking ID |
| `booking_reference` | VARCHAR(30) | NO | UK | None | Human-readable ref code (e.g. AMT-BK-202610-001) |
| `user_id` | INT | NO | FK | None | References `users(user_id)` |
| `schedule_id` | INT | NO | FK | None | References `schedules(schedule_id)` |
| `source_stop_id` | INT | NO | FK | None | Boarding stop reference |
| `destination_stop_id` | INT | NO | FK | None | Destination stop reference |
| `booking_date` | TIMESTAMP | YES | - | CURRENT_TIMESTAMP | Time booking was created |
| `journey_date` | DATE | NO | - | None | Travel date |
| `total_passengers` | INT | NO | - | None | Number of seats booked |
| `total_amount` | DECIMAL(10, 2) | NO | - | None | Total fare charged |
| `booking_status` | ENUM('pending', 'confirmed', 'cancelled') | NO | - | 'confirmed' | State of the booking |
| `cancellation_reason` | VARCHAR(255) | YES | - | NULL | Explanation if cancelled |
| `cancelled_at` | TIMESTAMP | YES | - | NULL | Cancellation timestamp |
| `created_at` | TIMESTAMP | YES | - | CURRENT_TIMESTAMP | System timestamp |

---

### 12. Table: `booking_seats`
Individual seat allocations per passenger in a booking.

| Column | Data Type | Nullable | Key | Default | Description |
|---|---|---|---|---|---|
| `booking_seat_id` | INT | NO | PK | AUTO_INCREMENT | Unique seat allocation ID |
| `booking_id` | INT | NO | FK | None | References parent `bookings(booking_id)` |
| `schedule_id` | INT | NO | FK | None | References `schedules(schedule_id)` |
| `seat_number` | INT | NO | - | None | Physical seat number on bus |
| `passenger_name` | VARCHAR(100) | NO | - | None | Name of the seat passenger |
| `passenger_age` | INT | NO | - | None | Age of the passenger |
| `passenger_gender` | ENUM('male', 'female', 'other') | NO | - | None | Gender of passenger |
| `fare` | DECIMAL(8, 2) | NO | - | None | Fare for this single seat |
| `status` | ENUM('booked', 'cancelled') | NO | - | 'booked' | Active seat status |

---

### 13. Table: `tickets`
Official boarding pass artifact with verification token.

| Column | Data Type | Nullable | Key | Default | Description |
|---|---|---|---|---|---|
| `ticket_id` | INT | NO | PK | AUTO_INCREMENT | Unique ticket identifier |
| `ticket_number` | VARCHAR(40) | NO | UK | None | Ticket serial number (e.g. TKT-AMT-101-001) |
| `booking_id` | INT | NO | FK, UK | None | References `bookings(booking_id)` (1:1) |
| `qr_code_data` | VARCHAR(255) | NO | - | None | Cryptographic verification string for QR |
| `issued_at` | TIMESTAMP | YES | - | CURRENT_TIMESTAMP | Issuance timestamp |
| `status` | ENUM('valid', 'used', 'cancelled') | NO | - | 'valid' | Boarding pass state |

---

### 14. Table: `payments`
Simulation transaction ledger linked to bookings.

| Column | Data Type | Nullable | Key | Default | Description |
|---|---|---|---|---|---|
| `payment_id` | INT | NO | PK | AUTO_INCREMENT | Unique payment ID |
| `payment_reference` | VARCHAR(50) | NO | UK | None | Transaction reference code |
| `booking_id` | INT | NO | FK | None | References `bookings(booking_id)` |
| `amount` | DECIMAL(10, 2) | NO | - | None | Paid amount in INR |
| `payment_method` | ENUM('DEMO_UPI', 'DEMO_CARD', 'DEMO_CASH', 'DEMO_NETBANKING') | NO | - | 'DEMO_UPI' | Simulation payment gateway |
| `transaction_status` | ENUM('success', 'pending', 'failed', 'refunded') | NO | - | 'success' | Settlement status |
| `payment_date` | TIMESTAMP | YES | - | CURRENT_TIMESTAMP | Transaction timestamp |
| `notes` | VARCHAR(255) | YES | - | None | Academic simulation notes |

---

### 15. Table: `audit_logs`
Security and operational audit trail.

| Column | Data Type | Nullable | Key | Default | Description |
|---|---|---|---|---|---|
| `log_id` | INT | NO | PK | AUTO_INCREMENT | Unique log event ID |
| `user_id` | INT | YES | FK | NULL | Acting user ID (NULL if system action) |
| `action` | VARCHAR(50) | NO | - | None | Event name (e.g. INSERT_BOOKING) |
| `table_name` | VARCHAR(50) | NO | - | None | Modified database table |
| `record_id` | INT | YES | - | NULL | Primary key ID of affected record |
| `details` | TEXT | YES | - | NULL | Contextual event description |
| `ip_address` | VARCHAR(45) | YES | - | '127.0.0.1' | Client network IP address |
| `created_at` | TIMESTAMP | YES | - | CURRENT_TIMESTAMP | Event timestamp |
