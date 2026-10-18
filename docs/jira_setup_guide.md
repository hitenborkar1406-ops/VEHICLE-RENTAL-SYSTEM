# JIRA Project Setup Guide — Vehicle Rental System

## Overview

This guide provides step-by-step instructions for setting up the Vehicle Rental System project in JIRA. Since direct JIRA API access was not available during development, a complete import-ready CSV backlog file has been prepared.

---

## Step 1: Create the JIRA Project

1. Log in to your JIRA instance (e.g., `https://your-team.atlassian.net`).
2. Click **Projects** → **Create Project**.
3. Select **Scrum** as the template.
4. Enter:
   - **Project Name:** Vehicle Rental System
   - **Key:** VRS
   - **Description:** A web-based vehicle rental management system for managing vehicles and rental bookings, built with Python, Flask, and SQLite.
5. Click **Create**.

## Step 2: Create Epics

Create three epics manually:

| Epic Name | Description |
|-----------|-------------|
| Vehicle Management | All features related to adding, editing, deleting, searching, and filtering vehicles |
| Booking Management | All features related to creating, viewing, cancelling bookings and enforcing business rules |
| Testing & Defect Resolution | Automated test suite creation, test execution, defect identification, and resolution |

## Step 3: Import the Backlog

### Option A: CSV Import (Recommended)

1. Go to **Project Settings** → **Import Issues** → **CSV**.
2. Upload `docs/jira_backlog.csv`.
3. Map the columns:
   - `Issue Type` → Issue Type
   - `Summary` → Summary
   - `Description` → Description
   - `Epic Link` → Epic Link
   - `Priority` → Priority
   - `Story Points` → Story Points
   - `Acceptance Criteria` → Custom field (create if needed)
   - `Sprint` → Sprint
   - `Status` → Status
4. Review the mapping and import.

### Option B: Manual Entry

Create each user story and task manually using the CSV file as reference. The CSV contains 3 epics, 18 user stories, and 20 tasks.

## Step 4: Create Sprint

1. Go to the **Backlog** view.
2. Click **Create Sprint**.
3. Name it: **Sprint 1 — Core Features & Testing**
4. Sprint Goal: "Deliver complete Vehicle Management and Booking Management modules with full test coverage."
5. Drag all issues into Sprint 1.
6. Set sprint duration: 2 weeks.

## Step 5: Sprint Execution Order

Recommended task sequence within Sprint 1:

### Week 1: Implementation
1. Set up project structure
2. Create database schema
3. Implement vehicle CRUD routes
4. Implement vehicle validation
5. Implement vehicle search and filter
6. Create vehicle HTML templates
7. Implement booking CRUD routes
8. Implement booking validation
9. Implement overlap detection
10. Implement rental calculation
11. Add BEGIN IMMEDIATE for booking creation
12. Create booking HTML templates
13. Build dashboard page
14. Design CSS stylesheet

### Week 2: Testing & Documentation
15. Write conftest.py
16. Write test_vehicles.py
17. Write test_bookings.py
18. Execute test suite and record results
19. Create test case document
20. Create project report
21. Create JIRA backlog CSV

## Step 6: Bug Report Template

When a defect is discovered during testing, create a JIRA Bug issue using this template:

```
Summary: [Module] - Brief description of the defect

Description:
## Environment
- OS: Windows
- Python: 3.12.10
- Browser: (if UI-related)

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Result
What should happen.

## Actual Result
What actually happened.

## Error Output / Screenshots
(Paste error messages or attach screenshots)

## Severity
- Blocker / Critical / Major / Minor / Trivial

## Priority
- Highest / High / Medium / Low / Lowest
```

### Severity Definitions

| Severity | Definition | Example |
|----------|------------|---------|
| Blocker | Application crashes or data loss | Database schema error prevents startup |
| Critical | Core feature broken, no workaround | Bookings cannot be created |
| Major | Feature broken but workaround exists | Search filter returns wrong results |
| Minor | Cosmetic or minor functional issue | Flash message typo |
| Trivial | Very minor, no impact | Alignment issue on mobile |

## Step 7: Defect Tracking Workflow

```
1. Execute test (automated or manual)
     ↓
2. Identify defect (test failure or unexpected behavior)
     ↓
3. Create JIRA Bug issue
   - Title, description, steps, expected/actual
   - Set severity and priority
   - Link to the related story/task
     ↓
4. Assign to developer (self, for individual project)
     ↓
5. Fix the defect in code
     ↓
6. Retest (re-run the failing test)
     ↓
7. Update JIRA Bug status to "Done"
   - Add comment with retest evidence
   - Link to the commit/change
```

---

## Current Status

**No defects were discovered during automated testing.** All 47 test cases passed on the first execution. The JIRA backlog CSV is ready for import. No bug issues need to be created at this time.

If defects are found during manual testing or future development, use the workflow above to track them.
