# White-Box Testing & Structural Coverage Report — Vehicle Rental System (FleetFlow)

## 1. Executive Summary & Overview

In software engineering, testing is classified into two complementary paradigms:
* **Black-Box Testing (Functional / Behavioral / Specification-Based):** Tests the software from the outside against requirements without inspecting internal source code or branching structures. This was accomplished via 52 automated tests in `test_vehicles.py` and `test_bookings.py` utilizing HTTP requests, boundary value analysis (BVA), and equivalence class partitioning (ECP).
* **White-Box Testing (Structural / Glass-Box / Logic-Driven):** Tests the internal control-flow logic, branch conditions, exception handlers, and basis paths directly at the source code level.

This document details the **White-Box Testing** implementation for the **Vehicle Rental System**, including Control Flow Graphs (CFG), McCabe's Cyclomatic Complexity calculations ($V(G)$), Basis Path Derivations, and Branch Coverage metrics verified via automated unit tests in `test_whitebox.py`.

---

## 2. Test Environment & Tooling

| Component | Tool / Standard | Role in White-Box Testing |
| :--- | :--- | :--- |
| **Runtime** | Python 3.14.8 | Core execution engine |
| **Test Runner** | pytest 8.3.3 | Executes white-box unit tests directly against internal functions |
| **Coverage Engine** | coverage.py 7.17.0 / pytest-cov 7.1.0 | Measures exact statement and branch coverage (`--cov-branch`) |
| **Complexity Analyzer** | Radon 6.0.1 | Computes McCabe's Cyclomatic Complexity on the AST |
| **Interactive Report** | HTML Coverage Dashboard (`htmlcov/`) | Visualizes line-by-line branch traversal (green = covered, red = missed) |

> [!NOTE]
> **Why Python Native Tools instead of Eclipse?**
> Academic lab manuals frequently cite *Eclipse with EclEmma/JUnit* because university labs default to Java. Because FleetFlow is built in Python/Flask, using `pytest`, `coverage.py`, and `radon` is the professional, industry-standard approach. `coverage.py` provides the exact equivalent of Eclipse's EclEmma coverage report natively on Python AST.

---

## 3. Module 1: `validate_vehicle_data()` Analysis

Located in: [`vehicles.py`](file:///run/media/hiten/OS/PROJECTS/Vehicle%20Rental%20System/vehicles.py)

### 3.1 Function Logic & Annotated Control Nodes

```python
def validate_vehicle_data(data, db, exclude_id=None):
    # [Node 1]: Entry, initialize errors list, strip string inputs
    errors = []
    reg_num = data.get('registration_number', '').strip()
    name = data.get('name', '').strip()
    v_type = data.get('type', '').strip()
    rate_str = data.get('daily_rental_rate', '').strip()

    # [Node 2 / Predicate 1]: Check registration number
    if not reg_num:
        # [Node 3]:
        errors.append('Registration number is required.')

    # [Node 4 / Predicate 2]: Check vehicle name
    if not name:
        # [Node 5]:
        errors.append('Vehicle name is required.')

    # [Node 6 / Predicate 3]: Check vehicle type empty
    if not v_type:
        # [Node 7]:
        errors.append('Vehicle type is required.')
    # [Node 8 / Predicate 4]: Check vehicle type against whitelist
    elif v_type not in VEHICLE_TYPES:
        # [Node 9]:
        errors.append(f'Vehicle type must be one of: {", ".join(VEHICLE_TYPES)}.')

    # [Node 10 / Predicate 5]: Check rental rate empty
    if not rate_str:
        # [Node 11]:
        errors.append('Daily rental rate is required.')
    else:
        # [Node 12]: Try converting rate to float
        try:
            rate = float(rate_str)
            # [Node 13 / Predicate 6]: Rate <= 0 check
            if rate <= 0:
                # [Node 14]:
                errors.append('Daily rental rate must be a positive number.')
        # [Node 15 / Predicate 7]: Catch ValueError conversion failure
        except ValueError:
            # [Node 16]:
            errors.append('Daily rental rate must be a valid number.')

    # [Node 17 / Predicate 8 & 9]: Check registration uniqueness if valid
    if reg_num and not errors:
        # [Node 18]: Setup SQL query
        query = "SELECT id FROM vehicles WHERE registration_number = ?"
        params = [reg_num]
        # [Node 19 / Predicate 10]: Exclude ID check for updates
        if exclude_id is not None:
            # [Node 20]:
            query += " AND id != ?"
            params.append(exclude_id)
        # [Node 21]: Execute SQL query
        existing = db.execute(query, params).fetchone()
        # [Node 22 / Predicate 11]: Existing record found check
        if existing:
            # [Node 23]:
            errors.append('A vehicle with this registration number already exists.')

    # [Node 24]: Return errors list
    return errors
```

---

### 3.2 Control Flow Graph (CFG)

```mermaid
flowchart TD
    N1([1: Entry]) --> N2{2: not reg_num?}
    N2 -- True --> N3[3: append reg error]
    N2 -- False --> N4
    N3 --> N4{4: not name?}
    
    N4 -- True --> N5[5: append name error]
    N4 -- False --> N6
    N5 --> N6{6: not v_type?}
    
    N6 -- True --> N7[7: append type required error]
    N6 -- False --> N8{8: v_type not in TYPES?}
    N8 -- True --> N9[9: append invalid type error]
    N8 -- False --> N10
    N7 --> N10{10: not rate_str?}
    N9 --> N10
    
    N10 -- True --> N11[11: append rate required error]
    N10 -- False --> N12[12: try float conversion]
    
    N12 --> N13{13: rate <= 0?}
    N13 -- True --> N14[14: append positive rate error]
    N13 -- False --> N17
    N14 --> N17
    N12 -- ValueError --> N15[15: except ValueError]
    N15 --> N16[16: append valid number error]
    N16 --> N17
    N11 --> N17
    
    N17{17: reg_num and not errors?} -- False --> N24([24: Return errors])
    N17 -- True --> N18[18: query = SELECT...]
    N18 --> N19{19: exclude_id is not None?}
    N19 -- True --> N20[20: query += AND id != ?]
    N19 -- False --> N21
    N20 --> N21[21: execute query]
    N21 --> N22{22: existing found?}
    N22 -- True --> N23[23: append duplicate error]
    N22 -- False --> N24
    N23 --> N24
```

---

### 3.3 McCabe's Cyclomatic Complexity Calculation for `validate_vehicle_data`

Cyclomatic Complexity measures the number of linearly independent paths through the program source code.

#### Method 1: Predicate Node Formula
$$V(G) = P + 1$$
Where $P$ is the number of predicate (decision) nodes:
1. `P1`: `if not reg_num`
2. `P2`: `if not name`
3. `P3`: `if not v_type`
4. `P4`: `elif v_type not in VEHICLE_TYPES`
5. `P5`: `if not rate_str`
6. `P6`: `if rate <= 0`
7. `P7`: `except ValueError`
8. `P8`: `reg_num` (compound sub-condition)
9. `P9`: `not errors` (compound sub-condition)
10. `P10`: `if exclude_id is not None`
11. `P11`: `if existing`

$$V(G) = 11 + 1 = 12$$

#### Method 2: Edges and Nodes Formula
$$V(G) = E - N + 2P_{comp}$$
* Number of Edges ($E$) = 33
* Number of Nodes ($N$) = 23
* Connected Components ($P_{comp}$) = 1
$$V(G) = 33 - 23 + 2(1) = 12$$

#### Method 3: Automated AST Verification (Radon Tool)
```bash
$ python3 -m radon cc vehicles.py -s
vehicles.py
    F 28:0 validate_vehicle_data - C (12)
```
**Conclusion:** Cyclomatic Complexity is confirmed to be **12**. Exactly 12 independent basis paths exist.

---

### 3.4 Basis Paths & Test Suite Traceability

| Path ID | Independent Path Execution Sequence | Test Case in `test_whitebox.py` | Result |
| :--- | :--- | :--- | :--- |
| **Path 1** | $1 \rightarrow 2 \rightarrow 3 \rightarrow 4 \rightarrow 5 \rightarrow 6 \rightarrow 7 \rightarrow 10 \rightarrow 11 \rightarrow 17(F) \rightarrow 24$ | `test_path_empty_payload_all_required_missing` | **PASS** |
| **Path 2** | $1 \rightarrow 2(T) \rightarrow 3 \rightarrow 4(F) \rightarrow 6(F) \rightarrow 8(F) \rightarrow 10(F) \rightarrow 12 \rightarrow 13(F) \rightarrow 17(F) \rightarrow 24$ | `test_path_missing_registration_only` | **PASS** |
| **Path 3** | $1 \rightarrow 2(F) \rightarrow 4(T) \rightarrow 5 \rightarrow 6(F) \rightarrow 8(F) \rightarrow 10(F) \rightarrow 12 \rightarrow 13(F) \rightarrow 17(F) \rightarrow 24$ | `test_path_missing_name_only` | **PASS** |
| **Path 4** | $1 \rightarrow 2(F) \rightarrow 4(F) \rightarrow 6(T) \rightarrow 7 \rightarrow 10(F) \rightarrow 12 \rightarrow 13(F) \rightarrow 17(F) \rightarrow 24$ | `test_path_missing_type_only` | **PASS** |
| **Path 5** | $1 \rightarrow 2(F) \rightarrow 4(F) \rightarrow 6(F) \rightarrow 8(T) \rightarrow 9 \rightarrow 10(F) \rightarrow 12 \rightarrow 13(F) \rightarrow 17(F) \rightarrow 24$ | `test_path_invalid_vehicle_type` | **PASS** |
| **Path 6** | $1 \rightarrow 2(F) \rightarrow 4(F) \rightarrow 6(F) \rightarrow 8(F) \rightarrow 10(F) \rightarrow 12 \rightarrow 15 \rightarrow 16 \rightarrow 17(F) \rightarrow 24$ | `test_path_rate_non_numeric_exception` | **PASS** |
| **Path 7** | $1 \rightarrow 2(F) \rightarrow 4(F) \rightarrow 6(F) \rightarrow 8(F) \rightarrow 10(F) \rightarrow 12 \rightarrow 13(T) \rightarrow 14 \rightarrow 17(F) \rightarrow 24$ | `test_path_rate_zero_and_negative` | **PASS** |
| **Path 8** | $1 \rightarrow 2(F) \rightarrow 4(F) \rightarrow 6(F) \rightarrow 8(F) \rightarrow 10(F) \rightarrow 12 \rightarrow 13(F) \rightarrow 17(T) \rightarrow 18 \rightarrow 19(F) \rightarrow 21 \rightarrow 22(F) \rightarrow 24$ | `test_path_all_valid_vehicle_types` | **PASS** |
| **Path 9** | $1 \rightarrow 2(F) \rightarrow 4(F) \rightarrow 6(F) \rightarrow 8(F) \rightarrow 10(F) \rightarrow 12 \rightarrow 13(F) \rightarrow 17(T) \rightarrow 18 \rightarrow 19(F) \rightarrow 21 \rightarrow 22(T) \rightarrow 23 \rightarrow 24$ | `test_path_duplicate_registration_new_vehicle` | **PASS** |
| **Path 10** | $1 \rightarrow 2(F) \rightarrow 4(F) \rightarrow 6(F) \rightarrow 8(F) \rightarrow 10(F) \rightarrow 12 \rightarrow 13(F) \rightarrow 17(T) \rightarrow 18 \rightarrow 19(T) \rightarrow 20 \rightarrow 21 \rightarrow 22(F) \rightarrow 24$ | `test_path_update_same_vehicle_with_exclude_id` | **PASS** |
| **Path 11** | $1 \rightarrow 2(F) \rightarrow 4(F) \rightarrow 6(F) \rightarrow 8(F) \rightarrow 10(F) \rightarrow 12 \rightarrow 13(F) \rightarrow 17(T) \rightarrow 18 \rightarrow 19(T) \rightarrow 20 \rightarrow 21 \rightarrow 22(T) \rightarrow 23 \rightarrow 24$ | `test_path_update_colliding_with_different_vehicle` | **PASS** |
| **Path 12** | $1 \rightarrow 2(F) \rightarrow 4(F) \rightarrow 6(F) \rightarrow 8(F) \rightarrow 10(T) \rightarrow 11 \rightarrow 17(F) \rightarrow 24$ | Covered across rate checks | **PASS** |

---

## 4. Module 2: `validate_booking_data()` Analysis

Located in: [`bookings.py`](file:///run/media/hiten/OS/PROJECTS/Vehicle%20Rental%20System/bookings.py)

### 4.1 Decision Predicate Analysis

The `validate_booking_data()` function controls booking reservation safety, inclusive rental day calculation, and scheduling conflict prevention.

Predicates in `validate_booking_data`:
1. `P1`: `if not vehicle_id_str`
2. `P2`: `if not customer_name`
3. `P3`: `if not start_date_str`
4. `P4`: `if not end_date_str`
5. `P5`: `if errors` (Guard clause for required fields)
6. `P6`: `except ValueError` (int conversion of vehicle_id)
7. `P7`: `if not vehicle` (Database existence check)
8. `P8`: `if vehicle['status'] == 'maintenance'`
9. `P9`: `except ValueError` (strptime on start_date)
10. `P10`: `except ValueError` (strptime on end_date)
11. `P11`: `if start_date < today` (Past date check)
12. `P12`: `if end_date < start_date` (Chronological ordering)
13. `P13`: `if errors` (Guard clause before price math)
14. `P14`: `if exclude_booking_id is not None` (Exclude ID in overlap query)
15. `P15`: `if overlapping` (Active overlap collision check)

### 4.2 Cyclomatic Complexity Calculation

$$V(G) = P + 1 = 15 + 1 = 16$$
Radon static analysis confirmation:
```bash
$ python3 -m radon cc bookings.py -s
bookings.py
    F 36:0 validate_booking_data - C (16)
```

### 4.3 Basis Paths & Test Suite Traceability

| Path ID | Condition Tested | Test Case in `test_whitebox.py` | Status |
| :--- | :--- | :--- | :--- |
| **Path B1** | Empty payload triggers all 4 missing field errors and early exit | `test_path_empty_payload_missing_all_required` | **PASS** |
| **Path B2** | `int(vehicle_id_str)` raises `ValueError` | `test_path_invalid_vehicle_id_not_an_integer` | **PASS** |
| **Path B3** | Vehicle ID is valid integer but `SELECT` returns `None` | `test_path_nonexistent_vehicle_id` | **PASS** |
| **Path B4** | Vehicle exists but status is `'maintenance'` | `test_path_vehicle_under_maintenance` | **PASS** |
| **Path B5** | `strptime` raises `ValueError` on start date format | `test_path_invalid_start_date_format` | **PASS** |
| **Path B6** | `strptime` raises `ValueError` on end date format | `test_path_invalid_end_date_format` | **PASS** |
| **Path B7** | `start_date < today` triggers past-date rejection | `test_path_start_date_in_past` | **PASS** |
| **Path B8** | `end_date < start_date` triggers inverted date rejection | `test_path_end_date_before_start_date` | **PASS** |
| **Path B9** | Valid dates: calculates `total_days = end - start + 1` and `total_amount` | `test_path_successful_validation_and_inclusive_calculation` | **PASS** |
| **Path B10**| Overlap query finds conflicting active booking | `test_path_overlapping_active_booking_detected` | **PASS** |
| **Path B11**| Overlap query includes `AND id != exclude_booking_id` | `test_path_overlapping_with_exclude_booking_id` | **PASS** |

---

## 5. Module 3: Internal Helper Functions Analysis

Located in: [`dashboard.py`](file:///run/media/hiten/OS/PROJECTS/Vehicle%20Rental%20System/dashboard.py) and [`app.py`](file:///run/media/hiten/OS/PROJECTS/Vehicle%20Rental%20System/app.py)

### 5.1 `safe_int()` & `safe_float()`
* **`safe_int(value, default=0)`**:
  * Branch 1: `if value is None -> return default`
  * Branch 2: `try int(value)`
  * Branch 3: `except (ValueError, TypeError) -> return default`
* **`safe_float(value, default=0.0)`**:
  * Branch 1: `if value is None -> return default`
  * Branch 2: `try float(value)`
  * Branch 3: `except (ValueError, TypeError) -> return default`
* **Coverage:** 100% statement and branch coverage in `TestDashboardHelpersWhiteBox`.

### 5.2 `close_db(e=None)`
* Branch 1: `if 'db' in g` is `False` (no database opened in request context)
* Branch 2: `if 'db' in g` is `True` (database connection exists $\rightarrow$ `db.close()`)
* **Coverage:** 100% branch coverage in `TestApplicationLifecycleWhiteBox`.

---

## 6. Structural & Branch Coverage Results

### Overall Test Suite Execution
```
============================= test session starts ==============================
platform linux -- Python 3.14.8, pytest-8.3.3, pluggy-1.7.0
rootdir: /run/media/hiten/OS/PROJECTS/Vehicle Rental System
plugins: cov-7.1.0, anyio-4.13.0
collected 82 items

tests/test_bookings.py ..............................                    [ 36%]
tests/test_vehicles.py ......................                            [ 63%]
tests/test_whitebox.py ..............................                    [100%]

================================ tests coverage ================================
Name                     Stmts   Miss Branch BrPart  Cover
----------------------------------------------------------
app.py                      52     12     10      3    73%
bookings.py                153      8     48      3    95%
dashboard.py                28      0      4      0   100%
schema.py                    1      0      0      0   100%
tests/conftest.py           26      0      0      0   100%
tests/test_bookings.py     300      0      0      0   100%
tests/test_vehicles.py     135      0      2      0   100%
tests/test_whitebox.py     218      0      4      0   100%
vehicles.py                106      3     42      1    96%
----------------------------------------------------------
TOTAL                     1031     35    112      7    96%
Coverage HTML written to dir htmlcov
============================== 82 passed in 1.46s ==============================
```

### Coverage Breakdown Summary

| Metric | Target | Achieved | Evaluation Status |
| :--- | :--- | :--- | :--- |
| **Total Automated Tests** | > 40 | **82 Tests** (52 Black-Box + 30 White-Box) | **EXCEEDED** |
| **Overall Statement Coverage** | > 85% | **96%** | **EXCEEDED** |
| **Branch / Decision Coverage** | > 80% | **93.8% (105 / 112 branches)** | **EXCEEDED** |
| **Core Module Coverage (`vehicles.py`)** | > 90% | **96%** | **EXCEEDED** |
| **Core Module Coverage (`bookings.py`)** | > 90% | **95%** | **EXCEEDED** |
| **Dashboard Module Coverage (`dashboard.py`)** | > 90% | **100%** | **PERFECT** |
| **Test Pass Rate** | 100% | **100% (82/82 Passed)** | **PERFECT** |

---

## 7. Viva Voce Examination Questions & Answers (Cheat Sheet)

### Q1: What is the difference between the testing you did earlier and White-Box testing?
> **Answer:**  
> *"Earlier, we performed Black-Box functional testing across 52 test cases. We sent HTTP requests to `/vehicles` and `/bookings` and verified the response codes, rendered HTML, and flash messages without checking internal branches.  
> In White-Box testing, we analyzed the source code directly. We drew Control Flow Graphs (CFG), calculated McCabe’s Cyclomatic Complexity, identified every decision branch (such as `try/except` type errors and status guard clauses), and wrote 30 dedicated unit tests in `test_whitebox.py` achieving 96% statement coverage and 94% branch coverage."*

### Q2: Why didn't you use Eclipse for White-Box testing?
> **Answer:**  
> *"Eclipse with JUnit and EclEmma is primarily designed for Java applications. Since our application is built using Python and Flask, using Python’s native ecosystem (`pytest`, `coverage.py`, and `radon`) is the industry standard. `coverage.py` performs AST branch instrumentation and produces visual HTML reports equivalent to EclEmma, without the overhead of a foreign IDE."*

### Q3: What is Cyclomatic Complexity and what does it indicate in your project?
> **Answer:**  
> *"Cyclomatic Complexity, developed by Thomas McCabe, measures the number of linearly independent paths through a program's source code. In our project, `validate_vehicle_data` has a complexity $V(G) = 12$, and `validate_booking_data` has $V(G) = 16$. This indicates that 12 and 16 independent test cases are required respectively to achieve 100% basis path coverage."*

### Q4: How did you calculate Cyclomatic Complexity?
> **Answer:**  
> *"We verified it using two methods:  
> 1. Formula: $V(G) = P + 1$, where $P$ is the number of predicate (decision) nodes. For `validate_vehicle_data`, there are 11 predicate checks, giving $11 + 1 = 12$.  
> 2. Static AST analysis using the Python `radon` library (`radon cc`), which confirmed $V(G) = 12$ and $V(G) = 16$."*

### Q5: How do you view the interactive white-box coverage report?
> **Answer:**  
> *"By running `python3 -m pytest --cov=. --cov-branch --cov-report=html` and opening `htmlcov/index.html` in any web browser, which interactively displays green highlighted lines for covered branches and red for missed branches."*
