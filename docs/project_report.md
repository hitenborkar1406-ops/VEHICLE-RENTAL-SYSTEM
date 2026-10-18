# Vehicle Rental System — Project Report

---

## 1. Title and Abstract

**Project Title:** Vehicle Rental System

**Abstract:**
The Vehicle Rental System is a web-based application developed to streamline the management of vehicle fleets and rental bookings. Built using Python, Flask, and SQLite, the system provides an intuitive interface for adding and managing vehicles, creating and tracking rental bookings, preventing scheduling conflicts, and calculating rental charges. The application features server-side validation, inclusive rental day calculation, overlapping booking prevention, and a comprehensive automated test suite of 47 test cases. This project was developed as an individual college PBL (Project-Based Learning) assignment to demonstrate proficiency in full-stack web development, database management, software testing, and project management using JIRA.

---

## 2. Problem Statement

Vehicle rental companies often manage bookings, customer information, payments, and vehicle availability manually or through disconnected systems. This can lead to:

- **Booking conflicts** where the same vehicle is reserved for overlapping dates
- **Delayed approvals** due to manual availability checks
- **Inaccurate records** from spreadsheet-based tracking
- **Poor customer experience** from lack of real-time availability information
- **Calculation errors** in rental charges

The proposed Vehicle Rental System provides an online platform for managing vehicles and rental bookings, with reliable availability checking, accurate rental calculations, input validation, and persistent records.

---

## 3. Objectives and Scope

### Objectives

1. Develop a web-based vehicle management module for CRUD operations on vehicle records.
2. Develop a booking management module with overlap prevention and rental calculation.
3. Implement robust server-side validation for all user inputs.
4. Create an intuitive, responsive user interface.
5. Write and execute a comprehensive automated test suite.
6. Document the project with a JIRA-based project management plan.

### Scope

**In Scope:**
- Vehicle CRUD with search and filtering
- Booking creation, viewing, and cancellation
- Inclusive rental day calculation
- Overlapping booking prevention
- Server-side validation and data integrity
- Dashboard with statistics
- Automated pytest test suite (47 tests)
- JIRA project management plan

**Out of Scope (Future Enhancements):**
- Real payment processing
- Insurance verification
- Document uploads
- User authentication and role-based access
- Email notifications
- Multi-location fleet management

---

## 4. Functional and Nonfunctional Requirements

### 4.1 Functional Requirements

#### Module 1: Vehicle Management

| ID | Requirement | Status |
|----|-------------|--------|
| FR-V01 | Add a vehicle with registration number, name, type, daily rate | Implemented |
| FR-V02 | View all vehicles in a table | Implemented |
| FR-V03 | Edit vehicle details | Implemented |
| FR-V04 | Search vehicles by name or registration number | Implemented |
| FR-V05 | Filter vehicles by type and status | Implemented |
| FR-V06 | Delete a vehicle only when no booking history exists | Implemented |
| FR-V07 | Validate required fields, positive rates, unique registration | Implemented |
| FR-V08 | Display clear validation errors and success messages | Implemented |

#### Module 2: Booking Management

| ID | Requirement | Status |
|----|-------------|--------|
| FR-B01 | Select an existing vehicle for booking | Implemented |
| FR-B02 | Enter customer name and rental start/end dates | Implemented |
| FR-B03 | Validate all required inputs | Implemented |
| FR-B04 | Reject invalid date ranges and past dates | Implemented |
| FR-B05 | Calculate rental price on the server (inclusive) | Implemented |
| FR-B06 | Store each booking with unique ID in SQLite | Implemented |
| FR-B07 | View booking records and status | Implemented |
| FR-B08 | Cancel a booking | Implemented |
| FR-B09 | Prevent overlapping active bookings for same vehicle | Implemented |
| FR-B10 | Allow cancelled bookings to release reserved dates | Implemented |
| FR-B11 | Preserve historical booking records | Implemented |
| FR-B12 | Handle booking creation safely (BEGIN IMMEDIATE) | Implemented |

### 4.2 Nonfunctional Requirements

| ID | Requirement | Status |
|----|-------------|--------|
| NFR-01 | Response time < 2 seconds for all operations | Met |
| NFR-02 | Responsive design for desktop and mobile | Met |
| NFR-03 | SQLite database for zero-configuration persistence | Met |
| NFR-04 | Parameterized queries to prevent SQL injection | Met |
| NFR-05 | Foreign key enforcement for data integrity | Met |
| NFR-06 | Server-side validation (never trust browser) | Met |
| NFR-07 | No hard-coded secrets | Met |

---

## 5. Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Backend | Python | 3.12.10 | Core programming language |
| Web Framework | Flask | 3.0.3 | HTTP routing, templating, request handling |
| Database | SQLite | Built-in | Persistent data storage |
| Frontend | HTML5, CSS3, JS | — | User interface |
| Typography | Inter | Google Fonts | Modern, readable typeface |
| Testing | pytest | 8.3.3 | Automated testing framework |
| HTTP Utilities | Werkzeug | 3.0.4 | WSGI utilities (Flask dependency) |
| Project Mgmt | JIRA | Cloud | Backlog, sprints, defect tracking |

---

## 6. Architecture and Database Design

### 6.1 Application Architecture

The system follows a **modular Flask blueprint architecture**:

```
┌─────────────────────────────────────────────┐
│                  Browser                     │
│  (HTML/CSS/JS — Server-rendered templates)   │
└─────────────────┬───────────────────────────┘
                  │ HTTP
┌─────────────────▼───────────────────────────┐
│              Flask Application               │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
│  │Dashboard │ │ Vehicles │ │   Bookings   │ │
│  │Blueprint │ │Blueprint │ │  Blueprint   │ │
│  └────┬─────┘ └────┬─────┘ └──────┬───────┘ │
│       │             │              │         │
│  ┌────▼─────────────▼──────────────▼───────┐ │
│  │        SQLite Database (WAL)            │ │
│  │  ┌──────────┐  ┌──────────────┐         │ │
│  │  │ vehicles │  │   bookings   │         │ │
│  │  └──────────┘  └──────────────┘         │ │
│  └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### 6.2 Key Architectural Decisions

1. **Application Factory Pattern** (`create_app()`): Enables isolated test instances.
2. **Flask Blueprints**: Separate modules for vehicles, bookings, and dashboard.
3. **Server-side rendering**: Jinja2 templates; no frontend framework needed.
4. **Request-scoped database connections**: Via Flask's `g` object.
5. **WAL journal mode**: Better concurrent read performance.
6. **BEGIN IMMEDIATE**: Reduces race condition window for booking creation.

### 6.3 Database Schema

#### Entity-Relationship Diagram

```
┌──────────────────────┐          ┌──────────────────────┐
│      vehicles         │          │      bookings         │
├──────────────────────┤          ├──────────────────────┤
│ id (PK)              │──1───M──│ id (PK)              │
│ registration_number  │          │ vehicle_id (FK)      │
│ name                 │          │ customer_name        │
│ type                 │          │ start_date           │
│ daily_rental_rate    │          │ end_date             │
│ status               │          │ total_days           │
│ created_at           │          │ total_amount         │
│ updated_at           │          │ status               │
└──────────────────────┘          │ created_at           │
                                  │ updated_at           │
                                  └──────────────────────┘
```

**Relationship:** One vehicle can have many bookings (1:M).

#### Constraints

- `vehicles.registration_number`: UNIQUE, NOT NULL
- `vehicles.daily_rental_rate`: CHECK > 0
- `vehicles.status`: CHECK IN ('available', 'rented', 'maintenance')
- `bookings.vehicle_id`: FOREIGN KEY → vehicles(id)
- `bookings.total_days`: CHECK > 0
- `bookings.total_amount`: CHECK > 0
- `bookings.status`: CHECK IN ('active', 'cancelled', 'completed')

---

## 7. Module Descriptions

### 7.1 Vehicle Management Module

**File:** `vehicles.py`

**Endpoints:**
| Method | URL | Function |
|--------|-----|----------|
| GET | /vehicles/ | List all vehicles with search/filter |
| GET | /vehicles/add | Show add vehicle form |
| POST | /vehicles/add | Create new vehicle |
| GET | /vehicles/edit/:id | Show edit form |
| POST | /vehicles/edit/:id | Update vehicle |
| POST | /vehicles/delete/:id | Delete vehicle |

**Validation Logic:**
- Registration number: required, trimmed, unique across vehicles
- Name: required, trimmed
- Type: required, must be one of [Car, SUV, Van, Truck, Motorcycle, Bus]
- Daily rental rate: required, must parse as float, must be > 0
- Duplicate check excludes current vehicle ID during edits

**Deletion Rule:**
A vehicle can only be deleted if it has zero associated bookings (active, cancelled, or completed). This preserves referential integrity and historical records.

### 7.2 Booking Management Module

**File:** `bookings.py`

**Endpoints:**
| Method | URL | Function |
|--------|-----|----------|
| GET | /bookings/ | List all bookings with filters |
| GET | /bookings/create | Show booking form |
| POST | /bookings/create | Create new booking |
| GET | /bookings/view/:id | View booking details |
| POST | /bookings/cancel/:id | Cancel booking |

**Rental Calculation (Inclusive):**
```
total_days = (end_date - start_date).days + 1
total_amount = total_days × daily_rental_rate
```
Example: 2027-01-10 to 2027-01-12 = 3 days (10th, 11th, 12th).

**Overlap Prevention:**
The system queries for existing active bookings where `start_date <= new_end AND end_date >= new_start`. If found, the booking is rejected. Cancelled bookings are excluded from the overlap check, allowing rebooking of cancelled dates.

**Race Condition Mitigation:**
`BEGIN IMMEDIATE` is used before the overlap check and insert, acquiring a write lock on the database. This reduces (but cannot eliminate in all scenarios) the window for duplicate reservations when multiple users submit simultaneously.

### 7.3 Dashboard Module

**File:** `dashboard.py`

Provides an overview with:
- Total vehicle count and breakdown by status
- Total booking count and breakdown by status
- Total revenue from active and completed bookings
- Last 5 bookings

---

## 8. JIRA Project Management

### 8.1 Project Setup

- **Project Name:** Vehicle Rental System
- **Project Key:** VRS
- **Template:** Scrum

### 8.2 Epics

| Epic | Stories | Tasks |
|------|---------|-------|
| Vehicle Management | 6 | 7 |
| Booking Management | 7 | 8 |
| Testing & Defect Resolution | 3 | 5 |

### 8.3 Sprint

- **Sprint 1:** Core Features & Testing
- **Duration:** 2 weeks
- **Sprint Goal:** Deliver complete Vehicle Management and Booking Management modules with full test coverage.
- **Total Story Points:** ~61

### 8.4 JIRA Artifacts

A complete import-ready CSV file is available at `docs/jira_backlog.csv` with:
- 3 epics
- 18 user stories with acceptance criteria
- 20 tasks

Detailed setup instructions are in `docs/jira_setup_guide.md`.

### 8.5 Defect Tracking

A repeatable defect tracking workflow has been documented:

1. Execute a test (automated or manual)
2. Identify a real defect (test failure or unexpected behavior)
3. Create a JIRA Bug with reproduction steps and expected/actual results
4. Assign severity (Blocker/Critical/Major/Minor/Trivial) and priority
5. Fix the defect in code
6. Retest and record evidence
7. Update JIRA Bug status to Done

**Bug report template** and **severity definitions** are provided in `docs/jira_setup_guide.md`.

**Note:** No actual defects were discovered during automated testing (47/47 passed). The defect tracking workflow and templates are ready for use during manual testing or future development.

---

## 9. Test Strategy and Test Case Results

### 9.1 Test Strategy

- **Framework:** pytest 8.3.3
- **Database Isolation:** Each test uses a fresh temporary SQLite database (via `tempfile.mkstemp`)
- **Test Client:** Flask's built-in test client simulates HTTP requests
- **Approach:** Integration tests that exercise the full request-response cycle through Flask routes
- **Coverage:** Both modules tested for happy paths, error handling, edge cases, and business rules

### 9.2 Test Execution Results

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-8.3.3, pluggy-1.6.0
rootdir: C:\PROJECTS\Vehicle Rental System
collected 47 items

test_vehicles.py   22 passed
test_bookings.py   25 passed

============================= 47 passed in 2.20s ==============================
```

| Module | Tests | Passed | Failed | Pass Rate |
|--------|-------|--------|--------|-----------|
| Vehicle Management | 22 | 22 | 0 | 100% |
| Booking Management | 25 | 25 | 0 | 100% |
| **Total** | **47** | **47** | **0** | **100%** |

### 9.3 Test Coverage Summary

| Category | Tests |
|----------|-------|
| Successful operations | 10 |
| Missing/invalid field validation | 12 |
| Business rule enforcement | 8 |
| Boundary/edge cases | 5 |
| Page rendering | 8 |
| Database persistence | 4 |

Full test case details with IDs, inputs, expected/actual results, and status are documented in `docs/test_cases.md`.

---

## 10. Defects, Fixes, and Retesting Evidence

### Defects Discovered During Automated Testing

**No defects were discovered.** All 47 automated tests passed on the first execution.

This section is reserved for defects found during manual testing or future development. Each defect should be documented using the template in `docs/jira_setup_guide.md`.

### Sample Bug Report Format (For Reference)

If a defect were discovered, it would be documented as:

```
Bug ID: VRS-BUG-001
Summary: [Module] - Brief description
Severity: Major
Priority: High
Status: (Open → In Progress → Fixed → Verified → Closed)

Steps to Reproduce:
1. Navigate to...
2. Enter...
3. Click...

Expected Result: ...
Actual Result: ...

Fix Description: ...
Retest Evidence: Test TC-XXX now passes. (screenshot/log)
```

**Important:** The sample above is a template format, not a claim of an actual defect found. No bugs have been fabricated.

---

## 11. Screenshots and Demonstration

### How to Capture Screenshots

Since this is a locally-run application, capture screenshots during demonstration:

1. Start the application: `python run.py`
2. Open http://127.0.0.1:5000 in a browser
3. Use Windows **Snipping Tool** (Win+Shift+S) or **Print Screen** to capture:
   - Dashboard with statistics
   - Vehicle list with sample data
   - Add vehicle form (empty and with validation errors)
   - Edit vehicle form
   - Booking creation form with rental preview
   - Booking list with active and cancelled bookings
   - Booking detail view
   - Search/filter results
   - Flash messages (success and error)

4. Save screenshots to the `docs/screenshots/` folder.

### Pages Available for Screenshots

| Page | URL | Key Elements |
|------|-----|-------------|
| Dashboard | / | Stat cards, recent bookings |
| Vehicle List | /vehicles/ | Table, search, filters |
| Add Vehicle | /vehicles/add | Form, validation hints |
| Edit Vehicle | /vehicles/edit/1 | Pre-filled form |
| Booking List | /bookings/ | Table, status badges |
| Create Booking | /bookings/create | Vehicle selector, date pickers, preview |
| Booking Detail | /bookings/view/1 | Full details, calculation |

---

## 12. Limitations, Conclusion, and Future Enhancements

### 12.1 Known Limitations

1. **No authentication:** Any user can access all features. There is no login system or role-based access control.
2. **Single-user concurrency:** While BEGIN IMMEDIATE reduces race conditions, SQLite is not designed for high-concurrency production use.
3. **No payment processing:** Rental amounts are calculated but no actual payment gateway is integrated.
4. **No email notifications:** Users are not notified of booking confirmations or cancellations via email.
5. **No file uploads:** Vehicle images or customer documents cannot be uploaded.
6. **Vehicle status not auto-updated:** The vehicle status (available/rented) is not automatically updated based on active bookings. This is a manual field.
7. **No booking completion workflow:** There is no automatic transition from 'active' to 'completed' based on the end date.

### 12.2 Conclusion

The Vehicle Rental System successfully implements the two required functional modules — Vehicle Management and Booking Management — with a polished web interface, robust server-side validation, and comprehensive automated testing. The application demonstrates:

- Full-stack development with Python/Flask
- Database design with SQLite including constraints, foreign keys, and indexes
- Server-side business logic for rental calculation and overlap prevention
- Responsive UI design with modern CSS
- Software quality practices with 47 automated tests (100% pass rate)
- Project management planning with JIRA

### 12.3 Future Enhancements

| Enhancement | Description | Priority |
|-------------|-------------|----------|
| User Authentication | Login system with admin/customer roles | High |
| Auto Status Update | Automatically mark vehicles as rented/available based on bookings | High |
| Booking Completion | Auto-complete bookings when end date passes | Medium |
| Email Notifications | Confirmation emails for bookings and cancellations | Medium |
| Payment Integration | Connect to a payment gateway for online payments | Medium |
| Vehicle Images | Upload and display vehicle photos | Low |
| Multi-location | Support for multiple rental locations | Low |
| Reporting | Export reports in PDF/Excel format | Low |
| Mobile App | Native mobile application | Low |

---

## Appendices

### A. How to Run the Application

```bash
pip install -r requirements.txt
python run.py
# Open http://127.0.0.1:5000
```

### B. How to Run Tests

```bash
python -m pytest -v
```

### C. File Listing

| File | Purpose |
|------|---------|
| `app.py` | Flask application factory |
| `run.py` | Entry point |
| `schema.py` | Database schema |
| `vehicles.py` | Vehicle management blueprint |
| `bookings.py` | Booking management blueprint |
| `dashboard.py` | Dashboard blueprint |
| `conftest.py` | Test fixtures |
| `test_vehicles.py` | Vehicle tests (22) |
| `test_bookings.py` | Booking tests (25) |
| `requirements.txt` | Dependencies |
| `README.md` | Project overview |
| `docs/test_cases.md` | Test case document |
| `docs/project_report.md` | This report |
| `docs/presentation_outline.md` | Presentation slides |
| `docs/jira_backlog.csv` | JIRA import CSV |
| `docs/jira_setup_guide.md` | JIRA setup guide |
| `docs/demo_checklist.md` | Demonstration checklist |
