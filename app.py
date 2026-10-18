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


def init_db(app):
    """Initialize the database using the schema SQL."""
    db_path = app.config['DATABASE']
    os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else '.', exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA_SQL)
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
