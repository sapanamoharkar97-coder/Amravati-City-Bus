# Formal Relational Schema & Normalization Analysis
## City Bus Management System for Amravati (`city_bus_db`)

---

## 1. Formal Relational Notation

Notation rules:
- **`PK`**: Primary Key (Underlined in standard DBMS literature)
- **`FK`**: Foreign Key with referenced table in parentheses
- **`UK`**: Candidate Key / Unique Constraint
- **`NN`**: Not Null Constraint

1. **`users`** (
   <ins>**`user_id`**</ins> [PK],
   `username` [UK, NN],
   `email` [UK, NN],
   `password_hash` [NN],
   `role` [NN],
   `full_name` [NN],
   `phone` [NN],
   `is_active` [NN],
   `created_at`,
   `updated_at`
)

2. **`passengers`** (
   <ins>**`passenger_id`**</ins> [PK],
   `user_id` [FK -> `users(user_id)` ON DELETE CASCADE, UK, NN],
   `gender`,
   `age`,
   `address`,
   `city`,
   `emergency_contact`,
   `created_at`
)

3. **`drivers`** (
   <ins>**`driver_id`**</ins> [PK],
   `license_number` [UK, NN],
   `full_name` [NN],
   `phone` [NN],
   `experience_years` [NN],
   `status` [NN],
   `created_at`
)

4. **`conductors`** (
   <ins>**`conductor_id`**</ins> [PK],
   `badge_number` [UK, NN],
   `full_name` [NN],
   `phone` [NN],
   `status` [NN],
   `created_at`
)

5. **`buses`** (
   <ins>**`bus_id`**</ins> [PK],
   `bus_number` [UK, NN],
   `registration_number` [UK, NN],
   `bus_type` [NN],
   `capacity` [NN],
   `status` [NN],
   `created_at`
)

6. **`bus_stops`** (
   <ins>**`stop_id`**</ins> [PK],
   `stop_name` [UK, NN],
   `landmark`,
   `latitude`,
   `longitude`,
   `city` [NN],
   `is_active` [NN],
   `created_at`
)

7. **`bus_routes`** (
   <ins>**`route_id`**</ins> [PK],
   `route_number` [UK, NN],
   `route_name` [NN],
   `start_stop_id` [FK -> `bus_stops(stop_id)`, NN],
   `end_stop_id` [FK -> `bus_stops(stop_id)`, NN],
   `total_distance_km` [NN],
   `estimated_duration_mins` [NN],
   `base_fare` [NN],
   `is_active` [NN],
   `created_at`
)

8. **`route_stops`** (
   <ins>**`route_stop_id`**</ins> [PK],
   `route_id` [FK -> `bus_routes(route_id)` ON DELETE CASCADE, NN],
   `stop_id` [FK -> `bus_stops(stop_id)` ON DELETE RESTRICT, NN],
   `stop_sequence` [NN],
   `distance_from_source_km` [NN],
   `fare_from_source` [NN],
   `halt_duration_mins` [NN]
)  
*Candidate Keys / Composite Unique Constraints:* `(route_id, stop_sequence)` and `(route_id, stop_id)`.

9. **`schedules`** (
   <ins>**`schedule_id`**</ins> [PK],
   `route_id` [FK -> `bus_routes(route_id)`, NN],
   `bus_id` [FK -> `buses(bus_id)`, NN],
   `departure_time` [NN],
   `arrival_time` [NN],
   `journey_date` [NN],
   `fare` [NN],
   `frequency` [NN],
   `status` [NN],
   `created_at`
)

10. **`staff_assignments`** (
    <ins>**`assignment_id`**</ins> [PK],
    `schedule_id` [FK -> `schedules(schedule_id)` ON DELETE CASCADE, UK, NN],
    `driver_id` [FK -> `drivers(driver_id)`, NN],
    `conductor_id` [FK -> `conductors(conductor_id)`, NN],
    `assigned_date` [NN],
    `status` [NN],
    `created_at`
)

11. **`bookings`** (
    <ins>**`booking_id`**</ins> [PK],
    `booking_reference` [UK, NN],
    `user_id` [FK -> `users(user_id)`, NN],
    `schedule_id` [FK -> `schedules(schedule_id)`, NN],
    `source_stop_id` [FK -> `bus_stops(stop_id)`, NN],
    `destination_stop_id` [FK -> `bus_stops(stop_id)`, NN],
    `booking_date` [NN],
    `journey_date` [NN],
    `total_passengers` [NN],
    `total_amount` [NN],
    `booking_status` [NN],
    `cancellation_reason`,
    `cancelled_at`,
    `created_at`
)

12. **`booking_seats`** (
    <ins>**`booking_seat_id`**</ins> [PK],
    `booking_id` [FK -> `bookings(booking_id)` ON DELETE CASCADE, NN],
    `schedule_id` [FK -> `schedules(schedule_id)`, NN],
    `seat_number` [NN],
    `passenger_name` [NN],
    `passenger_age` [NN],
    `passenger_gender` [NN],
    `fare` [NN],
    `status` [NN]
)

13. **`tickets`** (
    <ins>**`ticket_id`**</ins> [PK],
    `ticket_number` [UK, NN],
    `booking_id` [FK -> `bookings(booking_id)` ON DELETE CASCADE, UK, NN],
    `qr_code_data` [NN],
    `issued_at` [NN],
    `status` [NN]
)

14. **`payments`** (
    <ins>**`payment_id`**</ins> [PK],
    `payment_reference` [UK, NN],
    `booking_id` [FK -> `bookings(booking_id)` ON DELETE CASCADE, NN],
    `amount` [NN],
    `payment_method` [NN],
    `transaction_status` [NN],
    `payment_date` [NN],
    `notes`
)

15. **`audit_logs`** (
    <ins>**`log_id`**</ins> [PK],
    `user_id` [FK -> `users(user_id)` ON DELETE SET NULL],
    `action` [NN],
    `table_name` [NN],
    `record_id`,
    `details`,
    `ip_address`,
    `created_at`
)

---

## 2. Normalization Analysis

### First Normal Form (1NF) Compliance
- Every relation has a well-defined primary key.
- All column values are **atomic** (single indivisible values). For example, passenger seat numbers are not stored as comma-separated lists in `bookings`; instead, each seat allocation is an individual atomic row in `booking_seats`.
- No repeating groups or multivalued arrays exist within any relation.

### Second Normal Form (2NF) Compliance
- All tables are in 1NF.
- There are **no partial dependencies**: every non-prime attribute is fully functionally dependent on the entire primary key.
- In associative tables with composite unique constraints (such as `route_stops`), attributes `distance_from_source_km` and `fare_from_source` depend on the composite key `(route_id, stop_sequence)`, not on `route_id` alone.

### Third Normal Form (3NF) Compliance
- All tables are in 2NF.
- There are **no transitive dependencies** (where non-key attribute $X \rightarrow Y$ and $Y \rightarrow Z$ with $Z$ non-key).
  - *Example 1:* Passenger address and emergency contact are stored in `passengers`, not redundantly in `bookings`. The `bookings` table only references `user_id`.
  - *Example 2:* Bus capacity and fuel type belong to `buses`. The `schedules` table references `bus_id` without duplicating capacity.
  - *Example 3:* Stop name and coordinates belong to `bus_stops`. The `route_stops` table only stores `stop_id`.

### Boyce-Codd Normal Form (BCNF) Compliance
- For every functional dependency $X \rightarrow Y$, the determinant $X$ is a superkey.
- All candidate keys (`username`, `email` in `users`; `license_number` in `drivers`; `bus_number`, `registration_number` in `buses`; `route_number` in `bus_routes`) are unique and serve as valid superkeys.
