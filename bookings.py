"""
Vehicle Rental System - Booking Management Blueprint
=====================================================

Handles all booking operations:
- Create a booking with overlap prevention
- View all bookings with status
- Cancel a booking (releases reserved dates)
- Server-side rental price calculation

Rental Calculation Rule (Inclusive):
    total_days = (end_date - start_date).days + 1
    total_amount = total_days * daily_rental_rate

    This means renting from Oct 1 to Oct 3 = 3 rental days.

Overlap Prevention:
    Active bookings for the same vehicle cannot have overlapping date ranges.
    Cancelled bookings do not block new reservations for those dates.

Race Condition Mitigation:
    Booking creation uses BEGIN IMMEDIATE to acquire a write lock
    before checking availability, reducing the window for duplicate
    reservations in concurrent scenarios.
"""

import csv
import io
from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from app import get_db
from repositories.bookings import BookingRepository
from repositories.vehicles import VehicleRepository

bookings_bp = Blueprint('bookings', __name__)


def validate_booking_data(data, booking_repo: BookingRepository, vehicle_repo: VehicleRepository,
                          exclude_booking_id=None):
    """
    Validate booking form data on the server side.

    Args:
        data: Dictionary with booking fields.
        booking_repo: BookingRepository for database operations.
        vehicle_repo: VehicleRepository for database operations.
        exclude_booking_id: Booking ID to exclude from overlap check (for future edits).

    Returns:
        Tuple of (errors_list, parsed_data_dict).
        parsed_data_dict contains vehicle_id, customer_name, start_date, end_date,
        total_days, total_amount if valid.
    """
    errors = []
    parsed = {}

    # Required fields
    vehicle_id_str = data.get('vehicle_id', '').strip()
    customer_name = data.get('customer_name', '').strip()
    start_date_str = data.get('start_date', '').strip()
    end_date_str = data.get('end_date', '').strip()

    if not vehicle_id_str:
        errors.append('Please select a vehicle.')
    if not customer_name:
        errors.append('Customer name is required.')
    if not start_date_str:
        errors.append('Start date is required.')
    if not end_date_str:
        errors.append('End date is required.')

    if errors:
        return errors, parsed

    # Parse vehicle ID
    try:
        vehicle_id = int(vehicle_id_str)
    except ValueError:
        errors.append('Invalid vehicle selection.')
        return errors, parsed

    # Check vehicle exists
    vehicle = vehicle_repo.get_by_id(vehicle_id)
    if not vehicle:
        errors.append('Selected vehicle does not exist.')
        return errors, parsed

    # Check vehicle is not in maintenance
    if vehicle['status'] == 'maintenance':
        errors.append('This vehicle is currently under maintenance and cannot be booked.')

    # Parse dates
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    except ValueError:
        errors.append('Start date must be in YYYY-MM-DD format.')
        return errors, parsed

    try:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        errors.append('End date must be in YYYY-MM-DD format.')
        return errors, parsed

    # Date validation
    today = date.today()
    if start_date < today:
        errors.append('Start date cannot be in the past.')
    if end_date < start_date:
        errors.append('End date must be on or after the start date.')

    if errors:
        return errors, parsed

    # Inclusive day calculation: end - start + 1
    total_days = (end_date - start_date).days + 1

    # Server-side price calculation (never trust browser-submitted prices)
    total_amount = total_days * vehicle['daily_rental_rate']

    # Check for overlapping active bookings
    overlapping = booking_repo.check_overlap(vehicle_id, start_date_str, end_date_str, exclude_booking_id)
    if overlapping:
        errors.append(
            f'This vehicle already has an active booking from '
            f'{overlapping["start_date"]} to {overlapping["end_date"]}. '
            f'Please choose different dates or cancel the existing booking.'
        )

    parsed = {
        'vehicle_id': vehicle_id,
        'customer_name': customer_name,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'total_days': total_days,
        'total_amount': round(total_amount, 2),
        'daily_rate': vehicle['daily_rental_rate'],
    }

    return errors, parsed


@bookings_bp.route('/')
def list_bookings():
    """List all bookings with vehicle info and status."""
    db = get_db()
    booking_repo = BookingRepository(db)
    status_filter = request.args.get('status', '').strip()
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if page < 1:
        page = 1
    if per_page not in [10, 25, 50, 100]:
        per_page = 10

    result = booking_repo.get_all(status_filter=status_filter, search=search, page=page, per_page=per_page)

    return render_template('bookings/list.html',
                           bookings=result['items'],
                           status_filter=status_filter,
                           search=search,
                           pagination=result['pagination'])


@bookings_bp.route('/create', methods=['GET', 'POST'])
def create_booking():
    """
    Create a new booking with full server-side validation.

    Uses BEGIN IMMEDIATE for the insert to reduce race conditions
    when multiple users might book the same vehicle simultaneously.
    """
    db = get_db()
    booking_repo = BookingRepository(db)
    vehicle_repo = VehicleRepository(db)

    if request.method == 'POST':
        data = request.form

        # Use BEGIN IMMEDIATE to acquire write lock early
        # This reduces the race condition window for concurrent bookings
        db.execute("BEGIN IMMEDIATE")
        try:
            errors, parsed = validate_booking_data(data, booking_repo, vehicle_repo)

            if errors:
                db.execute("ROLLBACK")
                for error in errors:
                    flash(error, 'error')
                vehicles = vehicle_repo.get_available()
                return render_template('bookings/create.html',
                                       vehicles=vehicles,
                                       form_data=data,
                                       today=date.today().isoformat())

            booking_repo.create(
                vehicle_id=parsed['vehicle_id'],
                customer_name=parsed['customer_name'],
                start_date=parsed['start_date'],
                end_date=parsed['end_date'],
                total_days=parsed['total_days'],
                total_amount=parsed['total_amount']
            )
            # Update vehicle status to rented
            vehicle_repo.update_status(parsed['vehicle_id'], 'rented')
            db.commit()
            flash(
                f'Booking created successfully! '
                f'{parsed["total_days"]} day(s) × ₹{parsed["daily_rate"]:.2f}/day = '
                f'₹{parsed["total_amount"]:.2f} total.',
                'success'
            )
            return redirect(url_for('bookings.list_bookings'))
        except Exception:
            db.execute("ROLLBACK")
            raise

    # Only show available vehicles for booking
    vehicles = vehicle_repo.get_available()

    # Pre-select vehicle if passed via query parameter
    preselected_vehicle_id = request.args.get('vehicle_id', type=int)
    form_data = {}
    if preselected_vehicle_id:
        form_data['vehicle_id'] = preselected_vehicle_id

    return render_template('bookings/create.html',
                           vehicles=vehicles,
                           form_data=form_data,
                           today=date.today().isoformat())


@bookings_bp.route('/cancel/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    """
    Cancel an active booking. This releases the reserved dates,
    allowing new bookings for those dates. The booking record is
    preserved for historical reference.
    """
    db = get_db()
    booking_repo = BookingRepository(db)
    vehicle_repo = VehicleRepository(db)

    db.execute("BEGIN IMMEDIATE")
    try:
        booking = booking_repo.get_by_id_simple(booking_id)

        if not booking:
            db.execute("ROLLBACK")
            flash('Booking not found.', 'error')
            return redirect(url_for('bookings.list_bookings'))

        if booking['status'] != 'active':
            db.execute("ROLLBACK")
            flash('Only active bookings can be cancelled.', 'error')
            return redirect(url_for('bookings.list_bookings'))

        vehicle_id = booking['vehicle_id']

        if not booking_repo.cancel(booking_id):
            db.execute("ROLLBACK")
            flash('Failed to cancel booking.', 'error')
            return redirect(url_for('bookings.list_bookings'))

        # Check if vehicle has any other active bookings
        other_active = booking_repo.count_active_by_vehicle(vehicle_id, exclude_booking_id=booking_id)

        if other_active == 0:
            vehicle_repo.update_status(vehicle_id, 'available')

        db.commit()
        flash('Booking cancelled successfully. The reserved dates are now available.', 'success')
        return redirect(url_for('bookings.list_bookings'))
    except Exception:
        db.execute("ROLLBACK")
        raise


@bookings_bp.route('/view/<int:booking_id>')
def view_booking(booking_id):
    """View detailed information about a specific booking."""
    db = get_db()
    booking_repo = BookingRepository(db)
    booking = booking_repo.get_by_id(booking_id)

    if not booking:
        flash('Booking not found.', 'error')
        return redirect(url_for('bookings.list_bookings'))

    return render_template('bookings/view.html', booking=booking)


@bookings_bp.route('/complete/<int:booking_id>', methods=['POST'])
def complete_booking(booking_id):
    """
    Mark an active booking as completed (e.g. vehicle returned).
    Finalizes the rental record and preserves revenue calculations.
    """
    db = get_db()
    booking_repo = BookingRepository(db)
    vehicle_repo = VehicleRepository(db)

    db.execute("BEGIN IMMEDIATE")
    try:
        booking = booking_repo.get_by_id_simple(booking_id)

        if not booking:
            db.execute("ROLLBACK")
            flash('Booking not found.', 'error')
            return redirect(url_for('bookings.list_bookings'))

        if booking['status'] != 'active':
            db.execute("ROLLBACK")
            flash('Only active bookings can be marked as completed.', 'error')
            return redirect(url_for('bookings.view_booking', booking_id=booking_id))

        vehicle_id = booking['vehicle_id']

        if not booking_repo.complete(booking_id):
            db.execute("ROLLBACK")
            flash('Failed to complete booking.', 'error')
            return redirect(url_for('bookings.view_booking', booking_id=booking_id))

        # Check if vehicle has any other active bookings
        other_active = booking_repo.count_active_by_vehicle(vehicle_id, exclude_booking_id=booking_id)

        if other_active == 0:
            vehicle_repo.update_status(vehicle_id, 'available')

        db.commit()
        flash(f'Booking #{booking_id} marked as completed. Vehicle return recorded.', 'success')
        return redirect(url_for('bookings.view_booking', booking_id=booking_id))
    except Exception:
        db.execute("ROLLBACK")
        raise


@bookings_bp.route('/export')
def export_csv():
    """
    Export all bookings as a downloadable CSV report.
    Includes customer, vehicle, pricing, and status details.
    """
    db = get_db()
    booking_repo = BookingRepository(db)
    bookings = booking_repo.get_all_for_export()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Booking ID', 'Customer Name', 'Vehicle Name', 'Registration Number',
        'Vehicle Type', 'Start Date', 'End Date', 'Total Days',
        'Daily Rate (INR)', 'Total Amount (INR)', 'Status', 'Created At'
    ])

    for row in bookings:
        writer.writerow([
            row['id'],
            row['customer_name'],
            row['vehicle_name'],
            row['registration_number'],
            row['vehicle_type'],
            row['start_date'],
            row['end_date'],
            row['total_days'],
            f"{row['daily_rental_rate']:.2f}",
            f"{row['total_amount']:.2f}",
            row['status'].title(),
            row['created_at']
        ])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=rental_bookings_report.csv'}
    )

