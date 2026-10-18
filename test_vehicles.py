"""
Vehicle Rental System — Vehicle Management Tests
=================================================

Covers:
- TC-V01: Successful vehicle creation
- TC-V02: Missing required fields
- TC-V03: Duplicate registration number
- TC-V04: Zero rental rate
- TC-V05: Negative rental rate
- TC-V06: Vehicle search by name
- TC-V07: Vehicle search by registration number
- TC-V08: Vehicle filter by type
- TC-V09: Vehicle filter by status
- TC-V10: Vehicle update
- TC-V11: Vehicle deletion (no bookings)
- TC-V12: Vehicle deletion blocked (has bookings)
- TC-V13: Vehicle list page loads
- TC-V14: Add vehicle page loads
- TC-V15: Edit vehicle page loads
- TC-V16: Edit nonexistent vehicle
- TC-V17: Delete nonexistent vehicle
- TC-V18: All vehicle types accepted
- TC-V19: Invalid vehicle type rejected
"""

import pytest
from conftest import add_test_vehicle, add_test_booking


class TestVehicleCreation:
    """Tests for adding new vehicles."""

    def test_successful_vehicle_creation(self, client, app):
        """TC-V01: Add a valid vehicle and verify persistence."""
        response = add_test_vehicle(client)
        assert response.status_code == 200
        assert b'Vehicle added successfully' in response.data

        # Verify persistence in DB
        with app.app_context():
            from app import get_db
            db = get_db(app)
            vehicle = db.execute(
                "SELECT * FROM vehicles WHERE registration_number = 'MH-01-AB-1234'"
            ).fetchone()
            assert vehicle is not None
            assert vehicle['name'] == 'Toyota Innova'
            assert vehicle['type'] == 'Car'
            assert vehicle['daily_rental_rate'] == 2500.0
            assert vehicle['status'] == 'available'

    def test_missing_registration_number(self, client):
        """TC-V02a: Reject vehicle with missing registration number."""
        response = add_test_vehicle(client, reg='')
        assert b'Registration number is required' in response.data

    def test_missing_name(self, client):
        """TC-V02b: Reject vehicle with missing name."""
        response = add_test_vehicle(client, name='')
        assert b'Vehicle name is required' in response.data

    def test_missing_type(self, client):
        """TC-V02c: Reject vehicle with missing type."""
        response = add_test_vehicle(client, v_type='')
        assert b'Vehicle type is required' in response.data

    def test_missing_rate(self, client):
        """TC-V02d: Reject vehicle with missing rental rate."""
        response = add_test_vehicle(client, rate='')
        assert b'Daily rental rate is required' in response.data

    def test_duplicate_registration_number(self, client):
        """TC-V03: Reject vehicle with duplicate registration number."""
        add_test_vehicle(client, reg='MH-01-AB-1234')
        response = add_test_vehicle(client, reg='MH-01-AB-1234', name='Different Car')
        assert b'already exists' in response.data

    def test_zero_rental_rate(self, client):
        """TC-V04: Reject vehicle with zero rental rate."""
        response = add_test_vehicle(client, rate='0')
        assert b'positive number' in response.data

    def test_negative_rental_rate(self, client):
        """TC-V05: Reject vehicle with negative rental rate."""
        response = add_test_vehicle(client, rate='-500')
        assert b'positive number' in response.data

    def test_all_vehicle_types(self, client, app):
        """TC-V18: All predefined vehicle types are accepted."""
        types = ['Car', 'SUV', 'Van', 'Truck', 'Motorcycle', 'Bus']
        for i, v_type in enumerate(types):
            response = add_test_vehicle(
                client, reg=f'MH-01-XX-{i:04d}',
                name=f'Test {v_type}', v_type=v_type
            )
            assert b'Vehicle added successfully' in response.data

    def test_invalid_vehicle_type(self, client):
        """TC-V19: Invalid vehicle type is rejected."""
        response = add_test_vehicle(client, v_type='Helicopter')
        assert b'must be one of' in response.data


class TestVehicleSearch:
    """Tests for vehicle search and filtering."""

    def test_search_by_name(self, client):
        """TC-V06: Search finds vehicle by partial name match."""
        add_test_vehicle(client, reg='MH-01-AB-0001', name='Toyota Innova')
        add_test_vehicle(client, reg='MH-01-AB-0002', name='Honda City')
        response = client.get('/vehicles/?search=Toyota')
        assert b'Toyota Innova' in response.data
        assert b'Honda City' not in response.data

    def test_search_by_registration(self, client):
        """TC-V07: Search finds vehicle by registration number."""
        add_test_vehicle(client, reg='KA-05-MN-9999', name='Test Vehicle')
        response = client.get('/vehicles/?search=KA-05')
        assert b'KA-05-MN-9999' in response.data

    def test_filter_by_type(self, client):
        """TC-V08: Filter shows only matching vehicle type."""
        add_test_vehicle(client, reg='MH-01-AB-0001', name='Car One', v_type='Car')
        add_test_vehicle(client, reg='MH-01-AB-0002', name='SUV One', v_type='SUV')
        response = client.get('/vehicles/?type=SUV')
        assert b'SUV One' in response.data
        assert b'Car One' not in response.data

    def test_filter_by_status(self, client):
        """TC-V09: Filter shows only matching status."""
        add_test_vehicle(client, reg='MH-01-AB-0001', name='Available Car')
        response = client.get('/vehicles/?status=available')
        assert b'Available Car' in response.data


class TestVehicleUpdate:
    """Tests for editing vehicle details."""

    def test_successful_update(self, client, app):
        """TC-V10: Update vehicle details and verify persistence."""
        add_test_vehicle(client)

        with app.app_context():
            from app import get_db
            db = get_db(app)
            vehicle = db.execute("SELECT id FROM vehicles LIMIT 1").fetchone()
            vehicle_id = vehicle['id']

        response = client.post(f'/vehicles/edit/{vehicle_id}', data={
            'registration_number': 'MH-01-AB-5678',
            'name': 'Updated Innova',
            'type': 'SUV',
            'daily_rental_rate': '3000',
            'status': 'maintenance',
        }, follow_redirects=True)
        assert b'Vehicle updated successfully' in response.data

        with app.app_context():
            from app import get_db
            db = get_db(app)
            updated = db.execute(
                "SELECT * FROM vehicles WHERE id = ?", (vehicle_id,)
            ).fetchone()
            assert updated['name'] == 'Updated Innova'
            assert updated['type'] == 'SUV'
            assert updated['daily_rental_rate'] == 3000.0
            assert updated['status'] == 'maintenance'

    def test_edit_nonexistent_vehicle(self, client):
        """TC-V16: Editing a nonexistent vehicle shows error."""
        response = client.get('/vehicles/edit/9999', follow_redirects=True)
        assert b'Vehicle not found' in response.data


class TestVehicleDeletion:
    """Tests for vehicle deletion with constraint checks."""

    def test_successful_deletion(self, client, app):
        """TC-V11: Delete a vehicle with no bookings."""
        add_test_vehicle(client)

        with app.app_context():
            from app import get_db
            db = get_db(app)
            vehicle = db.execute("SELECT id FROM vehicles LIMIT 1").fetchone()
            vehicle_id = vehicle['id']

        response = client.post(f'/vehicles/delete/{vehicle_id}', follow_redirects=True)
        assert b'Vehicle deleted successfully' in response.data

        with app.app_context():
            from app import get_db
            db = get_db(app)
            deleted = db.execute(
                "SELECT * FROM vehicles WHERE id = ?", (vehicle_id,)
            ).fetchone()
            assert deleted is None

    def test_deletion_blocked_with_bookings(self, client, app):
        """TC-V12: Cannot delete vehicle with booking history."""
        add_test_vehicle(client)

        with app.app_context():
            from app import get_db
            db = get_db(app)
            vehicle = db.execute("SELECT id FROM vehicles LIMIT 1").fetchone()
            vehicle_id = vehicle['id']

        add_test_booking(client, vehicle_id=vehicle_id)

        response = client.post(f'/vehicles/delete/{vehicle_id}', follow_redirects=True)
        assert b'Cannot delete' in response.data

        # Vehicle should still exist
        with app.app_context():
            from app import get_db
            db = get_db(app)
            still_exists = db.execute(
                "SELECT * FROM vehicles WHERE id = ?", (vehicle_id,)
            ).fetchone()
            assert still_exists is not None

    def test_delete_nonexistent_vehicle(self, client):
        """TC-V17: Deleting a nonexistent vehicle shows error."""
        response = client.post('/vehicles/delete/9999', follow_redirects=True)
        assert b'Vehicle not found' in response.data


class TestVehiclePages:
    """Tests for page rendering."""

    def test_vehicle_list_page(self, client):
        """TC-V13: Vehicle list page loads successfully."""
        response = client.get('/vehicles/')
        assert response.status_code == 200
        assert b'Vehicle Management' in response.data

    def test_add_vehicle_page(self, client):
        """TC-V14: Add vehicle form page loads."""
        response = client.get('/vehicles/add')
        assert response.status_code == 200
        assert b'Add New Vehicle' in response.data

    def test_edit_vehicle_page(self, client):
        """TC-V15: Edit vehicle form page loads with data."""
        add_test_vehicle(client)
        response = client.get('/vehicles/edit/1')
        assert response.status_code == 200
        assert b'Edit Vehicle' in response.data
