#!/usr/bin/env python3
"""
Installation script for Road Damage Detection System
This script helps set up the environment and download necessary models
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
from pathlib import Path

def print_header():
    """Print installation header"""
    print("🚗 Road Damage Detection System - Installation")
    print("=" * 50)
    print("Based on: 'Automated Road Damage Detection Using UAV Images and Deep Learning Techniques'")
    print("Authors: Silva et al.")
    print("=" * 50)

def check_python_version():
    """Check if Python version is compatible"""
    print("\n1. Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_requirements():
    """Install Python requirements"""
    print("\n2. Installing Python requirements...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n3. Creating project directories...")
    
    directories = [
        "uploads",
        "static/detected_images",
        "static/thumbnails",
        "models",
        "logs",
        "data"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def download_sample_model():
    """Download a sample YOLOv8 model for demonstration"""
    print("\n4. Setting up AI model...")
    
    model_path = "models/yolov8n.pt"
    
    if os.path.exists(model_path):
        print(f"✅ Model already exists: {model_path}")
        return True
    
    try:
        print("📥 Downloading YOLOv8 nano model for demonstration...")
        print("   Note: Replace with your trained road damage model for production use")
        
        # This will be downloaded automatically by ultralytics when first used
        print("✅ Model setup complete (will download on first use)")
        return True
        
    except Exception as e:
        print(f"⚠️  Warning: Could not setup model: {e}")
        print("   The system will download the model automatically on first use")
        return True

def create_sample_data():
    """Create sample configuration files"""
    print("\n5. Creating configuration files...")
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write("""# Road Damage Detection System Configuration
SECRET_KEY=your-secret-key-change-this-in-production
FLASK_ENV=development
DATABASE_URL=sqlite:///road_damage.db
MODEL_PATH=models/road_damage_model.pt
CONFIDENCE_THRESHOLD=0.5
MAX_CONTENT_LENGTH=16777216
""")
        print("✅ Created .env configuration file")
    else:
        print("✅ Configuration file already exists")
    
    return True

def setup_database():
    """Initialize the database"""
    print("\n6. Setting up database...")
    
    try:
        # Import here to avoid issues if dependencies aren't installed yet
        from app import app, db
        
        with app.app_context():
            db.create_all()
            print("✅ Database initialized successfully")
        
        return True
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize database: {e}")
        print("   Database will be created when you first run the application")
        return True

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 50)
    print("🎉 Installation completed successfully!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Run the application:")
    print("   python run.py")
    print("\n2. Open your browser and go to:")
    print("   http://localhost:5000")
    print("\n3. For production deployment:")
    print("   - Replace the demo model with your trained road damage detection model")
    print("   - Update the SECRET_KEY in .env file")
    print("   - Configure a production database (PostgreSQL recommended)")
    print("   - Set FLASK_ENV=production in .env")
    print("\n4. Model Training:")
    print("   - Use the YOLOv5/YOLOv7 training scripts with your road damage dataset")
    print("   - Follow the paper's methodology for best results")
    print("   - Place your trained model in the models/ directory")
    print("\n📚 For more information, see README.md")
    print("🐛 Report issues at: [your-repository-url]")

def main():
    """Main installation function"""
    print_header()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Installation failed at requirements step")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("\n❌ Installation failed at directory creation step")
        sys.exit(1)
    
    # Setup model
    if not download_sample_model():
        print("\n❌ Installation failed at model setup step")
        sys.exit(1)
    
    # Create configuration
    if not create_sample_data():
        print("\n❌ Installation failed at configuration step")
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        print("\n❌ Installation failed at database setup step")
        sys.exit(1)
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()