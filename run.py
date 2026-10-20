"""
Vehicle Rental System - Entry Point
====================================

Starts the Flask development server.
Usage: python run.py
"""

import os
from app import create_app

app = create_app()
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 60)
    print("  Vehicle Rental System")
    print(f"  Running on port: {port}")
    print("=" * 60)
    app.run(debug=False, port=port, host='0.0.0.0')
