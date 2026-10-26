"""
Vehicle Repository - Data access for vehicle operations.
"""

from typing import Optional, List, Dict, Any
import sqlite3


class VehicleRepository:
    """Repository for vehicle database operations."""

    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def get_all(self, search: str = '', v_type: str = '', status: str = '',
                page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Get paginated list of vehicles with optional filters."""
        query = "SELECT * FROM vehicles WHERE 1=1"
        count_query = "SELECT COUNT(*) as total FROM vehicles WHERE 1=1"
        params = []

        if search:
            query += " AND (name LIKE ? OR registration_number LIKE ?)"
            count_query += " AND (name LIKE ? OR registration_number LIKE ?)"
            params.extend([f'%{search}%', f'%{search}%'])
        if v_type:
            query += " AND type = ?"
            count_query += " AND type = ?"
            params.append(v_type)
        if status:
            query += " AND status = ?"
            count_query += " AND status = ?"
            params.append(status)

        total = self.db.execute(count_query, params).fetchone()['total']
        total_pages = (total + per_page - 1) // per_page

        if page > total_pages and total_pages > 0:
            page = total_pages

        offset = (page - 1) * per_page
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([per_page, offset])

        vehicles = self.db.execute(query, params).fetchall()

        return {
            'items': vehicles,
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

    def get_by_id(self, vehicle_id: int) -> Optional[sqlite3.Row]:
        """Get vehicle by ID."""
        return self.db.execute("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,)).fetchone()

    def get_by_registration(self, registration_number: str) -> Optional[sqlite3.Row]:
        """Get vehicle by registration number."""
        return self.db.execute(
            "SELECT * FROM vehicles WHERE registration_number = ?",
            (registration_number,)
        ).fetchone()

    def create(self, registration_number: str, name: str, v_type: str,
               daily_rental_rate: float, status: str = 'available') -> int:
        """Create a new vehicle and return its ID."""
        cursor = self.db.execute(
            """INSERT INTO vehicles (registration_number, name, type, daily_rental_rate, status)
               VALUES (?, ?, ?, ?, ?)""",
            (registration_number, name, v_type, daily_rental_rate, status)
        )
        self.db.commit()
        return cursor.lastrowid

    def update(self, vehicle_id: int, registration_number: str, name: str,
               v_type: str, daily_rental_rate: float, status: str) -> bool:
        """Update vehicle details. Returns True if updated."""
        cursor = self.db.execute(
            """UPDATE vehicles 
               SET registration_number = ?, name = ?, type = ?, 
                   daily_rental_rate = ?, status = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (registration_number, name, v_type, daily_rental_rate, status, vehicle_id)
        )
        self.db.commit()
        return cursor.rowcount > 0

    def delete(self, vehicle_id: int) -> bool:
        """Delete vehicle by ID. Returns True if deleted."""
        cursor = self.db.execute("DELETE FROM vehicles WHERE id = ?", (vehicle_id,))
        self.db.commit()
        return cursor.rowcount > 0

    def has_bookings(self, vehicle_id: int) -> bool:
        """Check if vehicle has any bookings."""
        count = self.db.execute(
            "SELECT COUNT(*) as count FROM bookings WHERE vehicle_id = ?",
            (vehicle_id,)
        ).fetchone()['count']
        return count > 0

    def has_active_bookings(self, vehicle_id: int) -> bool:
        """Check if vehicle has active bookings."""
        count = self.db.execute(
            "SELECT COUNT(*) as count FROM bookings WHERE vehicle_id = ? AND status = 'active'",
            (vehicle_id,)
        ).fetchone()['count']
        return count > 0

    def update_status(self, vehicle_id: int, status: str) -> bool:
        """Update vehicle status."""
        cursor = self.db.execute(
            "UPDATE vehicles SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, vehicle_id)
        )
        self.db.commit()
        return cursor.rowcount > 0

    def get_available(self) -> List[sqlite3.Row]:
        """Get all available vehicles for booking."""
        return self.db.execute(
            "SELECT * FROM vehicles WHERE status = 'available' ORDER BY name"
        ).fetchall()

    def get_stats(self) -> Dict[str, int]:
        """Get vehicle statistics."""
        row = self.db.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'available' THEN 1 ELSE 0 END) as available,
                SUM(CASE WHEN status = 'rented' THEN 1 ELSE 0 END) as rented,
                SUM(CASE WHEN status = 'maintenance' THEN 1 ELSE 0 END) as maintenance
            FROM vehicles
        """).fetchone()
        return {
            'total': row['total'] if row else 0,
            'available': row['available'] if row else 0,
            'rented': row['rented'] if row else 0,
            'maintenance': row['maintenance'] if row else 0,
        }