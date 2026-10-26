"""
Vehicle Rental System - Repository Layer
=========================================

Data access layer providing abstraction over database operations.
"""

from repositories.vehicles import VehicleRepository
from repositories.bookings import BookingRepository

__all__ = ['VehicleRepository', 'BookingRepository']