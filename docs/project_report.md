# DBMS PROJECT REPORT
## CITY BUS MANAGEMENT SYSTEM FOR AMRAVATI (MAHARASHTRA, INDIA)

---

### 1. Title Page

**Project Title:** City Bus Management System for Amravati  
**Domain:** Database Management Systems (DBMS) & Full-Stack Web Engineering  
**Academic Level:** Bachelor of Engineering / Technology (B.E. / B.Tech) in Information Technology  
**Database Technology:** MySQL 8.x Relational Database Management System  
**Backend Framework:** Python 3 & Flask RESTful API Architecture  
**Frontend Framework:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5, Chart.js  
**Target Deployment Environment:** Microsoft Windows 10/11 & Local MySQL Server  
**Academic Year:** 2026  

---

### 2. Abstract

The **City Bus Management System for Amravati** is an end-to-end, database-backed enterprise transit automation platform designed to modernize public bus transport operations across the city of Amravati, Maharashtra, India. Public bus transport in semi-urban municipal regions often suffers from manual paper ticketing, lack of real-time seat tracking, scheduling delays, and opaque financial reconciliations.

This project implements a fully normalized 3NF relational database named `city_bus_db` comprising 15 interdependent tables, foreign key constraints, composite unique checks, triggers, views, and stored procedures. The software architecture features a lightweight, high-performance Python Flask backend implementing RESTful micro-endpoints and pessimistic row-level locking (`SELECT ... FOR UPDATE`) to guarantee ACID transaction semantics during simultaneous seat bookings. The client-side layer is built with responsive Bootstrap 5, interactive seat maps, official printable boarding passes with cryptographic QR tokens, and analytical Chart.js dashboards. The system provides real-time bidirectional synchronization between direct MySQL Workbench SQL queries and the live web user interface.

---

### 3. Introduction

Public bus transit is the backbone of urban mobility in Amravati, connecting critical transit junctions like Badnera Railway Station, commercial nodes like Rajkamal Square, healthcare centers like Irwin Hospital Chowk, and educational institutions like Sant Gadge Baba Amravati University (SGBAU). Managing modern transit demands requires robust database architectures capable of tracking vehicle assets, route sequences, driver-conductor duty rosters, timetable departures, passenger reservations, and revenue.

This system replaces outdated manual ledgers with a secure, automated relational platform that streamlines transit administration while providing passengers with transparent schedule lookups and seat reservations.

---

### 4. Problem Statement

Traditional municipal transit operations in Tier-2 Indian cities face multiple operational and administrative challenges:
1. **Manual Ticketing & Lack of Real-Time Visibility:** Conductors issue paper tickets manually, leaving depot managers without real-time passenger volume or route load metrics.
2. **Double Booking Risks:** Uncoordinated booking channels cause simultaneous over-allocation of seats.
3. **Complex Stage-Wise Fare Structures:** Inability to compute accurate stage fares for intermediate halts dynamically.
4. **Disjointed Crew Management:** Difficulties tracking driver and conductor assignments across varying daily shift schedules.
5. **Absence of Auditability:** Financial records and passenger cancellations lack an immutable database audit trail.

---

### 5. Objectives

The primary objectives of this project are:
1. To engineer a normalized Third Normal Form (3NF) relational database (`city_bus_db`) in MySQL 8.x.
2. To provide automated route sequencing and stage-wise fare calculations between intermediate Amravati stops.
3. To enforce database transaction integrity (ACID) with row-level locks preventing duplicate seat reservations.
4. To establish role-based access control (RBAC) separating administrative controls from passenger self-service.
5. To generate official printable boarding passes containing QR verification strings.
6. To deliver management dashboards with Chart.js visualizations for revenue by payment mode and route occupancy.
7. To ensure real-time synchronization between direct MySQL Workbench edits and the web application.

---

### 6. Scope

- **Geographic Scope:** Transit network centered in Amravati, Maharashtra, covering key nodes: Badnera Railway Station, Rajkamal Square, Irwin Hospital, Panchavati, SGBAU University, Central Bus Stand, Shivaji Nagar (HVPM), Walgaon MIDC, Camp Collectorate, and Shegaon Naka.
- **Functional Scope:** Fleet inventory, route halt management, timetable scheduling, crew rostering, passenger registration, seat selection, booking cancellations, simulation payments, audit logging, and CSV reporting.
- **Academic Disclaimer:** Schedule and pricing data are demonstrative for educational assessment and do not represent official MSRTC schedules.

---

### 7. Existing System

In the legacy manual system:
- Bus schedules are printed on physical depot notice boards.
- Seat allocation on local city buses is informal, causing overcrowding.
- Trip collections are calculated manually at the end of shifts using paper waybills.
- Cancellations and refunds require physical visits to the depot station counter.
- Historical data analysis requires manual ledger auditing.

---

### 8. Proposed System

The proposed system introduces:
- **Centralized MySQL 8.x Database:** Single source of truth with foreign key constraints and triggers.
- **Dynamic Route Sequence Matrix (`route_stops`):** Stores kilometer distances and incremental fares per halt.
- **Interactive Visual Seat Layout:** 2x2 layout mimicking real buses with live status (Available, Selected, Booked).
- **Pessimistic Concurrency Locking:** `SELECT ... FOR UPDATE` prevents race conditions.
- **Automated Audit Trail (`audit_logs`):** Database triggers and API hooks automatically record actions.
- **Immediate Live Sync:** Direct database modifications in MySQL Workbench appear on page refresh.

---

### 9. Feasibility Study

1. **Technical Feasibility:** Built entirely on open-source, industry-standard technologies (Python, Flask, MySQL 8.x, Vanilla JS, Bootstrap 5). Requires no paid APIs or cloud dependencies.
2. **Economic Feasibility:** Zero software licensing fees. Can run on local commodity Windows hardware or budget Linux servers.
3. **Operational Feasibility:** Intuitive browser-based user experience requiring no specialized software training for depot staff or passengers.

---

### 10. Hardware and Software Requirements

#### Hardware Requirements
- **Processor:** Intel Core i3 / AMD Ryzen 3 or higher.
- **RAM:** Minimum 4 GB (8 GB recommended).
- **Storage:** Minimum 500 MB free hard disk space.
- **Network:** Localhost (127.0.0.1) or LAN connectivity.

#### Software Requirements
- **Operating System:** Microsoft Windows 10/11 (or Linux / macOS).
- **Database Engine:** MySQL Server 8.0+ & MySQL Workbench 8.0+.
- **Runtime:** Python 3.10+ (with virtual environment support).
- **Web Browser:** Google Chrome, Microsoft Edge, or Mozilla Firefox.
- **Code Editor:** Visual Studio Code.

---

### 11. System Architecture

The application adopts a decoupled Three-Tier Architecture:
1. **Presentation Tier (Frontend):** Modern HTML5, CSS3, JavaScript, and Bootstrap 5 single-page and multi-page interfaces making asynchronous JSON `fetch()` calls.
2. **Application Tier (Backend):** Python Flask REST API server enforcing authentication, input validation, role-based authorization, and transactional business logic.
3. **Data Tier (MySQL Database):** Normalized relational schema (`city_bus_db`) running on InnoDB with ACID compliance, constraints, views, and stored procedures.

---

### 12. ER Diagram

Refer to [`docs/ER_diagram.md`](file:///C:/Users/Balaji/.gemini/antigravity/scratch/CityBusManagementSystem/docs/ER_diagram.md) for the full Mermaid diagram.  
Core entities: `users`, `passengers`, `drivers`, `conductors`, `buses`, `bus_stops`, `bus_routes`, `route_stops`, `schedules`, `staff_assignments`, `bookings`, `booking_seats`, `tickets`, `payments`, and `audit_logs`.

---

### 13. Relational Schema

Refer to [`docs/relational_schema.md`](file:///C:/Users/Balaji/.gemini/antigravity/scratch/CityBusManagementSystem/docs/relational_schema.md) for the formal schema definitions, primary keys, foreign keys, and candidate keys.

---

### 14. Data Dictionary

Refer to [`docs/data_dictionary.md`](file:///C:/Users/Balaji/.gemini/antigravity/scratch/CityBusManagementSystem/docs/data_dictionary.md) for complete column-by-column definitions, data types, nullability, and constraints across all 15 tables.

---

### 15. Normalization up to 3NF

The database was designed starting from an unnormalized state and decomposed through First Normal Form (1NF), Second Normal Form (2NF), and Third Normal Form (3NF). Full mathematical dependency proofs and functional dependency charts are detailed in [`docs/relational_schema.md`](file:///C:/Users/Balaji/.gemini/antigravity/scratch/CityBusManagementSystem/docs/relational_schema.md#2-normalization-analysis).

---

### 16. SQL Implementation

The relational implementation consists of modular scripts in `database/`:
- [`schema.sql`](file:///C:/Users/Balaji/.gemini/antigravity/scratch/CityBusManagementSystem/database/schema.sql): Table definitions, foreign keys, and indexes.
- [`sample_data.sql`](file:///C:/Users/Balaji/.gemini/antigravity/scratch/CityBusManagementSystem/database/sample_data.sql): Seed data for Amravati transit network.
- [`views.sql`](file:///C:/Users/Balaji/.gemini/antigravity/scratch/CityBusManagementSystem/database/views.sql): Abstracted query views (`v_bus_occupancy`, `v_route_stop_details`).
- [`procedures.sql`](file:///C:/Users/Balaji/.gemini/antigravity/scratch/CityBusManagementSystem/database/procedures.sql): Stored procedures for schedule search and revenue summaries.
- [`triggers.sql`](file:///C:/Users/Balaji/.gemini/antigravity/scratch/CityBusManagementSystem/database/triggers.sql): Automated audit logging and child status synchronization.
- [`crud_queries.sql`](file:///C:/Users/Balaji/.gemini/antigravity/scratch/CityBusManagementSystem/database/crud_queries.sql): DDL and DML operations.

---

### 17. Frontend Implementation

The frontend utilizes Vanilla JavaScript and Bootstrap 5 without bulky third-party frontend frameworks:
- **`index.html`**: Public landing page with schedule search.
- **`login.html` & `register.html`**: Authentication portal with demo auto-fill pills.
- **`dashboard.html`**: Administrator control panel with fleet KPIs and live audit logs.
- **`passenger_dashboard.html`**: Passenger booking portal with interactive 2x2 seat selection grid.
- **`buses.html`, `routes.html`, `stops.html`**: Fleet and infrastructure management.
- **`schedules.html`, `drivers.html`, `conductors.html`**: Timetable and crew assignment.
- **`bookings.html` & `tickets.html`**: Reservation management and printable boarding passes.
- **`reports.html`**: Analytical dashboards with Chart.js and CSV export.

---

### 18. Backend Implementation

The backend is built in Python Flask following a modular blueprint structure:
- **`app.py`**: Application factory, static asset routing, and health checks.
- **`db.py`**: Centralized connection manager and context manager supporting `mysql-connector-python` and `PyMySQL`.
- **`services/booking_service.py`**: ACID-compliant booking transaction coordinator with row locks.
- **`services/fare_service.py`**: Stage-wise fare calculator.
- **`utils/decorators.py`**: Role-based access control (`@login_required`, `@admin_required`).

---

### 19. Application Screenshots & Capture Guide

To capture screenshots for your final project submission report:
1. **Landing Page:** Open `http://127.0.0.1:5000/index.html` & capture the Hero section and Quick Search card.
2. **Admin Dashboard:** Log in as `admin` and capture the KPI cards, recent bookings table, and audit log.
3. **Bus Fleet Management:** Open `buses.html` and capture the registered vehicles table and the "Add Bus" modal.
4. **Passenger Seat Selector:** Open `passenger_dashboard.html`, search for a route, click "Select Seats", and capture the interactive 2x2 bus layout.
5. **Printable Boarding Pass:** Open `tickets.html?ticket_id=1` and capture the official ticket with QR code.
6. **Analytics & BI Charts:** Open `reports.html` and capture the revenue doughnut and popular routes bar charts.

---

### 20. Test Cases and Outputs

20 structured test cases covering authentication, CRUD, concurrency, cancellations, and MySQL live sync are documented in [`docs/test_cases.md`](file:///C:/Users/Balaji/.gemini/antigravity/scratch/CityBusManagementSystem/docs/test_cases.md).

---

### 21. Limitations

1. **Simulation Payments:** Real payment gateways (Razorpay, Stripe) require merchant credentials and banking webhooks; the system uses a simulated demonstration ledger.
2. **Static Fleet Sizes:** Bus capacities are fixed per vehicle rather than dynamically configurable.
3. **Offline Mode:** The system requires a live connection to the MySQL Server and does not cache writes offline.

---

### 22. Future Scope

1. **GPS Live Vehicle Tracking:** Integrating IoT GPS transponders on buses to show real-time bus locations on Leaflet / Google Maps.
2. **Automated QR Ticket Scanning:** Mobile app for conductors to scan passenger QR codes using a smartphone camera.
3. **SMS / WhatsApp Ticket Notifications:** Automatic dispatch of ticket details and departure alerts.

---

### 23. Conclusion

The **City Bus Management System for Amravati** successfully demonstrates the design and deployment of an enterprise-grade relational database management application. By adhering to 3NF normalization, ACID transaction principles, and modular REST API architecture, the project provides an intuitive and reliable tool for transit administration and passenger ticketing.

---

### 24. References

1. Elmasri, R., & Navathe, S. B. (2015). *Fundamentals of Database Systems* (7th ed.). Pearson.
2. Silberschatz, A., Korth, H. F., & Sudarshan, S. (2019). *Database System Concepts* (7th ed.). McGraw-Hill.
3. MySQL 8.0 Reference Manual: https://dev.mysql.com/doc/refman/8.0/en/
4. Flask Documentation (3.0.x): https://flask.palletsprojects.com/
5. Bootstrap 5 Documentation: https://getbootstrap.com/docs/5.3/
