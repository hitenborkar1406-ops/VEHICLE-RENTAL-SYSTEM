"""
Vehicle Rental System — White-Box (Structural & Basis Path) Test Suite
=====================================================================

This module implements comprehensive white-box unit testing directly against
the internal control-flow structures, decision predicates, and basis paths of:
  1. vehicles.validate_vehicle_data (Cyclomatic Complexity V(G) = 12)
  2. bookings.validate_booking_data (Cyclomatic Complexity V(G) = 16)
  3. dashboard.safe_int & dashboard.safe_float
  4. app.close_db & database teardown lifecycle

Unlike black-box tests which only query HTTP endpoints, these tests inspect
internal execution branches, exception blocks, and boundary conditions directly.
"""

import pytest
from datetime import date, timedelta
from flask import g
from vehicles import validate_vehicle_data, VEHICLE_TYPES
from bookings import validate_booking_data
from dashboard import safe_int, safe_float
from app import close_db
from repositories.vehicles import VehicleRepository
from repositories.bookings import BookingRepository


# ============================================================================
# 1. White-Box Testing for vehicles.validate_vehicle_data
#    McCabe Cyclomatic Complexity V(G) = 12
# ============================================================================
class TestValidateVehicleDataWhiteBox:
    """
    Direct structural and basis-path testing for validate_vehicle_data().
    Targets every predicate condition and try/except/if branch.
    """

    def test_path_empty_payload_all_required_missing(self, db):
        """
        Path: All required field conditions evaluate to True.
        Branch: not reg_num, not name, not v_type, not rate_str
        """
        data = {}
        repo = VehicleRepository(db)
        errors = validate_vehicle_data(data, repo)
        assert len(errors) == 4
        assert 'Registration number is required.' in errors
        assert 'Vehicle name is required.' in errors
        assert 'Vehicle type is required.' in errors
        assert 'Daily rental rate is required.' in errors

    def test_path_missing_registration_only(self, db):
        """Path: Only registration is missing/blank."""
        data = {
            'registration_number': '   ',
            'name': 'Toyota Camry',
            'type': 'Car',
            'daily_rental_rate': '1500'
        }
        repo = VehicleRepository(db)
        errors = validate_vehicle_data(data, repo)
        assert len(errors) == 1
        assert 'Registration number is required.' in errors

    def test_path_missing_name_only(self, db):
        """Path: Only vehicle name is missing/blank."""
        data = {
            'registration_number': 'MH-12-PQ-9999',
            'name': '',
            'type': 'Car',
            'daily_rental_rate': '1500'
        }
        repo = VehicleRepository(db)
        errors = validate_vehicle_data(data, repo)
        assert len(errors) == 1
        assert 'Vehicle name is required.' in errors

    def test_path_missing_type_only(self, db):
        """Path: Only vehicle type is missing."""
        data = {
            'registration_number': 'MH-12-PQ-9999',
            'name': 'Toyota Camry',
            'type': '',
            'daily_rental_rate': '1500'
        }
        repo = VehicleRepository(db)
        errors = validate_vehicle_data(data, repo)
        assert len(errors) == 1
        assert 'Vehicle type is required.' in errors

    def test_path_invalid_vehicle_type(self, db):
        """
        Path: v_type is provided, but 'v_type not in VEHICLE_TYPES' is True.
        Branch: elif v_type not in VEHICLE_TYPES
        """
        data = {
            'registration_number': 'MH-12-PQ-9999',
            'name': 'Speedboat 3000',
            'type': 'Boat',
            'daily_rental_rate': '2500'
        }
        repo = VehicleRepository(db)
        errors = validate_vehicle_data(data, repo)
        assert len(errors) == 1
        assert 'Vehicle type must be one of' in errors[0]

    def test_path_all_valid_vehicle_types(self, db):
        """
        Decision Coverage: Test all predefined valid types evaluate to False for type error.
        """
        for v_type in VEHICLE_TYPES:
            data = {
                'registration_number': f'MH-01-WB-{v_type[:3].upper()}',
                'name': f'Test {v_type}',
                'type': v_type,
                'daily_rental_rate': '1000'
            }
            repo = VehicleRepository(db)
            errors = validate_vehicle_data(data, repo)
            assert errors == []

    def test_path_rate_non_numeric_exception(self, db):
        """
        Path: rate_str is not empty, but float(rate_str) raises ValueError.
        Branch: except ValueError -> 'Daily rental rate must be a valid number.'
        """
        data = {
            'registration_number': 'MH-12-PQ-9999',
            'name': 'Toyota Camry',
            'type': 'Car',
            'daily_rental_rate': 'one_thousand'
        }
        repo = VehicleRepository(db)
        errors = validate_vehicle_data(data, repo)
        assert len(errors) == 1
        assert 'Daily rental rate must be a valid number.' in errors

    def test_path_rate_zero_and_negative(self, db):
        """
        Path: rate is a valid float, but rate <= 0 is True.
        Branch: if rate <= 0
        """
        for bad_rate in ['0', '0.0', '-1', '-250.50']:
            data = {
                'registration_number': 'MH-12-PQ-9999',
                'name': 'Toyota Camry',
                'type': 'Car',
                'daily_rental_rate': bad_rate
            }
            repo = VehicleRepository(db)
            errors = validate_vehicle_data(data, repo)
            assert len(errors) == 1
            assert 'Daily rental rate must be a positive number.' in errors

    def test_path_duplicate_registration_new_vehicle(self, db):
        """
        Path: Valid fields, reg_num and not errors is True, exclude_id is None,
        query finds existing record in database.
        Branch: if existing -> errors.append(...)
        """
        # Insert a vehicle into the database
        db.execute(
            "INSERT INTO vehicles (registration_number, name, type, daily_rental_rate, status) "
            "VALUES (?, ?, ?, ?, ?)",
            ('MH-20-EX-0001', 'Existing Honda', 'Car', 2000.0, 'available')
        )
        db.commit()

        # Try validating data with the identical registration number
        data = {
            'registration_number': 'MH-20-EX-0001',
            'name': 'Duplicate Attempt',
            'type': 'SUV',
            'daily_rental_rate': '2200'
        }
        repo = VehicleRepository(db)
        errors = validate_vehicle_data(data, repo, exclude_id=None)
        assert len(errors) == 1
        assert 'A vehicle with this registration number already exists.' in errors

    def test_path_update_same_vehicle_with_exclude_id(self, db):
        """
        Path: reg_num and not errors is True, exclude_id is provided,
        query filters 'AND id != exclude_id', returns no collision.
        Branch: if exclude_id is not None
        """
        cursor = db.execute(
            "INSERT INTO vehicles (registration_number, name, type, daily_rental_rate, status) "
            "VALUES (?, ?, ?, ?, ?)",
            ('MH-20-EX-0002', 'Vehicle to Update', 'Car', 2000.0, 'available')
        )
        db.commit()
        vehicle_id = cursor.lastrowid

        data = {
            'registration_number': 'MH-20-EX-0002',  # Keep same reg number
            'name': 'Vehicle to Update (Renamed)',
            'type': 'Car',
            'daily_rental_rate': '2500'
        }
        repo = VehicleRepository(db)
        errors = validate_vehicle_data(data, repo, exclude_id=vehicle_id)
        assert errors == []

    def test_path_update_colliding_with_different_vehicle(self, db):
        """
        Path: exclude_id is provided, but another record with the same reg_num exists.
        Branch: exclude_id is not None, existing is not None -> Collision detected.
        """
        db.execute(
            "INSERT INTO vehicles (registration_number, name, type, daily_rental_rate, status) "
            "VALUES (?, ?, ?, ?, ?)",
            ('MH-20-EX-0003', 'Vehicle Alpha', 'Car', 2000.0, 'available')
        )
        cursor2 = db.execute(
            "INSERT INTO vehicles (registration_number, name, type, daily_rental_rate, status) "
            "VALUES (?, ?, ?, ?, ?)",
            ('MH-20-EX-0004', 'Vehicle Beta', 'Car', 2000.0, 'available')
        )
        db.commit()
        beta_id = cursor2.lastrowid

        # Update Beta with Alpha's registration number
        data = {
            'registration_number': 'MH-20-EX-0003',
            'name': 'Vehicle Beta New Name',
            'type': 'Car',
            'daily_rental_rate': '2500'
        }
        repo = VehicleRepository(db)
        errors = validate_vehicle_data(data, repo, exclude_id=beta_id)
        assert len(errors) == 1
        assert 'A vehicle with this registration number already exists.' in errors


# ============================================================================
# 2. White-Box Testing for bookings.validate_booking_data
#    McCabe Cyclomatic Complexity V(G) = 16
# ============================================================================
class TestValidateBookingDataWhiteBox:
    """
    Direct structural and basis-path testing for validate_booking_data().
    Targets every guard clause, conversion exception, and validation predicate.
    """

    def test_path_empty_payload_missing_all_required(self, db):
        """
        Path: All required field guard clauses trigger.
        Branch: not vehicle_id_str, not customer_name, not start_date_str, not end_date_str
        """
        booking_repo = BookingRepository(db)
        vehicle_repo = VehicleRepository(db)
        errors, parsed = validate_booking_data({}, booking_repo, vehicle_repo)
        assert len(errors) == 4
        assert parsed == {}
        assert 'Please select a vehicle.' in errors
        assert 'Customer name is required.' in errors
        assert 'Start date is required.' in errors
        assert 'End date is required.' in errors

    def test_path_invalid_vehicle_id_not_an_integer(self, db):
        """
        Path: vehicle_id_str cannot be cast to int.
        Branch: try int(vehicle_id_str) -> except ValueError
        """
        booking_repo = BookingRepository(db)
        vehicle_repo = VehicleRepository(db)
        data = {
            'vehicle_id': 'not_an_id',
            'customer_name': 'Alice Wonder',
            'start_date': '2027-01-01',
            'end_date': '2027-01-05'
        }
        errors, parsed = validate_booking_data(data, booking_repo, vehicle_repo)
        assert len(errors) == 1
        assert 'Invalid vehicle selection.' in errors
        assert parsed == {}

    def test_path_nonexistent_vehicle_id(self, db):
        """
        Path: vehicle_id is a valid integer, but SELECT query returns None.
        Branch: if not vehicle: errors.append('Selected vehicle does not exist.')
        """
        booking_repo = BookingRepository(db)
        vehicle_repo = VehicleRepository(db)
        data = {
            'vehicle_id': '999999',
            'customer_name': 'Alice Wonder',
            'start_date': '2027-01-01',
            'end_date': '2027-01-05'
        }
        errors, parsed = validate_booking_data(data, booking_repo, vehicle_repo)
        assert len(errors) == 1
        assert 'Selected vehicle does not exist.' in errors
        assert parsed == {}

    def test_path_vehicle_under_maintenance(self, db):
        """
        Path: Vehicle exists, but vehicle['status'] == 'maintenance'.
        Branch: if vehicle['status'] == 'maintenance': errors.append(...)
        """
        cursor = db.execute(
            "INSERT INTO vehicles (registration_number, name, type, daily_rental_rate, status) "
            "VALUES (?, ?, ?, ?, ?)",
            ('MH-01-MAINT-1', 'Maintenance Truck', 'Truck', 3000.0, 'maintenance')
        )
        db.commit()
        v_id = cursor.lastrowid

        booking_repo = BookingRepository(db)
        vehicle_repo = VehicleRepository(db)
        data = {
            'vehicle_id': str(v_id),
            'customer_name': 'Alice Wonder',
            'start_date': '2027-01-01',
            'end_date': '2027-01-05'
        }
        errors, parsed = validate_booking_data(data, booking_repo, vehicle_repo)
        assert any('under maintenance' in e for e in errors)
        assert parsed == {}

    def test_path_invalid_start_date_format(self, db):
        """
        Path: start_date is not YYYY-MM-DD.
        Branch: try strptime(start_date_str) -> except ValueError
        """
        cursor = db.execute(
            "INSERT INTO vehicles (registration_number, name, type, daily_rental_rate, status) "
            "VALUES (?, ?, ?, ?, ?)",
            ('MH-01-DATE-1', 'Test Car', 'Car', 1500.0, 'available')
        )
        db.commit()
        v_id = cursor.lastrowid

        booking_repo = BookingRepository(db)
        vehicle_repo = VehicleRepository(db)
        data = {
            'vehicle_id': str(v_id),
            'customer_name': 'Alice Wonder',
            'start_date': '10-01-2027',  # Invalid format
            'end_date': '2027-01-12'
        }
        errors, parsed = validate_booking_data(data, booking_repo, vehicle_repo)
        assert len(errors) == 1
        assert 'Start date must be in YYYY-MM-DD format.' in errors
        assert parsed == {}

    def test_path_invalid_end_date_format(self, db):
        """
        Path: end_date is not YYYY-MM-DD.
        Branch: try strptime(end_date_str) -> except ValueError
        """
        cursor = db.execute(
            "INSERT INTO vehicles (registration_number, name, type, daily_rental_rate, status) "
            "VALUES (?, ?, ?, ?, ?)",
            ('MH-01-DATE-2', 'Test Car 2', 'Car', 1500.0, 'available')
        )
        db.commit()
        v_id = cursor.lastrowid

        booking_repo = BookingRepository(db)
        vehicle_repo = VehicleRepository(db)
        data = {
            'vehicle_id': str(v_id),
            'customer_name': 'Alice Wonder',
            'start_date': '2027-01-10',
            'end_date': 'invalid-end-date'
        }
        errors, parsed = validate_booking_data(data, booking_repo, vehicle_repo)
        assert len(errors) == 1
        assert 'End date must be in YYYY-MM-DD format.' in errors
        assert parsed == {}

    def test_path_start_date_in_past(self, db):
        """
        Path: start_date < today is True.
        Branch: if start_date < today
        """
        cursor = db.execute(
            "INSERT INTO vehicles (registration_number, name, type, daily_rental_rate, status) "
            "VALUES (?, ?, ?, ?, ?)",
            ('MH-01-DATE-3', 'Test Car 3', 'Car', 1500.0, 'available')
        )
        db.commit()
        v_id = cursor.lastrowid

        past_date = (date.today() - timedelta(days=5)).isoformat()
        future_date = (date.today() + timedelta(days=2)).isoformat()

        booking_repo = BookingRepository(db)
        vehicle_repo = VehicleRepository(db)
        data = {
            'vehicle_id': str(v_id),
            'customer_name': 'Alice Wonder',
            'start_date': past_date,
            'end_date': future_date
        }
        errors, parsed = validate_booking_data(data, booking_repo, vehicle_repo)
        assert 'Start date cannot be in the past.' in errors
        assert parsed == {}

    def test_path_end_date_before_start_date(self, db):
        """
        Path: end_date < start_date is True.
        Branch: if end_date < start_date
        """
        cursor = db.execute(
            "INSERT INTO vehicles (registration_number, name, type, daily_rental_rate, status) "
            "VALUES (?, ?, ?, ?, ?)",
            ('MH-01-DATE-4', 'Test Car 4', 'Car', 1500.0, 'available')
        )
        db.commit()
        v_id = cursor.lastrowid

        start = (date.today() + timedelta(days=10)).isoformat()
        end = (date.today() + timedelta(days=5)).isoformat()

        booking_repo = BookingRepository(db)
        vehicle_repo = VehicleRepository(db)
        data = {
            'vehicle_id': str(v_id),
            'customer_name': 'Alice Wonder',
            'start_date': start,
            'end_date': end
        }
        errors, parsed = validate_booking_data(data, booking_repo, vehicle_repo)
        assert 'End date must be on or after the start date.' in errors
        assert parsed == {}

    def test_path_successful_validation_and_inclusive_calculation(self, db):
        """
        Path: All validations pass, inclusive days and rental amount calculated accurately.
        Formula: total_days = (end - start).days + 1
        """
        cursor = db.execute(
            "INSERT INTO vehicles (registration_number, name, type, daily_rental_rate, status) "
            "VALUES (?, ?, ?, ?, ?)",
            ('MH-01-OK-1', 'Innova Crysta', 'SUV', 3000.0, 'available')
        )
        db.commit()
        v_id = cursor.lastrowid

        start = (date.today() + timedelta(days=2)).isoformat()
        end = (date.today() + timedelta(days=4)).isoformat()  # 3 days: d2, d3, d4

        booking_repo = BookingRepository(db)
        vehicle_repo = VehicleRepository(db)
        data = {
            'vehicle_id': str(v_id),
            'customer_name': 'Robert Brown',
            'start_date': start,
            'end_date': end
        }
        errors, parsed = validate_booking_data(data, booking_repo, vehicle_repo)
        assert errors == []
        assert parsed['vehicle_id'] == v_id
        assert parsed['customer_name'] == 'Robert Brown'
        assert parsed['total_days'] == 3
        assert parsed['total_amount'] == 9000.0
        assert parsed['daily_rate'] == 3000.0

    def test_path_overlapping_active_booking_detected(self, db):
        """
        Path: Overlapping query finds an active booking in the date range.
        Branch: if overlapping: errors.append(...)
        """
        cursor = db.execute(
            "INSERT INTO vehicles (registration_number, name, type, daily_rental_rate, status) "
            "VALUES (?, ?, ?, ?, ?)",
            ('MH-01-OVERLAP-1', 'Fleet Car', 'Car', 1000.0, 'available')
        )
        v_id = cursor.lastrowid

        start_1 = (date.today() + timedelta(days=10)).isoformat()
        end_1 = (date.today() + timedelta(days=15)).isoformat()

        # Insert active booking
        db.execute(
            "INSERT INTO bookings (vehicle_id, customer_name, start_date, end_date, total_days, total_amount, status) "
            "VALUES (?, ?, ?, ?, ?, ?, 'active')",
            (v_id, 'Existing Customer', start_1, end_1, 6, 6000.0)
        )
        db.commit()

        # Try to book overlapping range
        start_2 = (date.today() + timedelta(days=12)).isoformat()
        end_2 = (date.today() + timedelta(days=18)).isoformat()

        booking_repo = BookingRepository(db)
        vehicle_repo = VehicleRepository(db)
        data = {
            'vehicle_id': str(v_id),
            'customer_name': 'Conflict Seeker',
            'start_date': start_2,
            'end_date': end_2
        }
        errors, parsed = validate_booking_data(data, booking_repo, vehicle_repo)
        assert len(errors) == 1
        assert 'already has an active booking from' in errors[0]

    def test_path_overlapping_with_exclude_booking_id(self, db):
        """
        Path: exclude_booking_id is provided, preventing a booking from conflicting with itself.
        Branch: if exclude_booking_id is not None
        """
        cursor = db.execute(
            "INSERT INTO vehicles (registration_number, name, type, daily_rental_rate, status) "
            "VALUES (?, ?, ?, ?, ?)",
            ('MH-01-EXCL-1', 'Fleet Car 2', 'Car', 1000.0, 'available')
        )
        v_id = cursor.lastrowid

        start_1 = (date.today() + timedelta(days=10)).isoformat()
        end_1 = (date.today() + timedelta(days=15)).isoformat()

        b_cursor = db.execute(
            "INSERT INTO bookings (vehicle_id, customer_name, start_date, end_date, total_days, total_amount, status) "
            "VALUES (?, ?, ?, ?, ?, ?, 'active')",
            (v_id, 'Existing Customer', start_1, end_1, 6, 6000.0)
        )
        db.commit()
        booking_id = b_cursor.lastrowid

        booking_repo = BookingRepository(db)
        vehicle_repo = VehicleRepository(db)
        data = {
            'vehicle_id': str(v_id),
            'customer_name': 'Existing Customer Updated',
            'start_date': start_1,
            'end_date': end_1
        }
        # Exclude this booking ID
        errors, parsed = validate_booking_data(data, booking_repo, vehicle_repo, exclude_booking_id=booking_id)
        assert errors == []
        assert parsed['total_days'] == 6


# ============================================================================
# 3. White-Box Testing for Dashboard Helper Functions
# ============================================================================
class TestDashboardHelpersWhiteBox:
    """
    Direct branch and exception coverage for safe_int and safe_float helpers.
    """

    def test_safe_int_valid_values(self):
        """Branch: normal integer and float/string conversions."""
        assert safe_int(10) == 10
        assert safe_int("42") == 42
        assert safe_int(3.14) == 3

    def test_safe_int_none_handling(self):
        """Branch: if value is None: return default"""
        assert safe_int(None) == 0
        assert safe_int(None, default=99) == 99

    def test_safe_int_exception_handling(self):
        """Branch: except (ValueError, TypeError): return default"""
        assert safe_int("invalid_number") == 0
        assert safe_int("abc", default=-1) == -1
        assert safe_int([1, 2, 3], default=5) == 5

    def test_safe_float_valid_values(self):
        """Branch: normal float and integer conversions."""
        assert safe_float(12.5) == 12.5
        assert safe_float("99.99") == 99.99
        assert safe_float(100) == 100.0

    def test_safe_float_none_handling(self):
        """Branch: if value is None: return default"""
        assert safe_float(None) == 0.0
        assert safe_float(None, default=15.5) == 15.5

    def test_safe_float_exception_handling(self):
        """Branch: except (ValueError, TypeError): return default"""
        assert safe_float("not_a_float") == 0.0
        assert safe_float("xyz", default=2.5) == 2.5
        assert safe_float({}, default=0.0) == 0.0


# ============================================================================
# 4. White-Box Testing for Application Database Teardown
# ============================================================================
class TestApplicationLifecycleWhiteBox:
    """
    Branch testing for app.close_db() with and without active g.db connection.
    """

    def test_close_db_when_no_db_connected(self, app):
        """Branch: if 'db' in g is False."""
        with app.app_context():
            # g does not have 'db' set
            close_db(None)
            assert 'db' not in g

    def test_close_db_when_db_is_connected(self, app):
        """Branch: if 'db' in g is True, call db.close()."""
        with app.app_context():
            from app import get_db
            db_conn = get_db(app)
            assert 'db' in g
            close_db(None)
            # After close, executing query should raise sqlite3.ProgrammingError
            import sqlite3
            with pytest.raises(sqlite3.ProgrammingError):
                db_conn.execute("SELECT 1")
