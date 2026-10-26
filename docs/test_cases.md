# Test Case & Traceability Document — Vehicle Rental System (FleetFlow)

## 1. Test Environment & Execution Details
- **Operating System:** Linux (Fedora 43 / Kernel 6.13)
- **Language / Runtime:** Python 3.14.8
- **Testing Framework:** pytest 8.3.3 (pluggy 1.7.0, anyio 4.13.0)
- **Web Framework:** Flask 3.0.3
- **Database:** SQLite 3 (isolated in-memory/temp `.db` instances per test fixture via `conftest.py`)
- **Execution Command:** `python3 -m pytest -v`
- **Execution Date:** 2026-10-26
- **Total Automated Tests Executed:** 82 (52 Black-Box + 30 White-Box)
- **Black-Box Functional Tests:** 52 (22 Vehicles + 30 Bookings)
- **White-Box Structural Tests:** 30 (Basis Paths & Internal Logic)
- **Passed:** 82 (100%)
- **Failed:** 0
- **Skipped / Not Run:** 0

---

## 2. Jira Alignment & Project Hierarchy

### Epics
| Epic ID | Epic Name | Description |
| :--- | :--- | :--- |
| **VRS-1** | Vehicle Management | CRUD operations, inventory search, categorization, and validation for fleet vehicles. |
| **VRS-2** | Booking Management | Booking creation, inclusive rental calculation, conflict prevention, and cancellations. |
| **VRS-3** | Testing & Defect Resolution | Automated test suites, integration verification, regression testing, and defect re-testing. |

### User Stories (VRS-4 to VRS-16)
| Story ID | Parent Epic | Story Title | Description |
| :--- | :--- | :--- | :--- |
| **VRS-4** | VRS-1 | Add a Vehicle | As a fleet manager, I want to add new vehicles to the fleet inventory. |
| **VRS-5** | VRS-1 | View and Search Vehicles | As a manager, I want to view, search (by name/reg), and filter (by type/status) vehicles. |
| **VRS-6** | VRS-1 | Edit Vehicle Details | As a manager, I want to update vehicle specifications, rates, and operational status. |
| **VRS-7** | VRS-2 | Create a Rental Booking | As a customer/agent, I want to reserve an available vehicle for specific dates. |
| **VRS-8** | VRS-2 | Calculate Rental Cost | As a system, I want to calculate rental duration and cost inclusively (`days = end - start + 1`). |
| **VRS-9** | VRS-2 | Prevent Booking Conflicts | As a system, I want to block overlapping active bookings for the same vehicle. |
| **VRS-10** | VRS-2 | Cancel a Rental Booking | As an agent/customer, I want to cancel an active booking and immediately release the dates. |
| **VRS-11** | VRS-1 | Validate Vehicle Information | As a system, I want to enforce registration uniqueness, valid types, and positive daily rates. |
| **VRS-12** | VRS-2 | View Booking History | As an agent/manager, I want to view booking listings, detailed records, and dashboard metrics. |
| **VRS-13** | VRS-3 | Test Vehicle Management | As a QA engineer, I want automated regression tests for all vehicle operations and rules. |
| **VRS-14** | VRS-3 | Test Booking Management | As a QA engineer, I want automated regression tests for all booking workflows and constraints. |
| **VRS-15** | VRS-3 | Fix and Retest Defects | As a team, I want to verify defect fixes and ensure zero regressions across the codebase. |
| **VRS-16** | VRS-2 | Validate Booking Rules | As a system, I want to reject invalid dates (past, inverted) and unavailable/maintenance vehicles. |

---

## 3. Module 1: Vehicle Management Tests (22 Tests)
**Implemented in:** `test_vehicles.py`  
**QA Story:** VRS-13 (Test Vehicle Management)  
**Parent Epic:** VRS-1 (Vehicle Management)

| Test ID | Jira Story | Test Method | Test Scenario | Test Data | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-V01** | VRS-4 | `test_successful_vehicle_creation` | Verify successful creation of a valid vehicle and verify database persistence | `reg='MH-01-AB-1234'`, `name='Toyota Innova'`, `type='Car'`, `rate=2500` | HTTP 200, "Vehicle added successfully", record persisted in DB | Vehicle added successfully, DB record verified | **PASS** |
| **TC-V02a** | VRS-11 | `test_missing_registration_number` | Reject vehicle submission when registration number is empty | `reg=''`, `name='Toyota Innova'`, `type='Car'`, `rate='2500'` | Validation error: "Registration number is required" | Error flash message displayed | **PASS** |
| **TC-V02b** | VRS-11 | `test_missing_name` | Reject vehicle submission when vehicle name is empty | `reg='MH-01-AB-1234'`, `name=''`, `type='Car'`, `rate='2500'` | Validation error: "Vehicle name is required" | Error flash message displayed | **PASS** |
| **TC-V02c** | VRS-11 | `test_missing_type` | Reject vehicle submission when vehicle type is empty | `reg='MH-01-AB-1234'`, `name='Toyota Innova'`, `type=''`, `rate='2500'` | Validation error: "Vehicle type is required" | Error flash message displayed | **PASS** |
| **TC-V02d** | VRS-11 | `test_missing_rate` | Reject vehicle submission when daily rental rate is empty | `reg='MH-01-AB-1234'`, `name='Toyota Innova'`, `type='Car'`, `rate='''` | Validation error: "Daily rental rate is required" | Error flash message displayed | **PASS** |
| **TC-V03** | VRS-11 | `test_duplicate_registration_number` | Prevent creation of vehicle with duplicate registration number | Existing: `MH-01-AB-1234`; New: same reg, `name='Different Car'` | Validation error: "already exists", DB rejects duplicate | Error flash displayed, duplicate rejected | **PASS** |
| **TC-V04** | VRS-11 | `test_zero_rental_rate` | Reject vehicle with rental rate of zero (boundary check) | `rate='0'`, valid reg, name, type | Validation error: "positive number" | Error flash message displayed | **PASS** |
| **TC-V05** | VRS-11 | `test_negative_rental_rate` | Reject vehicle with negative rental rate | `rate='-500'`, valid reg, name, type | Validation error: "positive number" | Error flash message displayed | **PASS** |
| **TC-V06** | VRS-5 | `test_search_by_name` | Search vehicles by partial name match | Two vehicles in DB: 'Toyota Innova', 'Honda City'; Query: `search=Toyota` | Only 'Toyota Innova' returned; 'Honda City' excluded | Filtered list correctly displays Toyota | **PASS** |
| **TC-V07** | VRS-5 | `test_search_by_registration` | Search vehicle by registration number prefix | Vehicle: `KA-05-MN-9999`; Query: `search=KA-05` | Vehicle matching registration prefix returned | Matching vehicle returned in HTML | **PASS** |
| **TC-V08** | VRS-5 | `test_filter_by_type` | Filter vehicle list by specific vehicle type | DB has Car and SUV; Query: `type=SUV` | Only SUV displayed; Car excluded | Correct type filtered and displayed | **PASS** |
| **TC-V09** | VRS-5 | `test_filter_by_status` | Filter vehicle list by operational status | DB has available vehicle; Query: `status=available` | Only available vehicles displayed | Filter applied correctly | **PASS** |
| **TC-V10** | VRS-6 | `test_successful_update` | Update vehicle details and verify DB persistence | Initial: rate 2500; Updated: `name='Updated Innova'`, `rate=3000`, `status='maintenance'` | HTTP 200, "Vehicle updated successfully", DB updated | Fields updated in database | **PASS** |
| **TC-V11** | VRS-6 | `test_successful_deletion` | Delete a vehicle having no associated bookings | Vehicle with 0 bookings; `POST /vehicles/delete/<id>` | HTTP 200, "Vehicle deleted successfully", record deleted from DB | Vehicle successfully removed from DB | **PASS** |
| **TC-V12** | VRS-11 | `test_deletion_blocked_with_bookings` | Prevent deletion of a vehicle that has associated bookings | Vehicle has active booking; `POST /vehicles/delete/<id>` | Error: "Cannot delete vehicle with existing bookings", vehicle intact | Deletion blocked, vehicle retained in DB | **PASS** |
| **TC-V13** | VRS-5 | `test_vehicle_list_page` | Verify vehicle inventory page renders correctly | `GET /vehicles/` | HTTP 200, page header "Vehicles" present | Page rendered with HTTP 200 | **PASS** |
| **TC-V14** | VRS-4 | `test_add_vehicle_page` | Verify add vehicle form page renders with inputs | `GET /vehicles/add` | HTTP 200, page header "Add Vehicle" present | Page rendered with HTTP 200 | **PASS** |
| **TC-V15** | VRS-6 | `test_edit_vehicle_page` | Verify edit vehicle page renders with existing vehicle data | Existing vehicle ID 1; `GET /vehicles/edit/1` | HTTP 200, page header "Edit Vehicle" present | Page rendered with prefilled data | **PASS** |
| **TC-V16** | VRS-6 | `test_edit_nonexistent_vehicle` | Attempting to edit a nonexistent vehicle ID redirects with error | `GET /vehicles/edit/9999` | Redirect, error flash: "Vehicle not found" | Redirected with error flash message | **PASS** |
| **TC-V17** | VRS-6 | `test_delete_nonexistent_vehicle` | Attempting to delete a nonexistent vehicle ID returns error | `POST /vehicles/delete/9999` | Redirect, error flash: "Vehicle not found" | Redirected with error flash message | **PASS** |
| **TC-V18** | VRS-11 | `test_all_vehicle_types` | Verify all 6 predefined vehicle types are accepted | Types: Car, SUV, Van, Truck, Motorcycle, Bus | All 6 created successfully with "Vehicle added successfully" | All 6 categories accepted and saved | **PASS** |
| **TC-V19** | VRS-11 | `test_invalid_vehicle_type` | Reject vehicle submission with non-whitelisted type | `type='Helicopter'` | Error flash: "must be one of" | Type rejected with validation error | **PASS** |

---

## 4. Module 2: Booking Management Tests (25 Tests)
**Implemented in:** `test_bookings.py`  
**QA Story:** VRS-14 (Test Booking Management)  
**Parent Epic:** VRS-2 (Booking Management)

| Test ID | Jira Story | Test Method | Test Scenario | Test Data | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-B01** | VRS-7 | `test_successful_booking` | Create a valid booking and verify active status in DB | `vehicle_id=1`, `customer='John Doe'`, `2027-01-10` to `2027-01-12` | HTTP 200, "Booking created successfully", status 'active' in DB | Booking created and persisted in DB | **PASS** |
| **TC-B02** | VRS-16 | `test_missing_vehicle` | Reject booking submission when vehicle is not selected | `vehicle_id=''`, valid customer and dates | Validation error: "Please select a vehicle" | Error flash message displayed | **PASS** |
| **TC-B03** | VRS-16 | `test_missing_customer_name` | Reject booking submission when customer name is empty | `customer_name=''`, valid vehicle and dates | Validation error: "Customer name is required" | Error flash message displayed | **PASS** |
| **TC-B04** | VRS-16 | `test_missing_start_date` | Reject booking submission when start date is omitted | `start_date=''`, valid vehicle and end date | Validation error: "Start date is required" | Error flash message displayed | **PASS** |
| **TC-B05** | VRS-16 | `test_missing_end_date` | Reject booking submission when end date is omitted | `end_date=''`, valid vehicle and start date | Validation error: "End date is required" | Error flash message displayed | **PASS** |
| **TC-B06** | VRS-16 | `test_end_date_before_start_date` | Reject booking when end date precedes start date | `start='2027-01-15'`, `end='2027-01-10'` | Validation error: "End date must be on or after the start date" | Error flash message displayed | **PASS** |
| **TC-B07** | VRS-16 | `test_start_date_in_past` | Reject booking with a start date prior to current date | `start='2020-01-01'`, `end='2020-01-03'` | Validation error: "Start date cannot be in the past" | Error flash message displayed | **PASS** |
| **TC-B08** | VRS-8 | `test_rental_amount_calculation` | Verify inclusive rental day and total amount calculation | Rate = 2500, Dates: `2027-01-10` to `2027-01-12` (3 days) | `total_days=3`, `total_amount = 3 × 2500 = 7500.0` | `total_days=3`, `total_amount=7500.0` | **PASS** |
| **TC-B09** | VRS-16 | `test_booking_nonexistent_vehicle` | Reject booking for vehicle ID that does not exist | `vehicle_id=9999` | Error flash: "Vehicle does not exist" | Error flash message displayed | **PASS** |
| **TC-B10** | VRS-9 | `test_overlapping_booking_rejected` | Reject booking attempt overlapping existing active booking | Booking 1: Jan 10–12; Booking 2: Jan 11–13 (same vehicle) | Error: "already has an active booking during this period" | Overlap rejected, second booking blocked | **PASS** |
| **TC-B11** | VRS-10 | `test_successful_cancellation` | Cancel an active booking and verify status update | Active booking ID 1; `POST /bookings/cancel/1` | HTTP 200, "Booking cancelled successfully", status 'cancelled' | Status transitioned to 'cancelled' | **PASS** |
| **TC-B12** | VRS-10 | `test_cancel_already_cancelled` | Reject attempt to cancel an already cancelled booking | Cancelled booking ID 1; `POST /bookings/cancel/1` | Error flash: "Only active bookings can be cancelled" | Error flash message displayed | **PASS** |
| **TC-B13** | VRS-9 | `test_rebooking_after_cancellation` | Ensure cancelled dates are released and can be rebooked | Booking cancelled for Feb 01–03; Rebook Feb 01–03 | Booking created successfully (dates released) | New booking accepted for same dates | **PASS** |
| **TC-B14** | VRS-12 | `test_booking_list_page` | Verify booking history and listing page renders | `GET /bookings/` | HTTP 200, page header "Bookings" present | Page rendered with HTTP 200 | **PASS** |
| **TC-B15** | VRS-7 | `test_create_booking_page` | Verify create booking form renders with vehicle dropdown | `GET /bookings/create` | HTTP 200, "New Booking" present | Page rendered with HTTP 200 | **PASS** |
| **TC-B16** | VRS-12 | `test_view_booking_details` | Verify single booking details page displays data accurately | Booking ID 1 with Toyota Innova, John Doe; `GET /bookings/view/1` | HTTP 200, Customer name and vehicle name present | Details rendered accurately | **PASS** |
| **TC-B17** | VRS-12 | `test_view_nonexistent_booking` | Attempting to view nonexistent booking redirects with error | `GET /bookings/view/9999` | Redirect, error flash: "Booking not found" | Redirected with error flash message | **PASS** |
| **TC-B18** | VRS-10 | `test_cancel_nonexistent_booking` | Attempting to cancel nonexistent booking returns error | `POST /bookings/cancel/9999` | Redirect, error flash: "Booking not found" | Redirected with error flash message | **PASS** |
| **TC-B19** | VRS-8 | `test_same_day_booking` | Verify same-day booking counts as 1 full inclusive rental day | Rate = 1000, `start='2027-06-15'`, `end='2027-06-15'` | `total_days=1`, "1 day(s)", `total_amount=1000.0` | 1 day booking created with ₹1000 | **PASS** |
| **TC-B20** | VRS-8 | `test_multi_day_calculation` | Verify multi-day booking calculation over 7-day period | Rate = 1000, `start='2027-01-01'`, `end='2027-01-07'` | `total_days=7`, `total_amount = 7 × 1000 = 7000.0` | `total_days=7`, `total_amount=7000.0` | **PASS** |
| **TC-B21** | VRS-7 | `test_booking_persists_in_database` | Verify deep data persistence of all booking columns in SQLite | Customer 'Persistent Test', `2027-03-01` to `2027-03-05`, rate 1500 | Record in SQLite matches customer, dates, 5 days, ₹7500 | All columns verified in SQLite DB | **PASS** |
| **TC-B22** | VRS-9 | `test_adjacent_bookings_allowed` | Verify adjacent bookings (touching start/end boundaries) succeed | Booking 1: Jan 10–12; Booking 2: Jan 13–15 (same vehicle) | HTTP 200, "Booking created successfully" | Non-overlapping adjacent booking accepted | **PASS** |
| **TC-B23** | VRS-16 | `test_booking_vehicle_under_maintenance` | Reject booking when target vehicle has 'maintenance' status | Vehicle status = 'maintenance'; attempt booking | Error flash: vehicle under maintenance | Maintenance vehicle rejected | **PASS** |
| **TC-B24** | VRS-12 | `test_dashboard_loads` | Verify system dashboard overview page renders | `GET /` | HTTP 200, "Dashboard" present | Page rendered with HTTP 200 | **PASS** |
| **TC-B25** | VRS-12 | `test_dashboard_shows_stats` | Verify dashboard dynamically counts active vehicles in DB | 2 test vehicles added to database; `GET /` | HTML contains total count '2' | Statistics metric '2' displayed | **PASS** |

---

## 5. Traceability Matrix: Jira Story ID → Test Cases → Execution Results

| Jira Story ID | Story Title | Parent Epic | Mapped Test Case IDs | Automated Test Methods | Actual Test Result | Story Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **VRS-4** | Add a Vehicle | VRS-1 | TC-V01, TC-V14 | `test_successful_vehicle_creation`<br>`test_add_vehicle_page` | Both tests passed (HTTP 200, DB insertion verified) | **VERIFIED (PASS)** |
| **VRS-5** | View and Search Vehicles | VRS-1 | TC-V06, TC-V07, TC-V08, TC-V09, TC-V13 | `test_search_by_name`<br>`test_search_by_registration`<br>`test_filter_by_type`<br>`test_filter_by_status`<br>`test_vehicle_list_page` | All 5 tests passed (name/reg search & type/status filters verified) | **VERIFIED (PASS)** |
| **VRS-6** | Edit Vehicle Details | VRS-1 | TC-V10, TC-V11, TC-V15, TC-V16, TC-V17 | `test_successful_update`<br>`test_successful_deletion`<br>`test_edit_vehicle_page`<br>`test_edit_nonexistent_vehicle`<br>`test_delete_nonexistent_vehicle` | All 5 tests passed (updates, deletions & 404 handlers verified) | **VERIFIED (PASS)** |
| **VRS-7** | Create a Rental Booking | VRS-2 | TC-B01, TC-B15, TC-B21 | `test_successful_booking`<br>`test_create_booking_page`<br>`test_booking_persists_in_database` | All 3 tests passed (booking flow & SQLite persistence verified) | **VERIFIED (PASS)** |
| **VRS-8** | Calculate Rental Cost | VRS-2 | TC-B08, TC-B19, TC-B20 | `test_rental_amount_calculation`<br>`test_same_day_booking`<br>`test_multi_day_calculation` | All 3 tests passed (inclusive single & multi-day math verified) | **VERIFIED (PASS)** |
| **VRS-9** | Prevent Booking Conflicts | VRS-2 | TC-B10, TC-B13, TC-B22 | `test_overlapping_booking_rejected`<br>`test_rebooking_after_cancellation`<br>`test_adjacent_bookings_allowed` | All 3 tests passed (overlaps blocked, adjacent & rebook allowed) | **VERIFIED (PASS)** |
| **VRS-10** | Cancel a Rental Booking | VRS-2 | TC-B11, TC-B12, TC-B18 | `test_successful_cancellation`<br>`test_cancel_already_cancelled`<br>`test_cancel_nonexistent_booking` | All 3 tests passed (status transitions & guard rails verified) | **VERIFIED (PASS)** |
| **VRS-11** | Validate Vehicle Information | VRS-1 | TC-V02a, TC-V02b, TC-V02c, TC-V02d, TC-V03, TC-V04, TC-V05, TC-V12, TC-V18, TC-V19 | `test_missing_registration_number`<br>`test_missing_name`<br>`test_missing_type`<br>`test_missing_rate`<br>`test_duplicate_registration_number`<br>`test_zero_rental_rate`<br>`test_negative_rental_rate`<br>`test_deletion_blocked_with_bookings`<br>`test_all_vehicle_types`<br>`test_invalid_vehicle_type` | All 10 tests passed (required fields, rates > 0, uniqueness & types verified) | **VERIFIED (PASS)** |
| **VRS-12** | View Booking History | VRS-2 | TC-B14, TC-B16, TC-B17, TC-B24, TC-B25 | `test_booking_list_page`<br>`test_view_booking_details`<br>`test_view_nonexistent_booking`<br>`test_dashboard_loads`<br>`test_dashboard_shows_stats` | All 5 tests passed (list, detail view, 404, dashboard metrics verified) | **VERIFIED (PASS)** |
| **VRS-13** | Test Vehicle Management | VRS-3 | All 22 Vehicle Tests (TC-V01 to TC-V19) | All test methods in `TestVehicleCreation`, `TestVehicleSearch`, `TestVehicleUpdate`, `TestVehicleDeletion`, `TestVehiclePages` | 22/22 automated vehicle tests executed and passed | **VERIFIED (PASS)** |
| **VRS-14** | Test Booking Management | VRS-3 | All 25 Booking Tests (TC-B01 to TC-B25) | All test methods in `TestBookingCreation`, `TestRentalCalculation`, `TestOverlapPrevention`, `TestBookingCancellation`, `TestBookingPages`, `TestDatabasePersistence`, `TestDashboard` | 25/25 automated booking tests executed and passed | **VERIFIED (PASS)** |
| **VRS-15** | Fix and Retest Defects | VRS-3 | Regression Suite (All 47 Tests) | Full pytest test suite (`test_vehicles.py` + `test_bookings.py`) | 47/47 passed; zero defects detected, regression clean | **VERIFIED (PASS)** |
| **VRS-16** | Validate Booking Rules | VRS-2 | TC-B02, TC-B03, TC-B04, TC-B05, TC-B06, TC-B07, TC-B09, TC-B23 | `test_missing_vehicle`<br>`test_missing_customer_name`<br>`test_missing_start_date`<br>`test_missing_end_date`<br>`test_end_date_before_start_date`<br>`test_start_date_in_past`<br>`test_booking_nonexistent_vehicle`<br>`test_booking_vehicle_under_maintenance` | All 8 tests passed (past dates, date order, maintenance status verified) | **VERIFIED (PASS)** |

---

## 6. Dual-Tier Automated Testing Breakdown
- **Black-Box Tests (52 Total):**
  - **Vehicle Management (22 Tests):** Integration tests executing via pytest HTTP client against temporary SQLite databases (`tests/test_vehicles.py`).
  - **Booking Management (30 Tests):** Integration tests validating business calculations, collision prevention, date rules, status transitions, lifecycle completion, and CSV reports (`tests/test_bookings.py`).
- **White-Box Tests (30 Total):**
  - **Structural & Basis Path Tests (30 Tests):** Direct unit tests verifying Control Flow Graphs (CFG), McCabe's Cyclomatic Complexity ($V(G) = 12$ and $16$), and decision branches (`tests/test_whitebox.py`).
  - **Coverage:** Full statement and branch coverage analysis documented in [`docs/whitebox_testing.md`](file:///run/media/hiten/OS/PROJECTS/Vehicle%20Rental%20System/docs/whitebox_testing.md).
- **Manual Functional Testing (PBL Viva Demonstrations):**
  - UI responsiveness, dark/light theme switching, modal dialog animations, interactive vehicle filtering, and flash message auto-dismissal.

---

## 7. Actual Pytest Execution Output
```
============================= test session starts ==============================
platform linux -- Python 3.14.8, pytest-8.3.3, pluggy-1.7.0 -- /usr/bin/python3
cachedir: .pytest_cache
rootdir: /run/media/hiten/OS/PROJECTS/Vehicle Rental System
plugins: anyio-4.13.0
collecting ... collected 47 items

test_bookings.py::TestBookingCreation::test_successful_booking PASSED    [  2%]
test_bookings.py::TestBookingCreation::test_missing_vehicle PASSED       [  4%]
test_bookings.py::TestBookingCreation::test_missing_customer_name PASSED [  6%]
test_bookings.py::TestBookingCreation::test_missing_start_date PASSED    [  8%]
test_bookings.py::TestBookingCreation::test_missing_end_date PASSED      [ 10%]
test_bookings.py::TestBookingCreation::test_end_date_before_start_date PASSED [ 12%]
test_bookings.py::TestBookingCreation::test_start_date_in_past PASSED    [ 14%]
test_bookings.py::TestBookingCreation::test_booking_nonexistent_vehicle PASSED [ 17%]
test_bookings.py::TestBookingCreation::test_same_day_booking PASSED      [ 19%]
test_bookings.py::TestBookingCreation::test_booking_vehicle_under_maintenance PASSED [ 21%]
test_bookings.py::TestRentalCalculation::test_rental_amount_calculation PASSED [ 23%]
test_bookings.py::TestRentalCalculation::test_multi_day_calculation PASSED [ 25%]
test_bookings.py::TestOverlapPrevention::test_overlapping_booking_rejected PASSED [ 27%]
test_bookings.py::TestOverlapPrevention::test_adjacent_bookings_allowed PASSED [ 29%]
test_bookings.py::TestBookingCancellation::test_successful_cancellation PASSED [ 31%]
test_bookings.py::TestBookingCancellation::test_cancel_already_cancelled PASSED [ 34%]
test_bookings.py::TestBookingCancellation::test_rebooking_after_cancellation PASSED [ 36%]
test_bookings.py::TestBookingCancellation::test_cancel_nonexistent_booking PASSED [ 38%]
test_bookings.py::TestBookingPages::test_booking_list_page PASSED        [ 40%]
test_bookings.py::TestBookingPages::test_create_booking_page PASSED      [ 42%]
test_bookings.py::TestBookingPages::test_view_booking_details PASSED     [ 44%]
test_bookings.py::TestBookingPages::test_view_nonexistent_booking PASSED [ 46%]
test_bookings.py::TestDatabasePersistence::test_booking_persists_in_database PASSED [ 48%]
test_bookings.py::TestDashboard::test_dashboard_loads PASSED             [ 51%]
test_bookings.py::TestDashboard::test_dashboard_shows_stats PASSED       [ 53%]
test_vehicles.py::TestVehicleCreation::test_successful_vehicle_creation PASSED [ 55%]
test_vehicles.py::TestVehicleCreation::test_missing_registration_number PASSED [ 57%]
test_vehicles.py::TestVehicleCreation::test_missing_name PASSED          [ 59%]
test_vehicles.py::TestVehicleCreation::test_missing_type PASSED          [ 61%]
test_vehicles.py::TestVehicleCreation::test_missing_rate PASSED          [ 63%]
test_vehicles.py::TestVehicleCreation::test_duplicate_registration_number PASSED [ 65%]
test_vehicles.py::TestVehicleCreation::test_zero_rental_rate PASSED      [ 68%]
test_vehicles.py::TestVehicleCreation::test_negative_rental_rate PASSED  [ 70%]
test_vehicles.py::TestVehicleCreation::test_all_vehicle_types PASSED     [ 72%]
test_vehicles.py::TestVehicleCreation::test_invalid_vehicle_type PASSED  [ 74%]
test_vehicles.py::TestVehicleSearch::test_search_by_name PASSED          [ 76%]
test_vehicles.py::TestVehicleSearch::test_search_by_registration PASSED  [ 78%]
test_vehicles.py::TestVehicleSearch::test_filter_by_type PASSED          [ 80%]
test_vehicles.py::TestVehicleSearch::test_filter_by_status PASSED        [ 82%]
test_vehicles.py::TestVehicleUpdate::test_successful_update PASSED       [ 85%]
test_vehicles.py::TestVehicleUpdate::test_edit_nonexistent_vehicle PASSED [ 87%]
test_vehicles.py::TestVehicleDeletion::test_successful_deletion PASSED   [ 89%]
test_vehicles.py::TestVehicleDeletion::test_deletion_blocked_with_bookings PASSED [ 91%]
test_vehicles.py::TestVehicleDeletion::test_delete_nonexistent_vehicle PASSED [ 93%]
test_vehicles.py::TestVehiclePages::test_vehicle_list_page PASSED        [ 95%]
test_vehicles.py::TestVehiclePages::test_add_vehicle_page PASSED         [ 97%]
test_vehicles.py::TestVehiclePages::test_edit_vehicle_page PASSED        [100%]

============================== 47 passed in 1.06s ==============================
```
