"""
Vehicle Rental System - Dashboard Blueprint
===========================================

Provides the main dashboard with statistics about vehicles and bookings.
"""

from flask import Blueprint, render_template
from app import get_db

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

    # Vehicle statistics
    vehicle_stats_row = db.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'available' THEN 1 ELSE 0 END) as available,
            SUM(CASE WHEN status = 'rented' THEN 1 ELSE 0 END) as rented,
            SUM(CASE WHEN status = 'maintenance' THEN 1 ELSE 0 END) as maintenance
        FROM vehicles
    """).fetchone()

    vehicle_stats = {
        'total': safe_int(vehicle_stats_row['total']) if vehicle_stats_row else 0,
        'available': safe_int(vehicle_stats_row['available']) if vehicle_stats_row else 0,
        'rented': safe_int(vehicle_stats_row['rented']) if vehicle_stats_row else 0,
        'maintenance': safe_int(vehicle_stats_row['maintenance']) if vehicle_stats_row else 0,
    }

    # Booking statistics
    booking_stats_row = db.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
            SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
        FROM bookings
    """).fetchone()

    booking_stats = {
        'total': safe_int(booking_stats_row['total']) if booking_stats_row else 0,
        'active': safe_int(booking_stats_row['active']) if booking_stats_row else 0,
        'cancelled': safe_int(booking_stats_row['cancelled']) if booking_stats_row else 0,
        'completed': safe_int(booking_stats_row['completed']) if booking_stats_row else 0,
    }

    # Revenue (from active and completed bookings only)
    revenue_row = db.execute("""
        SELECT COALESCE(SUM(total_amount), 0) as total_revenue
        FROM bookings
        WHERE status IN ('active', 'completed')
    """).fetchone()

    revenue = {
        'total_revenue': safe_float(revenue_row['total_revenue']) if revenue_row else 0.0,
    }

    # Recent bookings (last 5)
    recent_bookings = db.execute("""
        SELECT b.*, v.name as vehicle_name, v.registration_number
        FROM bookings b
        JOIN vehicles v ON b.vehicle_id = v.id
        ORDER BY b.created_at DESC
        LIMIT 5
    """).fetchall()

    return render_template('dashboard.html',
                           vehicle_stats=vehicle_stats,
                           booking_stats=booking_stats,
                           revenue=revenue,
                           recent_bookings=recent_bookings)