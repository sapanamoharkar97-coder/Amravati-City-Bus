# System Flowcharts & Process Workflows
## City Bus Management System for Amravati

This document contains standard Mermaid process flowcharts illustrating the primary operations of the system.

---

## 1. User Authentication Flow

```mermaid
flowchart TD
    Start(["User arrives at Portal"]) --> CheckAuth{"Already Logged In?"}
    CheckAuth -- Yes --> RoleCheck{"User Role?"}
    RoleCheck -- Admin --> AdminDash["Redirect to Admin Dashboard (dashboard.html)"]
    RoleCheck -- Passenger --> PaxDash["Redirect to Passenger Portal (passenger_dashboard.html)"]

    CheckAuth -- No --> ActionSelect{"Existing Account?"}
    ActionSelect -- No --> RegisterForm["Fill Registration Form (Username, Email, Phone, Password)"]
    RegisterForm --> ValidateReg{"Valid Inputs & Unique Email/User?"}
    ValidateReg -- No --> ShowRegError["Display Validation Error"] --> RegisterForm
    ValidateReg -- Yes --> InsertUser["Insert users & passengers records in MySQL"]
    InsertUser --> GenToken["Generate Session & Token"] --> PaxDash

    ActionSelect -- Yes --> LoginForm["Enter Username/Email & Password"]
    LoginForm --> VerifyCreds{"Werkzeug Password Hash Matches?"}
    VerifyCreds -- No --> ShowLoginError["Display 'Invalid Credentials'"] --> LoginForm
    VerifyCreds -- Yes --> SetSession["Set HTTP Session & Local Storage Token"]
    SetSession --> RoleCheck
```

---

## 2. Route Search & Schedule Discovery Flow

```mermaid
flowchart TD
    StartSearch(["Passenger initiates Search"]) --> SelectStops["Select Boarding Stop & Destination Stop in Amravati"]
    SelectStops --> SelectDate["Choose Travel Date"]
    SelectDate --> SubmitSearch["Submit Search Request to API: /api/schedules/search"]
    SubmitSearch --> QueryDB["Execute SQL: Query schedules joined with route_stops"]
    QueryDB --> ValidateDirection{"Boarding Sequence < Drop-off Sequence?"}
    ValidateDirection -- No --> NoBuses["Return Empty Result: No valid forward transit on this corridor"]
    ValidateDirection -- Yes --> CheckCapacity["Query booking_seats: Calculate Booked vs Available Seats"]
    CheckCapacity --> CalcStageFare["Calculate Stage Fare: max(base_fare, dst_fare - src_fare)"]
    CalcStageFare --> RenderCards["Render Interactive Schedule Cards to Passenger"]
```

---

## 3. ACID-Compliant Seat Booking & Concurrency Flow

```mermaid
flowchart TD
    SelectSchedule(["Passenger Selects Bus Schedule"]) --> OpenSeatModal["Fetch /api/schedules/:id with Booked Seats Array"]
    OpenSeatModal --> RenderBusGrid["Render 2x2 Bus Layout Grid (Available vs Booked)"]
    RenderBusGrid --> PickSeats["Passenger selects 1 to 6 Seats"]
    PickSeats --> EnterPaxDetails["Enter Passenger Name, Age & Gender per Seat"]
    EnterPaxDetails --> SelectPayment["Select Demo Payment Gateway (UPI, Card, Cash)"]
    SelectPayment --> SubmitBooking["Submit POST /api/bookings"]

    subgraph MySQL_Transaction ["MySQL Transaction (Serializable / Row-Locking)"]
        TxStart["START TRANSACTION"] --> LockSchedule["SELECT schedule, capacity FROM schedules FOR UPDATE"]
        LockSchedule --> LockSeats["SELECT seat_number FROM booking_seats WHERE status='booked' FOR UPDATE"]
        LockSeats --> CheckCollision{"Any requested seat already booked?"}
        CheckCollision -- Yes (Race Condition) --> TxRollback["ROLLBACK TRANSACTION"]
        CheckCollision -- No --> InsertBooking["INSERT INTO bookings (confirmed)"]
        InsertBooking --> InsertSeats["INSERT INTO booking_seats (seat_number, pax_name)"]
        InsertSeats --> InsertTicket["INSERT INTO tickets (ticket_number, QR data)"]
        InsertTicket --> InsertPayment["INSERT INTO payments (success, demo_ref)"]
        InsertPayment --> TxCommit["COMMIT TRANSACTION"]
    end

    TxRollback --> ErrorResponse["Return HTTP 400: 'Seat already reserved by another rider'"]
    TxCommit --> SuccessModal["Display Booking Confirmation with Ticket Number"]
    SuccessModal --> ViewTicket["Open Boarding Pass (tickets.html)"]
```

---

## 4. Booking Cancellation & Seat Release Cycle

```mermaid
flowchart TD
    CancelReq(["Passenger / Admin requests Cancellation"]) --> OpenCancelModal["Input Cancellation Reason"]
    OpenCancelModal --> CallCancelAPI["POST /api/bookings/:id/cancel"]

    subgraph Cancel_Transaction ["Atomic Cancellation Transaction"]
        TxLock["SELECT booking FROM bookings FOR UPDATE"]
        TxLock --> CheckStatus{"Is booking already cancelled?"}
        CheckStatus -- Yes --> ReturnErr["Error: Already Cancelled"]
        CheckStatus -- No --> UpdateMaster["UPDATE bookings SET booking_status='cancelled', cancelled_at=NOW()"]
        UpdateMaster --> ReleaseSeats["UPDATE booking_seats SET status='cancelled'"]
        ReleaseSeats --> InvalidateTkt["UPDATE tickets SET status='cancelled'"]
        InvalidateTkt --> RefundPay["UPDATE payments SET transaction_status='refunded'"]
        RefundPay --> AuditCancel["INSERT INTO audit_logs (CANCEL_BOOKING)"]
        AuditCancel --> CommitCancel["COMMIT TRANSACTION"]
    end

    CommitCancel --> SeatsFreed["Seats immediately become available on seat selection grid"]
    SeatsFreed --> RefreshUI["Update Bookings Table with 'Cancelled' Badge"]
```
