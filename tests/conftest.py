"""
Vehicle Rental System — Pytest Configuration
=============================================

Provides shared fixtures for isolated test databases.
Each test gets a fresh, temporary database via the app fixture.
"""

import os
import sys
import tempfile
import pytest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app


@pytest.fixture
def app():
    """
    Create a test application instance with an isolated temporary database.
    The database is automatically cleaned up after the test.
    """
    db_fd, db_path = tempfile.mkstemp(suffix='.db')

    test_app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'SECRET_KEY': 'test-secret-key',
    })

    yield test_app

    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Provide a test client for HTTP request simulation."""
    return app.test_client()


@pytest.fixture
def db(app):
    """Provide a direct database connection for test assertions."""
    with app.app_context():
        from app import get_db
        database = get_db(app)
        yield database


def add_test_vehicle(client, reg='MH-01-AB-1234', name='Toyota Innova',
                     v_type='Car', rate='2500'):
    """Helper to add a vehicle via HTTP POST."""
    return client.post('/vehicles/add', data={
        'registration_number': reg,
        'name': name,
        'type': v_type,
        'daily_rental_rate': rate,
    }, follow_redirects=True)


def add_test_booking(client, vehicle_id=1, customer='John Doe',
                     start='2027-01-10', end='2027-01-12'):
    """Helper to create a booking via HTTP POST."""
    return client.post('/bookings/create', data={
        'vehicle_id': str(vehicle_id),
        'customer_name': customer,
        'start_date': start,
        'end_date': end,
    }, follow_redirects=True)
