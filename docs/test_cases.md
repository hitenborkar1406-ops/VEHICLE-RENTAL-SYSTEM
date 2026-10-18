# Test Case Document — Vehicle Rental System

## Test Environment
- **Python:** 3.12.10
- **pytest:** 8.3.3
- **Flask:** 3.0.3
- **Database:** SQLite (isolated temp databases per test)
- **Test Execution Date:** 2026-10-11
- **Total Tests:** 47
- **Passed:** 47
- **Failed:** 0

---

## Module 1: Vehicle Management Tests (22 tests)

| Test ID | Test Case | Preconditions | Input | Expected Result | Actual Result | Status |
|---------|-----------|---------------|-------|-----------------|---------------|--------|
| TC-V01 | Successful vehicle creation | Empty database | reg=MH-01-AB-1234, name=Toyota Innova, type=Car, rate=2500 | Vehicle created, stored in DB with correct fields | Vehicle created successfully, all fields match | ✅ PASS |
| TC-V02a | Missing registration number | None | reg=(empty) | Error: "Registration number is required" | Error displayed correctly | ✅ PASS |
| TC-V02b | Missing vehicle name | None | name=(empty) | Error: "Vehicle name is required" | Error displayed correctly | ✅ PASS |
| TC-V02c | Missing vehicle type | None | type=(empty) | Error: "Vehicle type is required" | Error displayed correctly | ✅ PASS |
| TC-V02d | Missing rental rate | None | rate=(empty) | Error: "Daily rental rate is required" | Error displayed correctly | ✅ PASS |
| TC-V03 | Duplicate registration number | Vehicle MH-01-AB-1234 exists | Same reg number, different name | Error: "already exists" | Error displayed correctly | ✅ PASS |
| TC-V04 | Zero rental rate | None | rate=0 | Error: "positive number" | Error displayed correctly | ✅ PASS |
| TC-V05 | Negative rental rate | None | rate=-500 | Error: "positive number" | Error displayed correctly | ✅ PASS |
| TC-V06 | Search by name | Two vehicles in DB | search="Toyota" | Only Toyota result shown | Correct vehicle returned | ✅ PASS |
| TC-V07 | Search by registration | Vehicle KA-05-MN-9999 exists | search="KA-05" | Matching vehicle found | Correct vehicle returned | ✅ PASS |
| TC-V08 | Filter by type | Car and SUV in DB | type=SUV | Only SUV shown | Correct filter applied | ✅ PASS |
| TC-V09 | Filter by status | Available vehicle exists | status=available | Only available shown | Correct filter applied | ✅ PASS |
| TC-V10 | Successful update | Vehicle exists | Updated fields | Vehicle updated in DB | All fields updated correctly | ✅ PASS |
| TC-V11 | Successful deletion (no bookings) | Vehicle with no bookings | Delete request | Vehicle removed from DB | Vehicle deleted, verified null | ✅ PASS |
| TC-V12 | Deletion blocked (has bookings) | Vehicle with booking history | Delete request | Error: "Cannot delete" | Error displayed, vehicle intact | ✅ PASS |
| TC-V13 | Vehicle list page loads | None | GET /vehicles/ | 200 with "Vehicle Management" | Page loads correctly | ✅ PASS |
| TC-V14 | Add vehicle page loads | None | GET /vehicles/add | 200 with "Add New Vehicle" | Page loads correctly | ✅ PASS |
| TC-V15 | Edit vehicle page loads | Vehicle exists | GET /vehicles/edit/1 | 200 with "Edit Vehicle" | Page loads with data | ✅ PASS |
| TC-V16 | Edit nonexistent vehicle | No vehicle id=9999 | GET /vehicles/edit/9999 | Error: "Vehicle not found" | Error displayed correctly | ✅ PASS |
| TC-V17 | Delete nonexistent vehicle | No vehicle id=9999 | POST /vehicles/delete/9999 | Error: "Vehicle not found" | Error displayed correctly | ✅ PASS |
| TC-V18 | All vehicle types accepted | None | Each of 6 types | All created successfully | All 6 types accepted | ✅ PASS |
| TC-V19 | Invalid vehicle type rejected | None | type=Helicopter | Error: "must be one of" | Error displayed correctly | ✅ PASS |

---

## Module 2: Booking Management Tests (25 tests)

| Test ID | Test Case | Preconditions | Input | Expected Result | Actual Result | Status |
|---------|-----------|---------------|-------|-----------------|---------------|--------|
| TC-B01 | Successful booking creation | Vehicle exists | vehicle_id=1, customer=John, dates=2027-01-10 to 2027-01-12 | Booking created with status active | Booking created successfully | ✅ PASS |
| TC-B02 | Missing vehicle selection | None | vehicle_id=(empty) | Error: "Please select a vehicle" | Error displayed correctly | ✅ PASS |
| TC-B03 | Missing customer name | Vehicle exists | customer=(empty) | Error: "Customer name is required" | Error displayed correctly | ✅ PASS |
| TC-B04 | Missing start date | Vehicle exists | start_date=(empty) | Error: "Start date is required" | Error displayed correctly | ✅ PASS |
| TC-B05 | Missing end date | Vehicle exists | end_date=(empty) | Error: "End date is required" | Error displayed correctly | ✅ PASS |
| TC-B06 | End date before start date | Vehicle exists | start=2027-01-15, end=2027-01-10 | Error: "End date must be on or after" | Error displayed correctly | ✅ PASS |
| TC-B07 | Start date in past | Vehicle exists | start=2020-01-01 | Error: "Start date cannot be in the past" | Error displayed correctly | ✅ PASS |
| TC-B08 | Rental amount calculation | Vehicle rate=2500 | dates=2027-01-10 to 2027-01-12 | 3 days × ₹2500 = ₹7500 | total_days=3, total_amount=7500.0 | ✅ PASS |
| TC-B09 | Booking nonexistent vehicle | No vehicle id=9999 | vehicle_id=9999 | Error: "does not exist" | Error displayed correctly | ✅ PASS |
| TC-B10 | Overlapping booking rejected | Active booking Jan 10–12 | Same vehicle, Jan 11–13 | Error: "already has an active booking" | Overlap detected and rejected | ✅ PASS |
| TC-B11 | Successful cancellation | Active booking exists | Cancel request | Status → cancelled | Status changed to cancelled | ✅ PASS |
| TC-B12 | Cancel already cancelled | Cancelled booking | Cancel request again | Error: "Only active bookings" | Error displayed correctly | ✅ PASS |
| TC-B13 | Rebooking after cancellation | Booking cancelled | Same dates, new customer | Booking created successfully | Dates released and rebooked | ✅ PASS |
| TC-B14 | Booking list page loads | None | GET /bookings/ | 200 with "Booking Management" | Page loads correctly | ✅ PASS |
| TC-B15 | Create booking page loads | None | GET /bookings/create | 200 with "Create New Booking" | Page loads correctly | ✅ PASS |
| TC-B16 | View booking details | Booking exists | GET /bookings/view/1 | 200 with customer and vehicle info | All details displayed | ✅ PASS |
| TC-B17 | View nonexistent booking | No booking id=9999 | GET /bookings/view/9999 | Error: "Booking not found" | Error displayed correctly | ✅ PASS |
| TC-B18 | Cancel nonexistent booking | No booking id=9999 | POST /bookings/cancel/9999 | Error: "Booking not found" | Error displayed correctly | ✅ PASS |
| TC-B19 | Same-day booking (1 day) | Vehicle rate=1000 | start=end=2027-06-15 | 1 day, ₹1000 | 1 day booking created | ✅ PASS |
| TC-B20 | Multi-day calculation | Vehicle rate=1000 | dates=2027-01-01 to 2027-01-07 | 7 days × ₹1000 = ₹7000 | total_days=7, total_amount=7000.0 | ✅ PASS |
| TC-B21 | Database persistence | Vehicle rate=1500 | Full booking data | All fields persisted correctly | All fields verified in DB | ✅ PASS |
| TC-B22 | Adjacent bookings allowed | Booking Jan 10–12 | Same vehicle, Jan 13–15 | No overlap, booking created | Adjacent booking accepted | ✅ PASS |
| TC-B23 | Booking vehicle under maintenance | Vehicle status=maintenance | Booking request | Error about maintenance | Maintenance vehicle rejected | ✅ PASS |
| TC-B24 | Dashboard loads | None | GET / | 200 with "Dashboard" | Page loads correctly | ✅ PASS |
| TC-B25 | Dashboard shows stats | 2 vehicles added | GET / | Count of 2 displayed | Statistics shown correctly | ✅ PASS |

---

## Test Execution Summary

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-8.3.3, pluggy-1.6.0
rootdir: C:\PROJECTS\Vehicle Rental System
collected 47 items

test_vehicles.py   22 passed
test_bookings.py   25 passed

============================= 47 passed in 2.20s ==============================
```

**No defects were discovered during automated testing.** All 47 test cases passed on the first execution run.
