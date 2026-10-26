"""
Vehicle Rental System - Dashboard Blueprint
===========================================

Provides the main dashboard with statistics about vehicles and bookings.
"""

from flask import Blueprint, render_template
from app import get_db
from repositories.vehicles import VehicleRepository
from repositories.bookings import BookingRepository

dashboard_bp = Blueprint('dashboard', __name__)


def safe_int(value, default=0):
    """Safely convert value to int, returning default if None or invalid."""
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value, default=0.0):
    """Safely convert value to float, returning default if None or invalid."""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


@dashboard_bp.route('/')
def index():
    """
    Dashboard showing key statistics:
    - Total vehicles, available/rented/maintenance counts
    - Total bookings, active/cancelled/completed counts
    - Recent bookings
    - Revenue summary
    """
    db = get_db()
    vehicle_repo = VehicleRepository(db)
    booking_repo = BookingRepository(db)

    # Vehicle statistics
    vehicle_stats = vehicle_repo.get_stats()

    # Booking statistics
    booking_stats = booking_repo.get_stats()

    # Revenue (from active and completed bookings only)
    revenue = {
        'total_revenue': booking_repo.get_revenue(),
    }

    # Recent bookings (last 5)
    recent_bookings = booking_repo.get_recent(limit=5)

    return render_template('dashboard.html',
                           vehicle_stats=vehicle_stats,
                           booking_stats=booking_stats,
                           revenue=revenue,
                           recent_bookings=recent_bookings)