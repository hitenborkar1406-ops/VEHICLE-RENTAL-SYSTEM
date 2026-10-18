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

vehicles_bp = Blueprint('vehicles', __name__)

# Allowed vehicle types
VEHICLE_TYPES = ['Car', 'SUV', 'Van', 'Truck', 'Motorcycle', 'Bus']
VEHICLE_STATUSES = ['available', 'rented', 'maintenance']


def validate_vehicle_data(data, db, exclude_id=None):
    """
    Validate vehicle form data on the server side.

    Args:
        data: Dictionary with vehicle fields.
        db: Database connection for uniqueness checks.
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
        query = "SELECT id FROM vehicles WHERE registration_number = ?"
        params = [reg_num]
        if exclude_id is not None:
            query += " AND id != ?"
            params.append(exclude_id)
        existing = db.execute(query, params).fetchone()
        if existing:
            errors.append('A vehicle with this registration number already exists.')

    return errors


@vehicles_bp.route('/')
def list_vehicles():
    """
    List all vehicles with optional search and filtering.

    Query Parameters:
        search: Search term for name or registration number.
        type: Filter by vehicle type.
        status: Filter by vehicle status.
    """
    db = get_db()
    search = request.args.get('search', '').strip()
    v_type = request.args.get('type', '').strip()
    status = request.args.get('status', '').strip()

    query = "SELECT * FROM vehicles WHERE 1=1"
    params = []

    if search:
        query += " AND (name LIKE ? OR registration_number LIKE ?)"
        params.extend([f'%{search}%', f'%{search}%'])
    if v_type:
        query += " AND type = ?"
        params.append(v_type)
    if status:
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY created_at DESC"
    vehicles = db.execute(query, params).fetchall()

    return render_template('vehicles/list.html',
                           vehicles=vehicles,
                           search=search,
                           selected_type=v_type,
                           selected_status=status,
                           vehicle_types=VEHICLE_TYPES,
                           vehicle_statuses=VEHICLE_STATUSES)


@vehicles_bp.route('/add', methods=['GET', 'POST'])
def add_vehicle():
    """Add a new vehicle with full server-side validation."""
    if request.method == 'POST':
        db = get_db()
        data = request.form
        errors = validate_vehicle_data(data, db)

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('vehicles/add.html',
                                   vehicle_types=VEHICLE_TYPES,
                                   form_data=data)

        db.execute(
            """INSERT INTO vehicles (registration_number, name, type, daily_rental_rate, status)
               VALUES (?, ?, ?, ?, ?)""",
            (
                data['registration_number'].strip(),
                data['name'].strip(),
                data['type'].strip(),
                float(data['daily_rental_rate'].strip()),
                data.get('status', 'available').strip()
            )
        )
        db.commit()
        flash('Vehicle added successfully!', 'success')
        return redirect(url_for('vehicles.list_vehicles'))

    return render_template('vehicles/add.html',
                           vehicle_types=VEHICLE_TYPES,
                           form_data={})


@vehicles_bp.route('/edit/<int:vehicle_id>', methods=['GET', 'POST'])
def edit_vehicle(vehicle_id):
    """Edit an existing vehicle with validation."""
    db = get_db()
    vehicle = db.execute("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,)).fetchone()

    if not vehicle:
        flash('Vehicle not found.', 'error')
        return redirect(url_for('vehicles.list_vehicles'))

    if request.method == 'POST':
        data = request.form
        errors = validate_vehicle_data(data, db, exclude_id=vehicle_id)

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('vehicles/edit.html',
                                   vehicle=vehicle,
                                   vehicle_types=VEHICLE_TYPES,
                                   vehicle_statuses=VEHICLE_STATUSES,
                                   form_data=data)

        db.execute(
            """UPDATE vehicles 
               SET registration_number = ?, name = ?, type = ?, 
                   daily_rental_rate = ?, status = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (
                data['registration_number'].strip(),
                data['name'].strip(),
                data['type'].strip(),
                float(data['daily_rental_rate'].strip()),
                data.get('status', vehicle['status']).strip(),
                vehicle_id
            )
        )
        db.commit()
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
    vehicle = db.execute("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,)).fetchone()

    if not vehicle:
        flash('Vehicle not found.', 'error')
        return redirect(url_for('vehicles.list_vehicles'))

    # Check for any bookings (active, completed, or cancelled)
    booking_count = db.execute(
        "SELECT COUNT(*) as count FROM bookings WHERE vehicle_id = ?",
        (vehicle_id,)
    ).fetchone()['count']

    if booking_count > 0:
        flash(
            f'Cannot delete this vehicle. It has {booking_count} booking record(s). '
            'Vehicles with booking history cannot be deleted to preserve records.',
            'error'
        )
        return redirect(url_for('vehicles.list_vehicles'))

    db.execute("DELETE FROM vehicles WHERE id = ?", (vehicle_id,))
    db.commit()
    flash('Vehicle deleted successfully!', 'success')
    return redirect(url_for('vehicles.list_vehicles'))
