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
3. Inclusive rental day calculation
4. Responsive web UI with dashboard
5. 47 automated tests with 100% pass rate
6. JIRA project management plan

---

## Slide 4: Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.12, Flask 3.0 |
| Database | SQLite (WAL mode) |
| Frontend | HTML5, CSS3, JavaScript |
| Testing | pytest (47 tests) |
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

## Slide 12: Testing Strategy

- **Framework:** pytest with isolated temp databases
- **Total Tests:** 47 (22 vehicle + 25 booking)
- **Pass Rate:** 100% (47/47)
- Categories covered:
  - CRUD operations
  - Validation (required fields, types, ranges)
  - Business rules (overlaps, deletion constraints)
  - Edge cases (same-day booking, adjacent dates)
  - Page rendering
  - Database persistence

---

## Slide 13: Test Results

```
47 passed in 2.20 seconds
```

| Module | Tests | Passed | Failed |
|--------|-------|--------|--------|
| Vehicle Management | 22 | 22 | 0 |
| Booking Management | 25 | 25 | 0 |

- No defects discovered during automated testing
- All results are from actual execution (not fabricated)

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
- 47 automated tests with 100% pass rate
- Professional UI with responsive design
- Complete JIRA project plan prepared
- Well-documented codebase

**Thank you!**

---

## Slide 17: Q&A

- Live demo available
- Code walkthrough on request
- Test execution can be shown live

---

## Presenter Notes

1. **Before the presentation:** Run `python run.py` and add 2-3 sample vehicles and bookings for demo data.
2. **During demo:** Show the dashboard first, then vehicles (add → search → edit → try delete with bookings), then bookings (create → view → cancel → rebook same dates).
3. **Testing demo:** Run `python -m pytest -v` live to show all 47 tests passing.
4. **Keep slides concise** — most content should come from the live demo.
