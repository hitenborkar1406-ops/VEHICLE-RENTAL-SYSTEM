"""
Booking Repository - Data access for booking operations.
"""

from typing import Optional, List, Dict, Any
import sqlite3
from datetime import date


class BookingRepository:
    """Repository for booking database operations."""

    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def get_all(self, status_filter: str = '', search: str = '',
                page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Get paginated list of bookings with vehicle info and optional filters."""
        query = """
            SELECT b.*, v.name as vehicle_name, v.registration_number, v.type as vehicle_type
            FROM bookings b
            JOIN vehicles v ON b.vehicle_id = v.id
            WHERE 1=1
        """
        count_query = """
            SELECT COUNT(*) as total
            FROM bookings b
            JOIN vehicles v ON b.vehicle_id = v.id
            WHERE 1=1
        """
        params = []

        if status_filter:
            query += " AND b.status = ?"
            count_query += " AND b.status = ?"
            params.append(status_filter)

        if search:
            query += " AND (b.customer_name LIKE ? OR v.name LIKE ? OR v.registration_number LIKE ?)"
            count_query += " AND (b.customer_name LIKE ? OR v.name LIKE ? OR v.registration_number LIKE ?)"
            params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])

        total = self.db.execute(count_query, params).fetchone()['total']
        total_pages = (total + per_page - 1) // per_page

        if page > total_pages and total_pages > 0:
            page = total_pages

        offset = (page - 1) * per_page
        query += " ORDER BY b.created_at DESC LIMIT ? OFFSET ?"
        params.extend([per_page, offset])

        bookings = self.db.execute(query, params).fetchall()

        return {
            'items': bookings,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages,
                'has_prev': page > 1,
                'has_next': page < total_pages,
                'prev_page': page - 1 if page > 1 else None,
                'next_page': page + 1 if page < total_pages else None,
            }
        }

    def get_by_id(self, booking_id: int) -> Optional[sqlite3.Row]:
        """Get booking by ID with vehicle info."""
        return self.db.execute(
            """SELECT b.*, v.name as vehicle_name, v.registration_number, 
                      v.type as vehicle_type, v.daily_rental_rate
               FROM bookings b
               JOIN vehicles v ON b.vehicle_id = v.id
               WHERE b.id = ?""",
            (booking_id,)
        ).fetchone()

    def get_by_id_simple(self, booking_id: int) -> Optional[sqlite3.Row]:
        """Get booking by ID without vehicle join."""
        return self.db.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()

    def get_active_by_vehicle(self, vehicle_id: int) -> List[sqlite3.Row]:
        """Get active bookings for a vehicle."""
        return self.db.execute(
            """SELECT * FROM bookings 
               WHERE vehicle_id = ? AND status = 'active'
               ORDER BY start_date""",
            (vehicle_id,)
        ).fetchall()

    def check_overlap(self, vehicle_id: int, start_date: str, end_date: str,
                      exclude_booking_id: Optional[int] = None) -> Optional[sqlite3.Row]:
        """Check for overlapping active bookings."""
        query = """
            SELECT id, start_date, end_date FROM bookings
            WHERE vehicle_id = ?
              AND status = 'active'
              AND start_date <= ?
              AND end_date >= ?
        """
        params = [vehicle_id, end_date, start_date]

        if exclude_booking_id is not None:
            query += " AND id != ?"
            params.append(exclude_booking_id)

        return self.db.execute(query, params).fetchone()

    def create(self, vehicle_id: int, customer_name: str, start_date: str,
               end_date: str, total_days: int, total_amount: float) -> int:
        """Create a new booking and return its ID. Caller must commit."""
        cursor = self.db.execute(
            """INSERT INTO bookings 
               (vehicle_id, customer_name, start_date, end_date, total_days, total_amount, status)
               VALUES (?, ?, ?, ?, ?, ?, 'active')""",
            (vehicle_id, customer_name, start_date, end_date, total_days, total_amount)
        )
        return cursor.lastrowid

    def cancel(self, booking_id: int) -> bool:
        """Cancel an active booking. Returns True if cancelled. Caller must commit."""
        cursor = self.db.execute(
            """UPDATE bookings 
               SET status = 'cancelled', updated_at = CURRENT_TIMESTAMP
               WHERE id = ? AND status = 'active'""",
            (booking_id,)
        )
        return cursor.rowcount > 0

    def complete(self, booking_id: int) -> bool:
        """Mark an active booking as completed. Returns True if completed. Caller must commit."""
        cursor = self.db.execute(
            """UPDATE bookings 
               SET status = 'completed', updated_at = CURRENT_TIMESTAMP
               WHERE id = ? AND status = 'active'""",
            (booking_id,)
        )
        return cursor.rowcount > 0

    def count_active_by_vehicle(self, vehicle_id: int, exclude_booking_id: Optional[int] = None) -> int:
        """Count active bookings for a vehicle."""
        query = "SELECT COUNT(*) as count FROM bookings WHERE vehicle_id = ? AND status = 'active'"
        params = [vehicle_id]
        if exclude_booking_id is not None:
            query += " AND id != ?"
            params.append(exclude_booking_id)
        return self.db.execute(query, params).fetchone()['count']

    def get_stats(self) -> Dict[str, int]:
        """Get booking statistics."""
        row = self.db.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
                SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
            FROM bookings
        """).fetchone()
        return {
            'total': row['total'] if row else 0,
            'active': row['active'] if row else 0,
            'cancelled': row['cancelled'] if row else 0,
            'completed': row['completed'] if row else 0,
        }

    def get_revenue(self) -> float:
        """Get total revenue from active and completed bookings."""
        row = self.db.execute("""
            SELECT COALESCE(SUM(total_amount), 0) as total_revenue
            FROM bookings
            WHERE status IN ('active', 'completed')
        """).fetchone()
        return row['total_revenue'] if row else 0.0

    def get_recent(self, limit: int = 5) -> List[sqlite3.Row]:
        """Get recent bookings with vehicle info."""
        return self.db.execute(
            """SELECT b.*, v.name as vehicle_name, v.registration_number
               FROM bookings b
               JOIN vehicles v ON b.vehicle_id = v.id
               ORDER BY b.created_at DESC
               LIMIT ?""",
            (limit,)
        ).fetchall()

    def get_all_for_export(self) -> List[sqlite3.Row]:
        """Get all bookings for CSV export."""
        return self.db.execute(
            """SELECT b.id, b.customer_name, v.name as vehicle_name, v.registration_number,
                      v.type as vehicle_type, b.start_date, b.end_date, b.total_days,
                      v.daily_rental_rate, b.total_amount, b.status, b.created_at
               FROM bookings b
               JOIN vehicles v ON b.vehicle_id = v.id
               ORDER BY b.created_at DESC"""
        ).fetchall()