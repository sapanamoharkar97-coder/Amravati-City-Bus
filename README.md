# City Bus Management System for Amravati (Maharashtra, India)

A full-stack, enterprise-grade, academic DBMS project connecting a normalized **MySQL 8.x** relational database with a **Python Flask REST API** and a modern **Bootstrap 5** frontend.

Designed for IT Engineering student practicals, project reports, viva voce defense, GitHub portfolios, and placement resumes.

---

## 🌟 Key Features

- **Normalized 3NF MySQL Database (`city_bus_db`):** 15 tables with foreign keys, composite unique constraints, indexes, triggers, views, and stored procedures.
- **Pessimistic Concurrency Locking:** `SELECT ... FOR UPDATE` prevents race conditions and simultaneous double booking.
- **Dynamic Fare Engine:** Calculates stage-wise fares based on intermediate stop sequences across Amravati city.
- **Interactive Visual Seat Selector:** 2x2 bus layout with live Available, Selected, and Booked states.
- **Printable E-Tickets & Boarding Passes:** Cryptographic QR code representation and print CSS styling.
- **Administrator Intelligence Dashboard:** Real-time KPI counters and Chart.js analytics for revenue and bus occupancy.
- **Live Bidirectional Synchronization:** Edits made in MySQL Workbench appear in the application immediately upon page refresh.
- **Complete Documentation Suite:** 24-section Project Report, ER Diagram, Relational Schema, Data Dictionary, Flowcharts, 35 Viva Q&As, and 20 Test Cases.

---

## 📁 Project Directory Structure

```text
CityBusManagementSystem/
├── backend/
│   ├── app.py                      # Flask application factory & static server
│   ├── config.py                   # Configuration & .env loader
│   ├── db.py                       # Centralized MySQL connection & pooling
│   ├── requirements.txt            # Python dependencies
│   ├── .env.example                # Example environment configuration
│   ├── .env                        # Local credentials (excluded from git)
│   ├── routes/
│   │   ├── auth_routes.py          # Authentication & profile endpoints
│   │   ├── admin_routes.py         # Dashboard metrics & audit logs
│   │   ├── bus_routes.py           # Bus fleet CRUD
│   │   ├── route_routes.py         # Transit route & halts CRUD
│   │   ├── stop_routes.py          # Bus stops CRUD
│   │   ├── staff_routes.py         # Drivers, conductors & roster assignments
│   │   ├── schedule_routes.py      # Timetable & schedule search
│   │   ├── booking_routes.py       # ACID booking transactions & cancellations
│   │   ├── ticket_routes.py        # Boarding pass & payments
│   │   └── report_routes.py        # Analytics & CSV export
│   ├── services/
│   │   ├── booking_service.py      # Pessimistic locking & transaction coordinator
│   │   └── fare_service.py         # Stage-wise fare calculator
│   └── utils/
│       ├── decorators.py           # @login_required & @admin_required RBAC
│       └── validators.py           # Input, email & phone validation
├── database/
│   ├── schema.sql                  # DDL: 15 normalized tables & constraints
│   ├── sample_data.sql             # Demo records for Amravati bus network
│   ├── views.sql                   # 4 Relational reporting views
│   ├── procedures.sql              # Stored procedures for search & revenue
│   ├── triggers.sql                # Audit logging & child status triggers
│   ├── crud_queries.sql            # Practical SQL examples (JOIN, GROUP BY)
│   ├── reports.sql                 # Analytical SQL queries
│   ├── alter_examples.sql          # ALTER TABLE demonstrations
│   ├── reset_demo_data.sql         # Manual reset script (destructive)
│   └── migrations/
│       ├── README.md               # Migration guidelines
│       └── 001_initial_schema.sql  # Baseline migration
├── docs/
│   ├── project_report.md           # 24-section university project report
│   ├── ER_diagram.md               # Mermaid ER diagram & cardinalities
│   ├── relational_schema.md        # Formal schema & 3NF proof
│   ├── data_dictionary.md          # Complete column & table specifications
│   ├── flowchart.md                # System flowcharts
│   ├── viva_questions.md           # 35 Viva Q&As + 10 Practical SQL queries
│   ├── test_cases.md               # 20 Structured test cases
│   └── database_maintenance.md     # Workbench editing & backup guide
├── frontend/
│   ├── index.html                  # Public landing page with quick search
│   ├── login.html                  # Portal login with demo autofill
│   ├── register.html               # Passenger registration
│   ├── dashboard.html              # Admin KPI dashboard
│   ├── passenger_dashboard.html    # Passenger search & interactive seat map
│   ├── buses.html                  # Fleet management
│   ├── routes.html                 # Route corridors & halts
│   ├── stops.html                  # Amravati bus stops
│   ├── drivers.html                # Driver roster
│   ├── conductors.html             # Conductor roster
│   ├── schedules.html              # Timetable & crew assignments
│   ├── bookings.html               # Bookings management & cancellations
│   ├── tickets.html                # Official printable boarding pass
│   ├── reports.html                # Chart.js visualizations & CSV export
│   ├── profile.html                # Account profile settings
│   ├── css/
│   │   ├── style.css               # Core navy & teal design theme
│   │   ├── dashboard.css           # Sidebar & KPI styling
│   │   ├── forms.css               # 2x2 seat grid & payment styles
│   │   └── print.css               # Clean print styles for tickets
│   └── js/
│       ├── api.js                  # Centralized fetch client & toasts
│       ├── auth.js                 # Session guard & logout handler
│       ├── validation.js           # Client-side input validation
│       ├── dashboard.js            # Admin metrics loader
│       ├── buses.js                # Bus fleet controller
│       ├── routes.js               # Route corridors controller
│       ├── stops.js                # Bus stops controller
│       ├── schedules.js            # Timetable controller
│       ├── bookings.js             # Booking manager controller
│       ├── tickets.js              # Ticket & QR generator
│       └── reports.js              # Chart.js analytics controller
├── README.md                       # Windows setup & execution guide
└── .gitignore                      # Git exclusion rules
```

---

## 🛠️ Step-by-Step Windows Installation & Execution Guide

Follow these exact steps to set up and run the application on Windows 10/11:

### Step 1: Open the Project in Visual Studio Code
1. Open Visual Studio Code.
2. Click **File** &rarr; **Open Folder...**
3. Select the `CityBusManagementSystem` folder.
4. Press ``Ctrl + ` `` to open the integrated Windows PowerShell terminal.

---

### Step 2: Set Up Python Virtual Environment

In your VS Code PowerShell terminal, run:

```powershell
# Verify Python is installed (Python 3.10+ recommended)
python --version

# Create virtual environment named .venv
python -m venv .venv

# If PowerShell execution policy restricts running scripts, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# Upgrade pip and install required backend packages
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
```

---

### Step 3: Configure Database Credentials (`.env`)

Open `backend/.env` in VS Code and configure your local MySQL credentials:

```ini
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=amravati_city_bus_mgmt_secret_key_2026
PORT=5000
HOST=127.0.0.1

DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_ROOT_PASSWORD_HERE
DB_NAME=city_bus_db

AUTO_CREATE_DEMO_ACCOUNTS=True
```
*(Replace `YOUR_MYSQL_ROOT_PASSWORD_HERE` with your actual MySQL Server password).*

---

### Step 4: Execute Database SQL Scripts

Open **MySQL Workbench** or your **MySQL Command Line Client** and execute the SQL scripts in this exact order:

#### Method A: Using MySQL Workbench (Recommended)
1. Open MySQL Workbench and connect to your local MySQL instance (`localhost:3306`).
2. Press `Ctrl + O` and open `database/schema.sql`. Execute it using the lightning bolt icon (`Ctrl + Shift + Enter`).
3. Open and execute `database/sample_data.sql`.
4. Open and execute `database/views.sql`.
5. Open and execute `database/procedures.sql`.
6. Open and execute `database/triggers.sql`.

#### Method B: Using Windows PowerShell CLI
```powershell
# Change directory to database folder
cd database

# Execute scripts in dependency order
mysql -u root -p -e "source schema.sql"
mysql -u root -p -e "source sample_data.sql"
mysql -u root -p -e "source views.sql"
mysql -u root -p -e "source procedures.sql"
mysql -u root -p -e "source triggers.sql"

# Return to root directory
cd ..
```

---

### Step 5: Start the Flask Backend Server

From the root project directory in your activated PowerShell terminal:

```powershell
# Navigate to the backend directory
cd backend

# Start the application
python app.py
```

You will see terminal output similar to:
```text
[INFO] Initializing Amravati City Bus Management System...
[INFO] Connected to MySQL database 'city_bus_db' (Version: 8.0.x)
[INFO] Server starting on http://127.0.0.1:5000
 * Serving Flask app 'app'
 * Running on http://127.0.0.1:5000
```

---

### Step 6: Access the Application

Open your browser and navigate to:
👉 **`http://127.0.0.1:5000`**

#### Pre-Configured Demonstration Accounts:

| Role | Username | Password | Access Capabilities |
|---|---|---|---|
| **Administrator** | `admin` | `Admin@123` | Full CRUD over fleet, routes, stops, schedules, crew rostering, audit logs, and reports. |
| **Passenger** | `rahul_sharma` | `Passenger@123` | Route search, interactive 2x2 seat booking, tickets, and booking history. |

*(On the login screen, you can also click the **"Admin Demo"** or **"Passenger Demo"** buttons for 1-click credential autofill).*

---

## 🔄 Proving Live Synchronization with MySQL Workbench

To demonstrate live database integration during your practical lab or viva:
1. Open **MySQL Workbench** while the Flask server is running.
2. Execute the following update directly in Workbench:
   ```sql
   USE city_bus_db;
   UPDATE buses 
   SET capacity = 42, bus_type = 'Electric AC' 
   WHERE bus_id = 2;
   ```
3. Switch to your browser and refresh `http://127.0.0.1:5000/buses.html`.
4. **Notice:** Bus #2 immediately reflects **42 seats** and **Electric AC** without restarting the Flask server!

---

## 🛠️ Common Troubleshooting & Fixes

| Issue | Root Cause | Solution |
|---|---|---|
| `Access denied for user 'root'@'localhost'` | Incorrect password in `backend/.env` | Verify your password in MySQL Workbench and update `DB_PASSWORD` in `backend/.env`. |
| `Can't connect to MySQL server on '127.0.0.1:3306'` | MySQL Windows Service is stopped | Open Windows Services (`services.msc`), find **MySQL80**, right-click and click **Start**. |
| `Unknown database 'city_bus_db'` | Database DDL script not executed | Execute `database/schema.sql` in MySQL Workbench to create the database and tables. |
| `Address already in use (Port 5000)` | Another application is using port 5000 | In `backend/.env`, change `PORT=5000` to `PORT=5050`, or kill the process: `Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess \| Stop-Process`. |
| `Activate.ps1 cannot be loaded because running scripts is disabled` | PowerShell execution policy | Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` in your PowerShell window. |

---

## 📄 License & Academic Attribution
Developed for IT Engineering Academic DBMS Examination and Project Submission (Amravati, Maharashtra).  
Fictional demonstration routes and timetable data for academic assessment.
