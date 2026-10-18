"""
Vehicle Rental System - Database Schema and Initialization
==========================================================

This module defines the SQLite database schema and provides
initialization routines for the Vehicle Rental System.

Tables:
    vehicles - Stores vehicle information (registration, name, type, rate, status)
    bookings - Stores rental bookings with foreign key to vehicles

Rental Calculation Rule (Inclusive):
    total_days = (end_date - start_date).days + 1
    total_amount = total_days * daily_rental_rate

    Example: Renting from 2026-10-01 to 2026-10-03 = 3 days
"""

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_number TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    daily_rental_rate REAL NOT NULL CHECK(daily_rental_rate > 0),
    status TEXT NOT NULL DEFAULT 'available' CHECK(status IN ('available', 'rented', 'maintenance')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER NOT NULL,
    customer_name TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    total_days INTEGER NOT NULL CHECK(total_days > 0),
    total_amount REAL NOT NULL CHECK(total_amount > 0),
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'cancelled', 'completed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
);

CREATE INDEX IF NOT EXISTS idx_bookings_vehicle_id ON bookings(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
CREATE INDEX IF NOT EXISTS idx_bookings_dates ON bookings(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_vehicles_status ON vehicles(status);
CREATE INDEX IF NOT EXISTS idx_vehicles_registration ON vehicles(registration_number);
"""
