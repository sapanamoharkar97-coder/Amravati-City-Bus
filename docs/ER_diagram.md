# Entity-Relationship (ER) Diagram
## City Bus Management System for Amravati (`city_bus_db`)

This document presents the relational Entity-Relationship model for the Amravati City Bus Management System. The diagram strictly matches the 15 normalized tables implemented in [`database/schema.sql`](file:///C:/Users/Balaji/.gemini/antigravity/scratch/CityBusManagementSystem/database/schema.sql).

---

## 1. Mermaid ER Diagram

```mermaid
erDiagram
    USERS ||--o| PASSENGERS : "extends (1:1)"
    USERS ||--o{ BOOKINGS : "places (1:N)"
    USERS ||--o{ AUDIT_LOGS : "triggers (1:N)"

    BUS_STOPS ||--o{ BUS_ROUTES : "start_stop (1:N)"
    BUS_STOPS ||--o{ BUS_ROUTES : "end_stop (1:N)"
    BUS_STOPS ||--o{ ROUTE_STOPS : "included_in (1:N)"
    BUS_ROUTES ||--|{ ROUTE_STOPS : "contains_stages (1:N)"

    BUS_ROUTES ||--o{ SCHEDULES : "scheduled_on (1:N)"
    BUSES ||--o{ SCHEDULES : "operates (1:N)"

    SCHEDULES ||--o| STAFF_ASSIGNMENTS : "assigned_to (1:1)"
    DRIVERS ||--o{ STAFF_ASSIGNMENTS : "drives (1:N)"
    CONDUCTORS ||--o{ STAFF_ASSIGNMENTS : "conducts (1:N)"

    SCHEDULES ||--o{ BOOKINGS : "reserved_under (1:N)"
    BUS_STOPS ||--o{ BOOKINGS : "source_halt (1:N)"
    BUS_STOPS ||--o{ BOOKINGS : "dest_halt (1:N)"

    BOOKINGS ||--|{ BOOKING_SEATS : "allocates (1:N)"
    SCHEDULES ||--o{ BOOKING_SEATS : "holds_seat_on (1:N)"

    BOOKINGS ||--|| TICKETS : "issues (1:1)"
    BOOKINGS ||--|{ PAYMENTS : "records (1:N)"

    USERS {
        int user_id PK
        string username UK
        string email UK
        string password_hash
        enum role
        string full_name
        string phone
        boolean is_active
        timestamp created_at
    }

    PASSENGERS {
        int passenger_id PK
        int user_id FK
        enum gender
        int age
        string address
        string city
        string emergency_contact
    }

    DRIVERS {
        int driver_id PK
        string license_number UK
        string full_name
        string phone
        int experience_years
        enum status
    }

    CONDUCTORS {
        int conductor_id PK
        string badge_number UK
        string full_name
        string phone
        enum status
    }

    BUSES {
        int bus_id PK
        string bus_number UK
        string registration_number UK
        enum bus_type
        int capacity
        enum status
    }

    BUS_STOPS {
        int stop_id PK
        string stop_name UK
        string landmark
        decimal latitude
        decimal longitude
        string city
        boolean is_active
    }

    BUS_ROUTES {
        int route_id PK
        string route_number UK
        string route_name
        int start_stop_id FK
        int end_stop_id FK
        decimal total_distance_km
        int estimated_duration_mins
        decimal base_fare
        boolean is_active
    }

    ROUTE_STOPS {
        int route_stop_id PK
        int route_id FK
        int stop_id FK
        int stop_sequence
        decimal distance_from_source_km
        decimal fare_from_source
        int halt_duration_mins
    }

    SCHEDULES {
        int schedule_id PK
        int route_id FK
        int bus_id FK
        time departure_time
        time arrival_time
        date journey_date
        decimal fare
        enum frequency
        enum status
    }

    STAFF_ASSIGNMENTS {
        int assignment_id PK
        int schedule_id FK,UK
        int driver_id FK
        int conductor_id FK
        date assigned_date
        enum status
    }

    BOOKINGS {
        int booking_id PK
        string booking_reference UK
        int user_id FK
        int schedule_id FK
        int source_stop_id FK
        int destination_stop_id FK
        date journey_date
        int total_passengers
        decimal total_amount
        enum booking_status
        string cancellation_reason
        timestamp cancelled_at
    }

    BOOKING_SEATS {
        int booking_seat_id PK
        int booking_id FK
        int schedule_id FK
        int seat_number
        string passenger_name
        int passenger_age
        enum passenger_gender
        decimal fare
        enum status
    }

    TICKETS {
        int ticket_id PK
        string ticket_number UK
        int booking_id FK,UK
        string qr_code_data
        timestamp issued_at
        enum status
    }

    PAYMENTS {
        int payment_id PK
        string payment_reference UK
        int booking_id FK
        decimal amount
        enum payment_method
        enum transaction_status
        timestamp payment_date
        string notes
    }

    AUDIT_LOGS {
        int log_id PK
        int user_id FK
        string action
        string table_name
        int record_id
        text details
        string ip_address
        timestamp created_at
    }
```

---

## 2. Relational Cardinalities and Multiplicities

| Parent Entity | Child Entity | Relationship Type | Cardinality | Explanation |
|---|---|---|---|---|
| `users` | `passengers` | Extension | 1 : (0,1) | A user with role 'passenger' has exactly one profile extension. Admin users do not require a row in `passengers`. |
| `bus_stops` | `bus_routes` | Origin / Destination | 1 : N | A bus stop serves as the starting point or destination for multiple bus routes. |
| `bus_routes` | `route_stops` | Composition | 1 : N | A route consists of multiple ordered stop sequences. |
| `bus_stops` | `route_stops` | Participation | 1 : N | A stop appears in many routes at different sequence positions. |
| `buses` | `schedules` | Assignment | 1 : N | A physical bus vehicle operates multiple daily or weekly schedules over time. |
| `bus_routes` | `schedules` | Timetable | 1 : N | A route has multiple morning, afternoon, and evening departures. |
| `schedules` | `staff_assignments` | Crew Deployment | 1 : 1 | Each specific schedule has at most one active crew assignment. |
| `drivers` | `staff_assignments` | Crew Assignment | 1 : N | A driver operates multiple schedules across days. |
| `conductors` | `staff_assignments` | Crew Assignment | 1 : N | A conductor operates multiple schedules across days. |
| `users` | `bookings` | Customer Order | 1 : N | A registered passenger places zero, one, or many bus bookings. |
| `schedules` | `bookings` | Journey Booking | 1 : N | A scheduled departure accepts bookings until bus capacity is reached. |
| `bookings` | `booking_seats` | Seat Allocations | 1 : N | A booking contains one or more reserved passenger seat records. |
| `bookings` | `tickets` | Proof of Passage | 1 : 1 | Every confirmed booking receives exactly one ticket with secure QR string. |
| `bookings` | `payments` | Settlement | 1 : N | A booking has payment records (e.g., initial payment, refund upon cancellation). |
| `users` | `audit_logs` | Audit Trail | 1 : N | Administrative and booking actions link back to the acting user. |
