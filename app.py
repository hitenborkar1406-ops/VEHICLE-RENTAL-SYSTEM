"""
Vehicle Rental System - Flask Application Factory
==================================================

Creates and configures the Flask application with:
- SQLite database connection management
- Foreign key enforcement
- Blueprint registration for vehicle and booking modules
- Database auto-initialization
"""

import os
import sqlite3
from flask import Flask, g
from schema import SCHEMA_SQL


def get_db(app=None):
    """
    Get a database connection for the current request.
    Connections are stored in Flask's g object and reused within a request.
    Foreign keys are enforced on every connection.
    """
    if 'db' not in g:
        from flask import current_app
        db_path = (app or current_app).config['DATABASE']
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
        g.db.execute("PRAGMA journal_mode = WAL")
    return g.db


def close_db(e=None):
    """Close the database connection at the end of a request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def seed_initial_data(conn):
    """Seed sample high-end vehicles and bookings if database is empty."""
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM vehicles")
    if c.fetchone()[0] > 0:
        return

    vehicles = [
        ('MH12BM0002', 'BMW M2 Competition', 'Car', 18000.0, 'available'),
        ('MH12BM0005', 'BMW M5 CS', 'Car', 32000.0, 'available'),
        ('MH12GW0063', 'Mercedes-AMG G63', 'SUV', 55000.0, 'available'),
        ('MH12LR7777', 'Range Rover Velar R-Dynamic', 'SUV', 28000.0, 'available'),
        ('MH12RR0001', 'Rolls-Royce Ghost Extended', 'Car', 95000.0, 'available'),
        ('MH12DU0004', 'Ducati Panigale V4 S', 'Motorcycle', 15000.0, 'available'),
        ('MH12GT0911', 'Porsche 911 GT3 RS', 'Car', 65000.0, 'maintenance'),
        ('MH12GT5000', 'Ford Mustang GT 5.0 V8', 'Car', 22000.0, 'available'),
        ('MH12SP3000', 'Toyota GR Supra 3.0 Pro', 'Car', 25000.0, 'available'),
        ('MH12LU6666', 'Lamborghini Urus Performante', 'SUV', 85000.0, 'available'),
        ('MH12ZX1000', 'Kawasaki Ninja ZX-10R', 'Motorcycle', 12000.0, 'available'),
        ('MH12BM1000', 'BMW S1000RR M Sport', 'Motorcycle', 16000.0, 'available'),
        ('MH12HD0114', 'Harley-Davidson Fat Boy 114', 'Motorcycle', 9500.0, 'available'),
        ('MH12SU1300', 'Suzuki Hayabusa GSX-1300R', 'Motorcycle', 14000.0, 'available'),
        ('MH12MB0008', 'Mercedes-Benz V-Class VIP', 'Van', 35000.0, 'available')
    ]
    c.executemany("""
        INSERT INTO vehicles (registration_number, name, type, daily_rental_rate, status)
        VALUES (?, ?, ?, ?, ?)
    """, vehicles)

    c.execute("SELECT id, registration_number FROM vehicles")
    v_map = {row[1]: row[0] for row in c.fetchall()}

    bookings = [
        (v_map.get('MH12BM0002', 1), 'John Smith', '2026-10-18', '2026-10-19', 2, 36000.0, 'active'),
        (v_map.get('MH12LR7777', 4), 'Hiten Borkar', '2026-10-19', '2026-10-23', 5, 140000.0, 'active'),
        (v_map.get('MH12DU0004', 6), 'Chirag_1406', '2026-10-30', '2026-11-13', 15, 225000.0, 'active')
    ]
    c.executemany("""
        INSERT INTO bookings (vehicle_id, customer_name, start_date, end_date, total_days, total_amount, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, bookings)
    conn.commit()


def init_db(app):
    """Initialize the database using the schema SQL and seed data if empty."""
    db_path = app.config['DATABASE']
    os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else '.', exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA_SQL)
    if not app.config.get('TESTING'):
        seed_initial_data(conn)
    conn.close()


def create_app(config=None):
    """
    Application factory for the Vehicle Rental System.

    Args:
        config: Optional dictionary of configuration overrides (used in testing).

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__, instance_relative_config=True)

    # Default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', os.urandom(24).hex()),
        DATABASE=os.path.join(app.instance_path, 'vehicle_rental.db'),
    )

    # Override with test configuration if provided
    if config:
        app.config.update(config)

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize database
    init_db(app)

    # Register teardown
    app.teardown_appcontext(close_db)

    # Register blueprints
    from vehicles import vehicles_bp
    from bookings import bookings_bp
    from dashboard import dashboard_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(vehicles_bp, url_prefix='/vehicles')
    app.register_blueprint(bookings_bp, url_prefix='/bookings')

    return app
