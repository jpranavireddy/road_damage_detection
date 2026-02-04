#!/usr/bin/env python3
"""
Test script for Road Damage Detection System
"""

import os
import sys
import requests
import json
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    required_modules = [
        'flask',
        'cv2',
        'numpy',
        'PIL',
        'ultralytics'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    return len(failed_imports) == 0

def test_directories():
    """Test if required directories exist"""
    print("\nTesting directories...")
    
    required_dirs = [
        'uploads',
        'static/detected_images',
        'models',
        'templates'
    ]
    
    missing_dirs = []
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ {directory}")
        else:
            print(f"❌ {directory}")
            missing_dirs.append(directory)
    
    return len(missing_dirs) == 0

def test_files():
    """Test if required files exist"""
    print("\nTesting files...")
    
    required_files = [
        'app.py',
        'run.py',
        'requirements.txt',
        'models/damage_detector.py',
        'templates/index.html',
        'templates/dashboard.html'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def test_damage_detector():
    """Test the damage detector module"""
    print("\nTesting damage detector...")
    
    try:
        from models.damage_detector import DamageDetector
        
        detector = DamageDetector()
        print("✅ DamageDetector initialized")
        
        # Test damage class mapping
        if hasattr(detector, 'damage_classes'):
            print(f"✅ Damage classes defined: {len(detector.damage_classes)} types")
        else:
            print("❌ Damage classes not defined")
            return False
        
        # Test color mapping
        if hasattr(detector, 'colors'):
            print(f"✅ Color mapping defined: {len(detector.colors)} colors")
        else:
            print("❌ Color mapping not defined")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing damage detector: {e}")
        return False

def test_flask_app():
    """Test if Flask app can be imported and configured"""
    print("\nTesting Flask application...")
    
    try:
        from app import app, db
        
        print("✅ Flask app imported successfully")
        
        # Test app configuration
        if app.config.get('SECRET_KEY'):
            print("✅ Secret key configured")
        else:
            print("⚠️  Secret key not configured")
        
        if app.config.get('SQLALCHEMY_DATABASE_URI'):
            print("✅ Database URI configured")
        else:
            print("❌ Database URI not configured")
            return False
        
        # Test database models
        with app.app_context():
            try:
                db.create_all()
                print("✅ Database models created successfully")
            except Exception as e:
                print(f"❌ Error creating database: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Flask app: {e}")
        return False

def create_test_image():
    """Create a simple test image for testing"""
    print("\nCreating test image...")
    
    try:
        import numpy as np
        import cv2
        
        # Create a simple test image
        test_image = np.zeros((640, 640, 3), dtype=np.uint8)
        test_image[:, :] = (100, 150, 200)  # Light blue background
        
        # Add some simple shapes to simulate road features
        cv2.rectangle(test_image, (100, 100), (540, 540), (80, 80, 80), -1)  # Road surface
        cv2.line(test_image, (320, 100), (320, 540), (255, 255, 255), 5)     # Center line
        
        # Save test image
        test_image_path = 'test_road_image.jpg'
        cv2.imwrite(test_image_path, test_image)
        
        print(f"✅ Test image created: {test_image_path}")
        return test_image_path
        
    except Exception as e:
        print(f"❌ Error creating test image: {e}")
        return None

def run_detection_test(test_image_path):
    """Test the detection functionality"""
    print("\nTesting damage detection...")
    
    if not test_image_path or not os.path.exists(test_image_path):
        print("❌ No test image available")
        return False
    
    try:
        from models.damage_detector import DamageDetector
        
        detector = DamageDetector()
        results = detector.detect_damage(test_image_path)
        
        print(f"✅ Detection completed")
        print(f"   Detections found: {len(results.get('detections', []))}")
        print(f"   Damage types: {results.get('damage_types', [])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in detection test: {e}")
        return False

def cleanup_test_files():
    """Clean up test files"""
    test_files = ['test_road_image.jpg']
    
    for file_path in test_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🧹 Cleaned up: {file_path}")

def main():
    """Run all tests"""
    print("🧪 Road Damage Detection System - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Directory Test", test_directories),
        ("File Test", test_files),
        ("Damage Detector Test", test_damage_detector),
        ("Flask App Test", test_flask_app)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    # Additional detection test
    print(f"\n--- Detection Test ---")
    test_image_path = create_test_image()
    if test_image_path and run_detection_test(test_image_path):
        passed_tests += 1
        print("✅ Detection Test PASSED")
        total_tests += 1
    else:
        print("❌ Detection Test FAILED")
        total_tests += 1
    
    # Cleanup
    cleanup_test_files()
    
    # Summary
    print("\n" + "=" * 50)
    print(f"Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! System is ready to use.")
        print("\nTo start the application, run:")
        print("   python run.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nTo install missing dependencies, run:")
        print("   pip install -r requirements.txt")
    
    print("=" * 50)

if __name__ == "__main__":
    main()