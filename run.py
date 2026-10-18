"""
Vehicle Rental System - Entry Point
====================================

Starts the Flask development server.
Usage: python run.py
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("  Vehicle Rental System")
    print("  Running at: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, port=5000)
