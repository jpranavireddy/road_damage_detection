from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
import cv2
import numpy as np
from datetime import datetime
import json
from werkzeug.utils import secure_filename
import base64
from io import BytesIO
from PIL import Image
import zipfile
import tempfile
import shutil

# Import our damage detection model and batch processor
from models.damage_detector import DamageDetector
from batch_processor import BatchRoadDamageProcessor

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///road_damage.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/detected_images', exist_ok=True)

# Initialize database
db = SQLAlchemy(app)

# Database Models
class DamageReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255), nullable=False)
    detected_image_path = db.Column(db.String(255), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    location_name = db.Column(db.String(255), nullable=True)
    damage_types = db.Column(db.Text, nullable=True)  # JSON string
    confidence_scores = db.Column(db.Text, nullable=True)  # JSON string
    detection_count = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'image_path': self.image_path,
            'detected_image_path': self.detected_image_path,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'location_name': self.location_name,
            'damage_types': json.loads(self.damage_types) if self.damage_types else [],
            'confidence_scores': json.loads(self.confidence_scores) if self.confidence_scores else [],
            'detection_count': self.detection_count,
            'timestamp': self.timestamp.isoformat()
        }

class BatchReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_name = db.Column(db.String(255), nullable=False)
    total_images = db.Column(db.Integer, nullable=False)
    damaged_count = db.Column(db.Integer, nullable=False)
    clean_count = db.Column(db.Integer, nullable=False)
    confidence_threshold = db.Column(db.Float, nullable=False)
    report_path = db.Column(db.String(500), nullable=True)
    html_report_path = db.Column(db.String(500), nullable=True)
    processing_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'flight_name': self.flight_name,
            'total_images': self.total_images,
            'damaged_count': self.damaged_count,
            'clean_count': self.clean_count,
            'damage_percentage': (self.damaged_count / self.total_images * 100) if self.total_images > 0 else 0,
            'confidence_threshold': self.confidence_threshold,
            'processing_timestamp': self.processing_timestamp.isoformat(),
            'report_url': f'/batch-report/{self.id}'
        }

# Initialize damage detector and batch processor
detector = DamageDetector()
batch_processor = BatchRoadDamageProcessor()

@app.route('/')
def index():
    return redirect(url_for('batch_upload'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/batch')
def batch_upload():
    return render_template('batch_upload.html')

@app.route('/batch-results')
def batch_results():
    return render_template('batch_results.html')

@app.route('/api/batch-upload', methods=['POST'])
def batch_upload_api():
    try:
        if 'folder' not in request.files:
            return jsonify({'error': 'No folder uploaded'}), 400
        
        files = request.files.getlist('folder')
        area_name = request.form.get('area_name', 'Unknown Area')
        flight_name = request.form.get('flight_name', f'Flight_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        confidence_threshold = float(request.form.get('confidence_threshold', 0.3))
        
        if not files:
            return jsonify({'error': 'No files in folder'}), 400
        
        # Create temporary directory for uploaded files
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Save uploaded files
            image_count = 0
            for file in files:
                if file.filename and batch_processor.is_image_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(temp_dir, filename)
                    file.save(file_path)
                    image_count += 1
            
            if image_count == 0:
                return jsonify({'error': 'No valid image files found'}), 400
            
            # Update batch processor confidence threshold
            batch_processor.confidence_threshold = confidence_threshold
            
            # Process the folder
            results = batch_processor.process_folder(temp_dir, flight_name, area_name)
            
            # Update area name in results
            if 'area_analysis' in results:
                results['area_analysis']['area_name'] = area_name
            
            # Generate web report
            html_report = batch_processor.generate_web_report(results)
            
            # Save batch results to database
            batch_report = BatchReport(
                flight_name=f"{area_name} - {flight_name}",
                total_images=results['summary']['total_images'],
                damaged_count=results['summary']['damaged_count'],
                clean_count=results['summary']['clean_count'],
                confidence_threshold=confidence_threshold,
                report_path=results['report_path'],
                html_report_path=html_report,
                processing_timestamp=datetime.utcnow()
            )
            
            db.session.add(batch_report)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'batch_id': batch_report.id,
                'summary': results['summary'],
                'html_report_url': f'/batch-report/{batch_report.id}',
                'message': f'Processed {image_count} images. Found {results["summary"]["damaged_count"]} damaged roads.'
            })
            
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/batch-report/<int:batch_id>')
def view_batch_report(batch_id):
    try:
        batch_report = BatchReport.query.get_or_404(batch_id)
        
        # Read the HTML report file
        if os.path.exists(batch_report.html_report_path):
            with open(batch_report.html_report_path, 'r') as f:
                html_content = f.read()
            return html_content
        else:
            return "Report not found", 404
            
    except Exception as e:
        return f"Error loading report: {str(e)}", 500

@app.route('/api/batch-reports')
def get_batch_reports():
    try:
        reports = BatchReport.query.order_by(BatchReport.processing_timestamp.desc()).all()
        return jsonify([report.to_dict() for report in reports])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Single image upload functionality removed - only batch processing supported
# @app.route('/api/upload', methods=['POST'])
# def upload_image():
#     # This functionality has been removed in favor of batch processing only
#     return jsonify({'error': 'Single image upload not supported. Please use batch processing.'}), 400

@app.route('/api/reports')
def get_reports():
    try:
        reports = DamageReport.query.order_by(DamageReport.timestamp.desc()).all()
        return jsonify([report.to_dict() for report in reports])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/<int:report_id>')
def get_report(report_id):
    try:
        report = DamageReport.query.get_or_404(report_id)
        return jsonify(report.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/output/<path:filename>')
def output_file(filename):
    return send_from_directory('output', filename)

@app.route('/output/detected_images/<filename>')
def detected_image(filename):
    return send_from_directory('output/detected_images', filename)

@app.route('/output/damaged_images/<filename>')
def damaged_image(filename):
    return send_from_directory('output/damaged_images', filename)

@app.route('/output/thumbnails/<filename>')
def thumbnail_image(filename):
    return send_from_directory('output/thumbnails', filename)

@app.route('/api/stats')
def get_stats():
    try:
        total_reports = DamageReport.query.count()
        total_damages = db.session.query(db.func.sum(DamageReport.detection_count)).scalar() or 0
        
        # Damage type statistics
        damage_stats = {}
        reports = DamageReport.query.all()
        for report in reports:
            if report.damage_types:
                types = json.loads(report.damage_types)
                for damage_type in types:
                    damage_stats[damage_type] = damage_stats.get(damage_type, 0) + 1
        
        return jsonify({
            'total_reports': total_reports,
            'total_damages': total_damages,
            'damage_type_stats': damage_stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=8080)