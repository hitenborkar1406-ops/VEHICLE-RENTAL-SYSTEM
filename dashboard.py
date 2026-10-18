"""
Vehicle Rental System - Dashboard Blueprint
=============================================

Provides the main dashboard with statistics about vehicles and bookings.
"""

from flask import Blueprint, render_template
from app import get_db

dashboard_bp = Blueprint('dashboard', __name__)


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
    vehicle_stats = db.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'available' THEN 1 ELSE 0 END) as available,
            SUM(CASE WHEN status = 'rented' THEN 1 ELSE 0 END) as rented,
            SUM(CASE WHEN status = 'maintenance' THEN 1 ELSE 0 END) as maintenance
        FROM vehicles
    """).fetchone()

    # Booking statistics
    booking_stats = db.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
            SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
        FROM bookings
    """).fetchone()

    # Revenue (from active and completed bookings only)
    revenue = db.execute("""
        SELECT COALESCE(SUM(total_amount), 0) as total_revenue
        FROM bookings
        WHERE status IN ('active', 'completed')
    """).fetchone()

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
