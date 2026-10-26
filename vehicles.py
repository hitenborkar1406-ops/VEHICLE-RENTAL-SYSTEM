"""
Vehicle Rental System - Vehicle Management Blueprint
=====================================================

Handles all CRUD operations for vehicles:
- Add vehicle with validation
- View all vehicles with search/filter
- Edit vehicle details
- Delete vehicle (with booking constraint checks)

Validation Rules:
- Registration number: required, unique
- Name: required
- Type: required, must be one of predefined types
- Daily rental rate: required, must be positive number
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import get_db
from repositories.vehicles import VehicleRepository

vehicles_bp = Blueprint('vehicles', __name__)

# Allowed vehicle types
VEHICLE_TYPES = ['Car', 'SUV', 'Van', 'Truck', 'Motorcycle', 'Bus']
VEHICLE_STATUSES = ['available', 'rented', 'maintenance']


def validate_vehicle_data(data, repo: VehicleRepository, exclude_id=None):
    """
    Validate vehicle form data on the server side.

    Args:
        data: Dictionary with vehicle fields.
        repo: VehicleRepository for database operations.
        exclude_id: Vehicle ID to exclude from uniqueness check (for edits).

    Returns:
        List of error messages. Empty list means valid.
    """
    errors = []

    # Required fields
    reg_num = data.get('registration_number', '').strip()
    name = data.get('name', '').strip()
    v_type = data.get('type', '').strip()
    rate_str = data.get('daily_rental_rate', '').strip()

    if not reg_num:
        errors.append('Registration number is required.')
    if not name:
        errors.append('Vehicle name is required.')
    if not v_type:
        errors.append('Vehicle type is required.')
    elif v_type not in VEHICLE_TYPES:
        errors.append(f'Vehicle type must be one of: {", ".join(VEHICLE_TYPES)}.')

    # Rental rate validation
    if not rate_str:
        errors.append('Daily rental rate is required.')
    else:
        try:
            rate = float(rate_str)
            if rate <= 0:
                errors.append('Daily rental rate must be a positive number.')
        except ValueError:
            errors.append('Daily rental rate must be a valid number.')

    # Unique registration number
    if reg_num and not errors:
        existing = repo.get_by_registration(reg_num)
        if existing and (exclude_id is None or existing['id'] != exclude_id):
            errors.append('A vehicle with this registration number already exists.')

    # Prevent setting status to 'available' if vehicle has active bookings
    if exclude_id is not None:
        status = data.get('status', '').strip()
        if status == 'available':
            if repo.has_active_bookings(exclude_id):
                errors.append('Cannot set status to available: vehicle has active bookings.')

    return errors


@vehicles_bp.route('/')
def list_vehicles():
    """
    List all vehicles with optional search and filtering.

    Query Parameters:
        search: Search term for name or registration number.
        type: Filter by vehicle type.
        status: Filter by vehicle status.
        page: Page number (default 1)
        per_page: Items per page (default 10)
    """
    db = get_db()
    repo = VehicleRepository(db)
    search = request.args.get('search', '').strip()
    v_type = request.args.get('type', '').strip()
    status = request.args.get('status', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if page < 1:
        page = 1
    if per_page not in [10, 25, 50, 100]:
        per_page = 10

    result = repo.get_all(search=search, v_type=v_type, status=status, page=page, per_page=per_page)

    return render_template('vehicles/list.html',
                           vehicles=result['items'],
                           search=search,
                           selected_type=v_type,
                           selected_status=status,
                           vehicle_types=VEHICLE_TYPES,
                           vehicle_statuses=VEHICLE_STATUSES,
                           pagination=result['pagination'])


@vehicles_bp.route('/add', methods=['GET', 'POST'])
def add_vehicle():
    """Add a new vehicle with full server-side validation."""
    db = get_db()
    repo = VehicleRepository(db)

    if request.method == 'POST':
        data = request.form
        errors = validate_vehicle_data(data, repo)

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('vehicles/add.html',
                                   vehicle_types=VEHICLE_TYPES,
                                   form_data=data)

        repo.create(
            registration_number=data['registration_number'].strip(),
            name=data['name'].strip(),
            v_type=data['type'].strip(),
            daily_rental_rate=float(data['daily_rental_rate'].strip()),
            status=data.get('status', 'available').strip()
        )
        flash('Vehicle added successfully!', 'success')
        return redirect(url_for('vehicles.list_vehicles'))

    return render_template('vehicles/add.html',
                           vehicle_types=VEHICLE_TYPES,
                           form_data={})


@vehicles_bp.route('/edit/<int:vehicle_id>', methods=['GET', 'POST'])
def edit_vehicle(vehicle_id):
    """Edit an existing vehicle with validation."""
    db = get_db()
    repo = VehicleRepository(db)
    vehicle = repo.get_by_id(vehicle_id)

    if not vehicle:
        flash('Vehicle not found.', 'error')
        return redirect(url_for('vehicles.list_vehicles'))

    if request.method == 'POST':
        data = request.form
        errors = validate_vehicle_data(data, repo, exclude_id=vehicle_id)

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('vehicles/edit.html',
                                   vehicle=vehicle,
                                   vehicle_types=VEHICLE_TYPES,
                                   vehicle_statuses=VEHICLE_STATUSES,
                                   form_data=data)

        repo.update(
            vehicle_id=vehicle_id,
            registration_number=data['registration_number'].strip(),
            name=data['name'].strip(),
            v_type=data['type'].strip(),
            daily_rental_rate=float(data['daily_rental_rate'].strip()),
            status=data.get('status', vehicle['status']).strip()
        )
        flash('Vehicle updated successfully!', 'success')
        return redirect(url_for('vehicles.list_vehicles'))

    return render_template('vehicles/edit.html',
                           vehicle=vehicle,
                           vehicle_types=VEHICLE_TYPES,
                           vehicle_statuses=VEHICLE_STATUSES,
                           form_data={})


@vehicles_bp.route('/delete/<int:vehicle_id>', methods=['POST'])
def delete_vehicle(vehicle_id):
    """
    Delete a vehicle only if it has no booking history (active or past).
    This protects referential integrity and historical records.
    """
    db = get_db()
    repo = VehicleRepository(db)
    vehicle = repo.get_by_id(vehicle_id)

    if not vehicle:
        flash('Vehicle not found.', 'error')
        return redirect(url_for('vehicles.list_vehicles'))

    # Check for any bookings (active, completed, or cancelled)
    if repo.has_bookings(vehicle_id):
        flash(
            'Cannot delete this vehicle. It has booking record(s). '
            'Vehicles with booking history cannot be deleted to preserve records.',
            'error'
        )
        return redirect(url_for('vehicles.list_vehicles'))

    repo.delete(vehicle_id)
    flash('Vehicle deleted successfully!', 'success')
    return redirect(url_for('vehicles.list_vehicles'))
