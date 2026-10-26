# Vehicle Rental System

A web-based vehicle rental management system built with Python, Flask, and SQLite for a college Project-Based Learning (PBL) assignment.

## Features

### Module 1: Vehicle Management
- Add, edit, and delete vehicles
- Search and filter by name, registration, type, and status
- Server-side validation (unique registration, positive rates)
- Deletion protection for vehicles with booking history

### Module 2: Booking Management
- Create bookings with vehicle selection and date range
- Inclusive rental calculation: `(end_date - start_date + 1) × daily_rate`
- Overlap prevention for active bookings on the same vehicle
- Booking cancellation (releases dates for rebooking)
- Booking lifecycle completion (records vehicle return and finalizes reservation)
- One-click CSV report export for reservations
- Historical record preservation
- Race condition mitigation via `BEGIN IMMEDIATE`

### Dashboard
- Vehicle and booking statistics
- Revenue summary
- Recent bookings

## Technology Stack

| Component       | Technology         |
|-----------------|--------------------|
| Backend         | Python 3.12, Flask 3.0 |
| Database        | SQLite (WAL mode)  |
| Frontend        | HTML5, CSS3, JavaScript |
| Testing         | pytest             |
| Typography      | Inter (Google Fonts) |

## Quick Start

### Prerequisites
- Python 3.10 or higher
- pip

### Installation

```bash
# Clone or navigate to the project directory
cd "Vehicle Rental System"

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

The application will be available at **http://127.0.0.1:5000**

### Running Tests

```bash
# Run all automated tests (82 tests: 52 Black-Box + 30 White-Box)
python3 -m pytest -v

# Run Black-Box tests only
python3 -m pytest tests/test_vehicles.py tests/test_bookings.py -v

# Run White-Box tests only (basis paths & branch coverage)
python3 -m pytest tests/test_whitebox.py -v

# Generate visual HTML branch coverage report (equivalent to Eclipse EclEmma)
python3 -m pytest --cov=. --cov-branch --cov-report=html
```

## Project Structure

```
Vehicle Rental System/
├── app.py                  # Flask application factory
├── run.py                  # Entry point (python run.py)
├── schema.py               # Database schema definition
├── vehicles.py             # Vehicle management blueprint
├── bookings.py             # Booking management blueprint
├── dashboard.py            # Dashboard blueprint
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignore rules
├── tests/                  # Automated test suite
│   ├── conftest.py         # Pytest fixtures and isolated database setup
│   ├── test_vehicles.py    # Vehicle black-box tests (22 tests)
│   ├── test_bookings.py    # Booking black-box tests (30 tests)
│   └── test_whitebox.py    # White-box structural & basis path tests (30 tests)
├── templates/
│   ├── base.html           # Base layout template
│   ├── dashboard.html      # Dashboard page
│   ├── vehicles/
│   │   ├── list.html       # Vehicle listing with search/filter
│   │   ├── add.html        # Add vehicle form
│   │   └── edit.html       # Edit vehicle form
│   └── bookings/
│       ├── list.html       # Booking listing with filters
│       ├── create.html     # Create booking form
│       └── view.html       # Booking detail view
├── static/
│   ├── css/
│   │   └── styles.css      # Complete design system & responsive styling
│   └── js/
│       ├── app.js          # Client-side interactions & form logic
│       └── lucide.min.js   # Icon package
└── docs/
    ├── test_cases.md        # Black-box test cases & traceability matrix
    ├── whitebox_testing.md  # White-box CFG, Cyclomatic Complexity & Basis Paths
    ├── project_report.md    # Comprehensive project report
    ├── presentation_outline.md  # Evaluation presentation
    ├── jira_backlog.csv     # JIRA import-ready backlog
    ├── jira_setup_guide.md  # JIRA setup instructions
    └── demo_checklist.md    # Demonstration checklist
```

## Database Schema

### vehicles
| Column              | Type    | Constraints                    |
|---------------------|---------|--------------------------------|
| id                  | INTEGER | PRIMARY KEY AUTOINCREMENT      |
| registration_number | TEXT    | NOT NULL, UNIQUE               |
| name                | TEXT    | NOT NULL                       |
| type                | TEXT    | NOT NULL                       |
| daily_rental_rate   | REAL    | NOT NULL, CHECK > 0            |
| status              | TEXT    | DEFAULT 'available'            |
| created_at          | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP    |
| updated_at          | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP    |

### bookings
| Column        | Type    | Constraints                         |
|---------------|---------|-------------------------------------|
| id            | INTEGER | PRIMARY KEY AUTOINCREMENT           |
| vehicle_id    | INTEGER | FOREIGN KEY → vehicles(id)          |
| customer_name | TEXT    | NOT NULL                            |
| start_date    | TEXT    | NOT NULL                            |
| end_date      | TEXT    | NOT NULL                            |
| total_days    | INTEGER | NOT NULL, CHECK > 0                 |
| total_amount  | REAL    | NOT NULL, CHECK > 0                 |
| status        | TEXT    | DEFAULT 'active'                    |
| created_at    | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP         |
| updated_at    | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP         |

## Rental Calculation Rule

This system uses **inclusive** day counting:

```
total_days = (end_date - start_date).days + 1
total_amount = total_days × daily_rental_rate
```

**Example:** Renting from January 10 to January 12 = **3 days** (10th, 11th, 12th)

## Security Notes

- All values calculated server-side (never trusts browser-submitted prices)
- Parameterized SQL queries throughout (no SQL injection)
- Foreign key enforcement enabled on every connection
- Input validation on both client and server
- No hard-coded secrets (SECRET_KEY generated at runtime)
- No fake security claims — no payment gateway exists in this version

## License

This project is developed for educational purposes as a college PBL assignment.
