# Presentation Outline — Vehicle Rental System

## College PBL Evaluation Presentation

**Duration:** 15–20 minutes recommended

---

## Slide 1: Title Slide

- **Title:** Vehicle Rental System
- **Subtitle:** Project-Based Learning — Individual Project
- **Name:** [Your Name]
- **Course / Section:** [Your Course Details]
- **Date:** October 2026

---

## Slide 2: Problem Statement

- Manual or disconnected vehicle rental management leads to:
  - Booking conflicts and double-bookings
  - Inaccurate rental calculations
  - Poor record-keeping
  - No real-time availability checking
- **Solution:** A web-based system with automated conflict prevention and server-side calculations

---

## Slide 3: Objectives

1. Vehicle CRUD with validation and search
2. Booking management with overlap prevention
3. Inclusive rental day calculation & CSV export
4. Responsive web UI with real-time dashboard
5. 82 automated tests (Black-Box + White-Box) with 100% pass rate
6. JIRA project management plan

---

## Slide 4: Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.14, Flask 3.0 |
| Database | SQLite (WAL mode) |
| Frontend | HTML5, CSS3, JavaScript |
| Testing & Coverage | pytest 8.3, coverage.py 7.17, radon (82 tests, 96% coverage) |
| Project Management | JIRA |

- No paid APIs, cloud services, or complex infrastructure
- Zero-configuration SQLite database

---

## Slide 5: Architecture

- Flask application factory with blueprints
- Three modules: Dashboard, Vehicles, Bookings
- SQLite with foreign keys, constraints, and indexes
- Server-rendered Jinja2 templates
- Architecture diagram (from project report)

---

## Slide 6: Database Design

- **vehicles** table: id, registration_number (unique), name, type, daily_rental_rate, status
- **bookings** table: id, vehicle_id (FK), customer_name, dates, total_days, total_amount, status
- ER diagram showing 1:M relationship
- Constraints: CHECK, UNIQUE, FOREIGN KEY

---

## Slide 7: Module 1 — Vehicle Management

- **Demo:** Add → List → Search → Edit → Delete
- Features:
  - 6 vehicle types supported
  - Search by name or registration
  - Filter by type and status
  - Deletion blocked if booking history exists
  - Server-side validation with clear error messages

---

## Slide 8: Module 2 — Booking Management

- **Demo:** Create → View → Cancel → Rebook
- Key business rules:
  - Inclusive calculation: (end − start + 1) × rate
  - Overlapping active bookings prevented
  - Cancelled bookings release dates
  - BEGIN IMMEDIATE for race condition mitigation
  - Price always calculated server-side

---

## Slide 9: Dashboard

- **Demo:** Show dashboard with statistics
- Features:
  - Vehicle count by status (available, rented, maintenance)
  - Booking count by status (active, cancelled, completed)
  - Total revenue
  - Recent bookings table

---

## Slide 10: UI Design

- Dark theme with modern aesthetics
- Inter typography (Google Fonts)
- Responsive layout (desktop + mobile)
- Flash messages for success/error feedback
- Status badges with color coding
- Client-side rental preview (estimate only)
- **Show screenshots or live demo**

---

## Slide 11: Security Practices

- Parameterized SQL queries (no SQL injection)
- Foreign key enforcement (PRAGMA foreign_keys = ON)
- Server-side validation (never trust browser inputs)
- Prices calculated on server (browser values ignored)
- No hard-coded secrets (SECRET_KEY generated at runtime)
- No fake security claims

---

## Slide 12: Dual-Tier Testing Strategy
 
 - **Testing Architecture:** Isolated SQLite database fixtures per test (`conftest.py`)
 - **Total Tests:** 82 Automated Tests across 3 Suites (100% Pass Rate)
 - **1. Black-Box Testing (52 Tests):**
   - 22 Vehicle CRUD, type filtering, registration uniqueness tests
   - 30 Booking workflow, collision blocking, lifecycle completion, and CSV export tests
   - Boundary Value Analysis (BVA) & Equivalence Partitioning (EP)
 - **2. White-Box Testing (30 Tests):**
   - Control Flow Graph (CFG) analysis
   - Basis path testing for `validate_vehicle_data` and `validate_booking_data`
   - McCabe's Cyclomatic Complexity verification ($V(G) = 12$ and $V(G) = 16$)
   - 100% exception handling and guard clause coverage
 
 ---
 
 ## Slide 13: Test Results & Coverage Metrics
 
 ```
 ============================== 82 passed in 1.23s ==============================
 TOTAL Coverage: 96% | Branch Coverage: 93.8% (105/112 branches covered)
 ```
 
 | Module / Suite | Test Type | Tests | Passed | Coverage |
 | :--- | :--- | :--- | :--- | :--- |
 | `test_vehicles.py` | Black-Box Functional | 22 | 22 | 96% |
 | `test_bookings.py` | Black-Box Functional | 30 | 30 | 95% |
 | `test_whitebox.py` | White-Box Basis Paths | 30 | 30 | 100% (helpers/paths) |
 | **Total System** | **Dual-Tier Verification** | **82** | **82** | **96% (100% Pass)** |
 
 - Zero regressions or defects detected across all test executions
 - Visual interactive HTML coverage report available (`htmlcov/index.html`)
 
 ---
 
 ## Slide 14: JIRA Project Management
 
 - **Project:** VRS (Scrum template)
 - **Epics:** Vehicle Management, Booking Management, Testing & Defect Resolution
 - **User Stories:** 18 with acceptance criteria
 - **Tasks:** 20
 - **Sprint 1:** Core Features & Testing (2 weeks)
 - Import-ready CSV backlog prepared
 - Bug report template and defect tracking workflow defined
 
 ---
 
 ## Slide 15: Limitations & Future Enhancements
 
 **Current Limitations:**
 - No user authentication
 - No payment gateway
 - No email notifications
 - Manual vehicle status management
 
 **Future Enhancements:**
 - User login with role-based access
 - Auto-update vehicle status from bookings
 - Payment integration
 - Email notifications
 - Vehicle image uploads
 - Mobile application
 
 ---
 
 ## Slide 16: Conclusion
 
 - Successfully implemented both required modules
 - All functional requirements met
 - 82 automated tests (Black-Box + White-Box) with 100% pass rate
 - 96% statement coverage and 94% branch coverage
 - Professional UI with responsive design
 - Complete JIRA project plan prepared
 - Well-documented codebase
 
 **Thank you!**
 
 ---
 
 ## Slide 17: Q&A
 
 - Live demo available
 - Code walkthrough on request
 - Test execution and coverage reports can be shown live
 
 ---
 
 ## Presenter Notes
 
 1. **Before the presentation:** Run `python3 run.py` and ensure the luxury fleet and sample bookings are loaded for demo.
 2. **During demo:** Show the dashboard first, then vehicles (add → search → edit → try delete with bookings), then bookings (create → view → complete → cancel → export CSV).
 3. **Testing demo:** Run `python3 -m pytest -v` live to show all 82 tests passing.
 4. **White-Box demo:** Run `python3 -m pytest --cov=. --cov-branch` or open `htmlcov/index.html` to show 96% coverage to evaluators.
 5. **Keep slides concise** — most content should come from the live demo.
