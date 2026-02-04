#!/usr/bin/env python3
"""
Road Damage Detection System
Run script for the Flask application
"""

import os
import sys
from app import app, db

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        'uploads',
        'static/detected_images',
        'models'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Directory '{directory}' ready")

def initialize_database():
    """Initialize the database with tables"""
    with app.app_context():
        try:
            db.create_all()
            print("✓ Database initialized successfully")
        except Exception as e:
            print(f"✗ Error initializing database: {e}")
            return False
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'flask',
        'torch',
        'ultralytics',
        'opencv-python',
        'pillow',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} is missing")
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main function to run the application"""
    print("🚗 Road Damage Detection System")
    print("=" * 40)
    
    # Check dependencies
    print("\n1. Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    # Create directories
    print("\n2. Creating directories...")
    create_directories()
    
    # Initialize database
    print("\n3. Initializing database...")
    if not initialize_database():
        sys.exit(1)
    
    # Start the application
    print("\n4. Starting the application...")
    print("🌐 Access the application at: http://localhost:5000")
    print("📊 Dashboard available at: http://localhost:5000/dashboard")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 40)
    
    try:
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Thank you for using Road Damage Detection System!")

if __name__ == '__main__':
    main()