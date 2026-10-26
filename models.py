"""
Vehicle Rental System - SQLAlchemy Models for Alembic
======================================================

These models mirror the SQLite schema defined in schema.py for use with Alembic migrations.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index, CheckConstraint, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Vehicle(Base):
    """Vehicle model."""
    __tablename__ = 'vehicles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    registration_number = Column(String(50), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)
    daily_rental_rate = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default='available')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint('daily_rental_rate > 0', name='check_daily_rate_positive'),
        CheckConstraint("status IN ('available', 'rented', 'maintenance')", name='check_status_valid'),
        Index('idx_vehicles_status', 'status'),
        Index('idx_vehicles_registration', 'registration_number'),
    )

    def __repr__(self):
        return f"<Vehicle(id={self.id}, reg='{self.registration_number}', name='{self.name}')>"


class Booking(Base):
    """Booking model."""
    __tablename__ = 'bookings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False)
    customer_name = Column(String(100), nullable=False)
    start_date = Column(String(10), nullable=False)  # Stored as ISO format YYYY-MM-DD
    end_date = Column(String(10), nullable=False)
    total_days = Column(Integer, nullable=False)
    total_amount = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default='active')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint('total_days > 0', name='check_total_days_positive'),
        CheckConstraint('total_amount > 0', name='check_total_amount_positive'),
        CheckConstraint("status IN ('active', 'cancelled', 'completed')", name='check_booking_status_valid'),
        Index('idx_bookings_vehicle_id', 'vehicle_id'),
        Index('idx_bookings_status', 'status'),
        Index('idx_bookings_dates', 'start_date', 'end_date'),
    )

    def __repr__(self):
        return f"<Booking(id={self.id}, vehicle_id={self.vehicle_id}, customer='{self.customer_name}')>"