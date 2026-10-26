"""
Vehicle Rental System — Booking Management Tests
=================================================

Covers:
- TC-B01: Successful booking creation
- TC-B02: Missing vehicle selection
- TC-B03: Missing customer name
- TC-B04: Missing start date
- TC-B05: Missing end date
- TC-B06: End date before start date
- TC-B07: Start date in the past
- TC-B08: Rental amount calculation (inclusive)
- TC-B09: Booking a nonexistent vehicle
- TC-B10: Overlapping booking prevention
- TC-B11: Successful booking cancellation
- TC-B12: Cancel already cancelled booking
- TC-B13: Rebooking dates after cancellation
- TC-B14: Booking list page loads
- TC-B15: Create booking page loads
- TC-B16: View booking details
- TC-B17: View nonexistent booking
- TC-B18: Cancel nonexistent booking
- TC-B19: Same-day booking (1 day)
- TC-B20: Multi-day booking calculation
- TC-B21: Database persistence of booking
- TC-B22: Adjacent bookings (no overlap)
- TC-B23: Booking vehicle under maintenance
"""

import pytest
from conftest import add_test_vehicle, add_test_booking


class TestBookingCreation:
    """Tests for creating new bookings."""

    def test_successful_booking(self, client, app):
        """TC-B01: Create a valid booking and verify persistence."""
        add_test_vehicle(client)

        with app.app_context():
            from app import get_db
            db = get_db(app)
            vehicle = db.execute("SELECT id FROM vehicles LIMIT 1").fetchone()
            vehicle_id = vehicle['id']

        response = add_test_booking(client, vehicle_id=vehicle_id,
                                    start='2027-01-10', end='2027-01-12')
        assert response.status_code == 200
        assert b'Booking created successfully' in response.data

    def test_missing_vehicle(self, client):
        """TC-B02: Reject booking without vehicle selection."""
        response = client.post('/bookings/create', data={
            'vehicle_id': '',
            'customer_name': 'Test',
            'start_date': '2027-01-10',
            'end_date': '2027-01-12',
        }, follow_redirects=True)
        assert b'Please select a vehicle' in response.data

    def test_missing_customer_name(self, client):
        """TC-B03: Reject booking without customer name."""
        add_test_vehicle(client)
        response = client.post('/bookings/create', data={
            'vehicle_id': '1',
            'customer_name': '',
            'start_date': '2027-01-10',
            'end_date': '2027-01-12',
        }, follow_redirects=True)
        assert b'Customer name is required' in response.data

    def test_missing_start_date(self, client):
        """TC-B04: Reject booking without start date."""
        add_test_vehicle(client)
        response = client.post('/bookings/create', data={
            'vehicle_id': '1',
            'customer_name': 'Test',
            'start_date': '',
            'end_date': '2027-01-12',
        }, follow_redirects=True)
        assert b'Start date is required' in response.data

    def test_missing_end_date(self, client):
        """TC-B05: Reject booking without end date."""
        add_test_vehicle(client)
        response = client.post('/bookings/create', data={
            'vehicle_id': '1',
            'customer_name': 'Test',
            'start_date': '2027-01-10',
            'end_date': '',
        }, follow_redirects=True)
        assert b'End date is required' in response.data

    def test_end_date_before_start_date(self, client):
        """TC-B06: Reject booking where end < start."""
        add_test_vehicle(client)
        response = add_test_booking(client, start='2027-01-15', end='2027-01-10')
        assert b'End date must be on or after the start date' in response.data

    def test_start_date_in_past(self, client):
        """TC-B07: Reject booking with past start date."""
        add_test_vehicle(client)
        response = add_test_booking(client, start='2020-01-01', end='2020-01-03')
        assert b'Start date cannot be in the past' in response.data

    def test_booking_nonexistent_vehicle(self, client):
        """TC-B09: Reject booking for a vehicle that does not exist."""
        response = add_test_booking(client, vehicle_id=9999)
        assert b'does not exist' in response.data

    def test_same_day_booking(self, client, app):
        """TC-B19: Same-day booking results in 1 rental day."""
        add_test_vehicle(client, rate='1000')

        with app.app_context():
            from app import get_db
            db = get_db(app)
            vehicle = db.execute("SELECT id FROM vehicles LIMIT 1").fetchone()
            vehicle_id = vehicle['id']

        response = add_test_booking(client, vehicle_id=vehicle_id,
                                    start='2027-06-15', end='2027-06-15')
        assert b'Booking created successfully' in response.data
        assert b'1 day(s)' in response.data

    def test_booking_vehicle_under_maintenance(self, client, app):
        """TC-B23: Cannot book a vehicle under maintenance."""
        add_test_vehicle(client)

        with app.app_context():
            from app import get_db
            db = get_db(app)
            db.execute("UPDATE vehicles SET status = 'maintenance' WHERE id = 1")
            db.commit()

        response = add_test_booking(client, vehicle_id=1)
        assert b'maintenance' in response.data


class TestRentalCalculation:
    """Tests for the inclusive rental day calculation."""

    def test_rental_amount_calculation(self, client, app):
        """
        TC-B08: Verify inclusive rental calculation.
        Jan 10 to Jan 12 = 3 days. Rate ₹2500/day → ₹7500 total.
        """
        add_test_vehicle(client, rate='2500')

        with app.app_context():
            from app import get_db
            db = get_db(app)
            vehicle = db.execute("SELECT id FROM vehicles LIMIT 1").fetchone()
            vehicle_id = vehicle['id']

        add_test_booking(client, vehicle_id=vehicle_id,
                         start='2027-01-10', end='2027-01-12')

        with app.app_context():
            from app import get_db
            db = get_db(app)
            booking = db.execute("SELECT * FROM bookings LIMIT 1").fetchone()
            assert booking['total_days'] == 3  # inclusive: 10, 11, 12
            assert booking['total_amount'] == 7500.0  # 3 × 2500

    def test_multi_day_calculation(self, client, app):
        """
        TC-B20: 7-day booking calculation.
        Jan 1 to Jan 7 = 7 days. Rate ₹1000/day → ₹7000.
        """
        add_test_vehicle(client, rate='1000')

        with app.app_context():
            from app import get_db
            db = get_db(app)
            vehicle = db.execute("SELECT id FROM vehicles LIMIT 1").fetchone()
            vehicle_id = vehicle['id']

        add_test_booking(client, vehicle_id=vehicle_id,
                         start='2027-01-01', end='2027-01-07')

        with app.app_context():
            from app import get_db
            db = get_db(app)
            booking = db.execute("SELECT * FROM bookings LIMIT 1").fetchone()
            assert booking['total_days'] == 7
            assert booking['total_amount'] == 7000.0


class TestOverlapPrevention:
    """Tests for overlapping booking prevention."""

    def test_overlapping_booking_rejected(self, client, app):
        """TC-B10: Cannot create overlapping active bookings for same vehicle."""
        add_test_vehicle(client)

        with app.app_context():
            from app import get_db
            db = get_db(app)
            vehicle = db.execute("SELECT id FROM vehicles LIMIT 1").fetchone()
            vehicle_id = vehicle['id']

        # First booking: Jan 10–12
        add_test_booking(client, vehicle_id=vehicle_id,
                         start='2027-01-10', end='2027-01-12')

        # Overlapping booking: Jan 11–13
        response = add_test_booking(client, vehicle_id=vehicle_id,
                                    customer='Jane Doe',
                                    start='2027-01-11', end='2027-01-13')
        assert b'already has an active booking' in response.data

    def test_adjacent_bookings_allowed(self, client, app):
        """TC-B22: Adjacent (non-overlapping) bookings are allowed."""
        add_test_vehicle(client)

        with app.app_context():
            from app import get_db
            db = get_db(app)
            vehicle = db.execute("SELECT id FROM vehicles LIMIT 1").fetchone()
            vehicle_id = vehicle['id']

        # First booking: Jan 10–12
        add_test_booking(client, vehicle_id=vehicle_id,
                         start='2027-01-10', end='2027-01-12')

        # Adjacent booking: Jan 13–15 (starts after first ends)
        response = add_test_booking(client, vehicle_id=vehicle_id,
                                    customer='Jane Doe',
                                    start='2027-01-13', end='2027-01-15')
        assert b'Booking created successfully' in response.data


class TestBookingCancellation:
    """Tests for booking cancellation and rebooking."""

    def test_successful_cancellation(self, client, app):
        """TC-B11: Cancel an active booking."""
        add_test_vehicle(client)

        with app.app_context():
            from app import get_db
            db = get_db(app)
            vehicle = db.execute("SELECT id FROM vehicles LIMIT 1").fetchone()
            vehicle_id = vehicle['id']

        add_test_booking(client, vehicle_id=vehicle_id)

        with app.app_context():
            from app import get_db
            db = get_db(app)
            booking = db.execute("SELECT id FROM bookings LIMIT 1").fetchone()
            booking_id = booking['id']

        response = client.post(f'/bookings/cancel/{booking_id}', follow_redirects=True)
        assert b'Booking cancelled successfully' in response.data

        # Verify status changed
        with app.app_context():
            from app import get_db
            db = get_db(app)
            cancelled = db.execute(
                "SELECT * FROM bookings WHERE id = ?", (booking_id,)
            ).fetchone()
            assert cancelled['status'] == 'cancelled'

    def test_cancel_already_cancelled(self, client, app):
        """TC-B12: Cannot cancel an already cancelled booking."""
        add_test_vehicle(client)

        with app.app_context():
            from app import get_db
            db = get_db(app)
            vehicle = db.execute("SELECT id FROM vehicles LIMIT 1").fetchone()
            vehicle_id = vehicle['id']

        add_test_booking(client, vehicle_id=vehicle_id)

        with app.app_context():
            from app import get_db
            db = get_db(app)
            booking = db.execute("SELECT id FROM bookings LIMIT 1").fetchone()
            booking_id = booking['id']

        # Cancel first
        client.post(f'/bookings/cancel/{booking_id}', follow_redirects=True)
        # Try again
        response = client.post(f'/bookings/cancel/{booking_id}', follow_redirects=True)
        assert b'Only active bookings can be cancelled' in response.data

    def test_rebooking_after_cancellation(self, client, app):
        """TC-B13: Can rebook same dates after cancellation releases them."""
        add_test_vehicle(client)

        with app.app_context():
            from app import get_db
            db = get_db(app)
            vehicle = db.execute("SELECT id FROM vehicles LIMIT 1").fetchone()
            vehicle_id = vehicle['id']

        # Book
        add_test_booking(client, vehicle_id=vehicle_id,
                         start='2027-02-01', end='2027-02-03')

        with app.app_context():
            from app import get_db
            db = get_db(app)
            booking = db.execute("SELECT id FROM bookings LIMIT 1").fetchone()
            booking_id = booking['id']

        # Cancel
        client.post(f'/bookings/cancel/{booking_id}', follow_redirects=True)

        # Rebook same dates
        response = add_test_booking(client, vehicle_id=vehicle_id,
                                    customer='New Customer',
                                    start='2027-02-01', end='2027-02-03')
        assert b'Booking created successfully' in response.data

    def test_cancel_nonexistent_booking(self, client):
        """TC-B18: Cancelling a nonexistent booking shows error."""
        response = client.post('/bookings/cancel/9999', follow_redirects=True)
        assert b'Booking not found' in response.data


class TestBookingPages:
    """Tests for booking page rendering."""

    def test_booking_list_page(self, client):
        """TC-B14: Booking list page loads successfully."""
        response = client.get('/bookings/')
        assert response.status_code == 200
        assert b'Bookings' in response.data

    def test_create_booking_page(self, client):
        """TC-B15: Create booking form page loads."""
        response = client.get('/bookings/create')
        assert response.status_code == 200
        assert b'New Booking' in response.data

    def test_view_booking_details(self, client, app):
        """TC-B16: View booking details page shows correct info."""
        add_test_vehicle(client)

        with app.app_context():
            from app import get_db
            db = get_db(app)
            vehicle = db.execute("SELECT id FROM vehicles LIMIT 1").fetchone()
            vehicle_id = vehicle['id']

        add_test_booking(client, vehicle_id=vehicle_id)

        with app.app_context():
            from app import get_db
            db = get_db(app)
            booking = db.execute("SELECT id FROM bookings LIMIT 1").fetchone()
            booking_id = booking['id']

        response = client.get(f'/bookings/view/{booking_id}')
        assert response.status_code == 200
        assert b'John Doe' in response.data
        assert b'Toyota Innova' in response.data

    def test_view_nonexistent_booking(self, client):
        """TC-B17: Viewing a nonexistent booking redirects with error."""
        response = client.get('/bookings/view/9999', follow_redirects=True)
        assert b'Booking not found' in response.data


class TestDatabasePersistence:
    """Tests for data persistence."""

    def test_booking_persists_in_database(self, client, app):
        """TC-B21: Booking data persists correctly in SQLite."""
        add_test_vehicle(client, rate='1500')

        with app.app_context():
            from app import get_db
            db = get_db(app)
            vehicle = db.execute("SELECT id FROM vehicles LIMIT 1").fetchone()
            vehicle_id = vehicle['id']

        add_test_booking(client, vehicle_id=vehicle_id,
                         customer='Persistent Test',
                         start='2027-03-01', end='2027-03-05')

        with app.app_context():
            from app import get_db
            db = get_db(app)
            booking = db.execute(
                "SELECT * FROM bookings WHERE customer_name = 'Persistent Test'"
            ).fetchone()
            assert booking is not None
            assert booking['vehicle_id'] == vehicle_id
            assert booking['start_date'] == '2027-03-01'
            assert booking['end_date'] == '2027-03-05'
            assert booking['total_days'] == 5  # inclusive
            assert booking['total_amount'] == 7500.0  # 5 × 1500
            assert booking['status'] == 'active'


class TestDashboard:
    """Tests for the dashboard page."""

    def test_dashboard_loads(self, client):
        """Dashboard page loads with statistics."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Dashboard' in response.data

    def test_dashboard_shows_stats(self, client, app):
        """Dashboard shows correct vehicle and booking counts."""
        add_test_vehicle(client, reg='MH-01-XX-0001', name='Car 1')
        add_test_vehicle(client, reg='MH-01-XX-0002', name='Car 2')
        response = client.get('/')
        assert b'2' in response.data  # Total vehicles


class TestBookingCompletion:
    """Tests for completing bookings (vehicle return workflow)."""

    def test_successful_booking_completion(self, client, app):
        """TC-B24: Mark active booking as completed and verify status."""
        add_test_vehicle(client)

        with app.app_context():
            from app import get_db
            db = get_db(app)
            vehicle = db.execute("SELECT id FROM vehicles LIMIT 1").fetchone()
            vehicle_id = vehicle['id']

        add_test_booking(client, vehicle_id=vehicle_id, start='2027-04-01', end='2027-04-03')

        with app.app_context():
            from app import get_db
            db = get_db(app)
            booking = db.execute("SELECT id FROM bookings WHERE status = 'active' LIMIT 1").fetchone()
            booking_id = booking['id']

        response = client.post(f'/bookings/complete/{booking_id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'marked as completed' in response.data

        with app.app_context():
            from app import get_db
            db = get_db(app)
            updated = db.execute("SELECT status FROM bookings WHERE id = ?", (booking_id,)).fetchone()
            assert updated['status'] == 'completed'

    def test_cannot_complete_already_completed_booking(self, client, app):
        """TC-B25: Reject completing an already completed booking."""
        add_test_vehicle(client)

        with app.app_context():
            from app import get_db
            db = get_db(app)
            vehicle = db.execute("SELECT id FROM vehicles LIMIT 1").fetchone()
            vehicle_id = vehicle['id']

        add_test_booking(client, vehicle_id=vehicle_id, start='2027-04-10', end='2027-04-12')

        with app.app_context():
            from app import get_db
            db = get_db(app)
            booking = db.execute("SELECT id FROM bookings WHERE status = 'active' LIMIT 1").fetchone()
            booking_id = booking['id']

        # Complete first time
        client.post(f'/bookings/complete/{booking_id}')

        # Attempt to complete second time
        response = client.post(f'/bookings/complete/{booking_id}', follow_redirects=True)
        assert b'Only active bookings can be marked as completed' in response.data

    def test_cannot_complete_cancelled_booking(self, client, app):
        """TC-B26: Reject completing a cancelled booking."""
        add_test_vehicle(client)

        with app.app_context():
            from app import get_db
            db = get_db(app)
            vehicle = db.execute("SELECT id FROM vehicles LIMIT 1").fetchone()
            vehicle_id = vehicle['id']

        add_test_booking(client, vehicle_id=vehicle_id, start='2027-04-15', end='2027-04-18')

        with app.app_context():
            from app import get_db
            db = get_db(app)
            booking = db.execute("SELECT id FROM bookings WHERE status = 'active' LIMIT 1").fetchone()
            booking_id = booking['id']

        client.post(f'/bookings/cancel/{booking_id}')

        response = client.post(f'/bookings/complete/{booking_id}', follow_redirects=True)
        assert b'Only active bookings can be marked as completed' in response.data

    def test_complete_nonexistent_booking(self, client):
        """TC-B27: Completing nonexistent booking redirects with error."""
        response = client.post('/bookings/complete/99999', follow_redirects=True)
        assert b'Booking not found' in response.data


class TestBookingExport:
    """Tests for CSV report export."""

    def test_export_csv_headers_and_content(self, client, app):
        """TC-B28: Export bookings as CSV with correct headers and records."""
        add_test_vehicle(client, reg='MH-04-EX-1000', name='Export Test Car', rate='3000')

        with app.app_context():
            from app import get_db
            db = get_db(app)
            vehicle = db.execute("SELECT id FROM vehicles WHERE registration_number = 'MH-04-EX-1000'").fetchone()
            vehicle_id = vehicle['id']

        add_test_booking(client, vehicle_id=vehicle_id, customer='Alice Exporter',
                         start='2027-05-01', end='2027-05-03')

        response = client.get('/bookings/export')
        assert response.status_code == 200
        assert response.mimetype == 'text/csv'
        assert 'Content-Disposition' in response.headers
        assert 'attachment; filename=rental_bookings_report.csv' in response.headers['Content-Disposition']

        csv_text = response.data.decode('utf-8')
        assert 'Booking ID,Customer Name,Vehicle Name,Registration Number' in csv_text
        assert 'Alice Exporter' in csv_text
        assert 'Export Test Car' in csv_text
        assert 'MH-04-EX-1000' in csv_text
        assert 'Active' in csv_text

