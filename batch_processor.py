#!/usr/bin/env python3
"""
Batch Road Damage Detection System
Processes a folder of drone images and identifies only damaged roads
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
import cv2
import numpy as np
from models.damage_detector import DamageDetector
from utils.image_processing import ImageProcessor
from utils.damage_analysis import DamageAnalyzer
from utils.location_service import LocationService
import argparse

class BatchRoadDamageProcessor:
    def __init__(self, confidence_threshold=0.3):
        """
        Initialize batch processor
        
        Args:
            confidence_threshold (float): Minimum confidence for damage detection
        """
        self.detector = DamageDetector()
        self.image_processor = ImageProcessor()
        self.damage_analyzer = DamageAnalyzer()
        self.location_service = LocationService()
        self.confidence_threshold = confidence_threshold
        
        # Create output directories
        self.setup_output_directories()
        
    def setup_output_directories(self):
        """Create necessary output directories"""
        self.output_dirs = {
            'damaged_images': 'output/damaged_images',
            'clean_images': 'output/clean_images',
            'detected_images': 'output/detected_images',
            'reports': 'output/reports',
            'thumbnails': 'output/thumbnails'
        }
        
        for directory in self.output_dirs.values():
            os.makedirs(directory, exist_ok=True)
    
    def is_image_file(self, filename):
        """Check if file is a valid image"""
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        return Path(filename).suffix.lower() in valid_extensions
    
    def extract_gps_from_filename(self, filename):
        """
        Extract GPS coordinates from filename if available
        Expected format: image_lat40.7128_lon-74.0060_timestamp.jpg
        """
        try:
            basename = Path(filename).stem
            parts = basename.split('_')
            
            lat, lon = None, None
            for part in parts:
                if part.startswith('lat'):
                    lat = float(part[3:])
                elif part.startswith('lon'):
                    lon = float(part[3:])
            
            return lat, lon
        except:
            return None, None
    
    def process_single_image(self, image_path, output_prefix=""):
        """
        Process a single image for damage detection
        
        Args:
            image_path (str): Path to input image
            output_prefix (str): Prefix for output files
            
        Returns:
            dict: Processing results
        """
        print(f"Processing: {os.path.basename(image_path)}")
        
        try:
            # Get image info
            image_info = self.image_processor.get_image_info(image_path)
            if not image_info:
                return {'error': 'Could not read image'}
            
            # Extract GPS from filename
            lat, lon = self.extract_gps_from_filename(image_path)
            
            # Detect damage
            detections = self.detector.detect_damage(image_path, self.confidence_threshold)
            
            # Determine if image has damage
            has_damage = len(detections['detections']) > 0
            
            # Generate output filename
            base_name = Path(image_path).stem
            if output_prefix:
                base_name = f"{output_prefix}_{base_name}"
            
            result = {
                'original_path': image_path,
                'filename': os.path.basename(image_path),
                'has_damage': has_damage,
                'damage_count': len(detections['detections']),
                'damage_types': detections['damage_types'],
                'confidence_scores': detections['confidence_scores'],
                'detections': detections['detections'],
                'latitude': lat,
                'longitude': lon,
                'image_info': image_info,
                'timestamp': datetime.now().isoformat()
            }
            
            # Analyze damages in detail if present
            if has_damage:
                detailed_damages = []
                for detection in detections['detections']:
                    damage_analysis = self.damage_analyzer.analyze_single_damage(
                        detection, image_info['height'] if image_info else 640
                    )
                    detailed_damages.append(damage_analysis)
                
                result['detailed_damage_analysis'] = detailed_damages
                result['total_repair_cost'] = sum(d['repair_cost'] for d in detailed_damages)
                result['total_repair_time_hours'] = sum(d['repair_time_hours'] for d in detailed_damages)
                result['highest_priority'] = min(d['priority']['level'] for d in detailed_damages)
                result['most_severe'] = max(detailed_damages, key=lambda x: ['minor', 'moderate', 'severe', 'critical'].index(x['severity']))['severity']
            
            # Copy image to appropriate directory
            if has_damage:
                # Copy to damaged images directory
                damaged_path = os.path.join(self.output_dirs['damaged_images'], f"{base_name}.jpg")
                shutil.copy2(image_path, damaged_path)
                result['damaged_image_path'] = damaged_path
                
                # Create detected image with bounding boxes
                detected_path = os.path.join(self.output_dirs['detected_images'], f"detected_{base_name}.jpg")
                if self.detector.save_detected_image(image_path, detections, detected_path):
                    result['detected_image_path'] = detected_path
                
                # Create thumbnail
                thumbnail_path = os.path.join(self.output_dirs['thumbnails'], f"thumb_{base_name}.jpg")
                self.image_processor.create_thumbnail(image_path, thumbnail_path)
                result['thumbnail_path'] = thumbnail_path
                
                print(f"  ✅ DAMAGE DETECTED: {len(detections['detections'])} damages found")
                print(f"     Types: {', '.join(detections['damage_types'])}")
            else:
                # Copy to clean images directory
                clean_path = os.path.join(self.output_dirs['clean_images'], f"{base_name}.jpg")
                shutil.copy2(image_path, clean_path)
                result['clean_image_path'] = clean_path
                print(f"  ✅ CLEAN: No damage detected")
            
            return result
            
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
            return {'error': str(e), 'filename': os.path.basename(image_path)}
    
    def process_folder(self, input_folder, flight_name=None, area_name=None):
        """
        Process all images in a folder
        
        Args:
            input_folder (str): Path to folder containing drone images
            flight_name (str): Name of the flight/survey
            area_name (str): Name of the area being surveyed
            
        Returns:
            dict: Complete processing results
        """
        if not os.path.exists(input_folder):
            raise ValueError(f"Input folder does not exist: {input_folder}")
        
        # Store area name for location extraction
        self.current_area_name = area_name or flight_name or 'Unknown Area'
        
        # Get all image files
        image_files = []
        for root, dirs, files in os.walk(input_folder):
            for file in files:
                if self.is_image_file(file):
                    image_files.append(os.path.join(root, file))
        
        if not image_files:
            raise ValueError(f"No image files found in: {input_folder}")
        
        print(f"\n🚁 Processing drone survey: {flight_name or 'Unnamed Flight'}")
        print(f"📁 Input folder: {input_folder}")
        print(f"📸 Found {len(image_files)} images to process")
        print("=" * 60)
        
        # Process each image
        results = []
        damaged_images = []
        clean_images = []
        
        for i, image_path in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}] ", end="")
            
            result = self.process_single_image(image_path, flight_name)
            results.append(result)
            
            if result.get('has_damage', False):
                damaged_images.append(result)
            elif 'clean_image_path' in result:
                clean_images.append(result)
        
        # Generate summary report with detailed analysis
        summary = self.generate_summary_report(results, flight_name, input_folder)
        
        # Generate detailed area analysis
        all_detailed_damages = []
        for result in results:
            if result.get('has_damage', False) and 'detailed_damage_analysis' in result:
                for damage in result['detailed_damage_analysis']:
                    damage['source_image'] = result['filename']
                    damage['gps_location'] = {
                        'latitude': result.get('latitude'),
                        'longitude': result.get('longitude')
                    }
                    all_detailed_damages.append(damage)
        
        area_analysis = self.damage_analyzer.generate_area_summary(
            flight_name, all_detailed_damages, len(image_files)
        )
        
        # Save detailed report
        report_path = os.path.join(self.output_dirs['reports'], f"report_{flight_name or 'survey'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_path, 'w') as f:
            json.dump({
                'summary': summary,
                'area_analysis': area_analysis,
                'detailed_results': results
            }, f, indent=2)
        
        print(f"\n" + "=" * 60)
        print(f"🎉 Processing Complete!")
        print(f"📊 Summary:")
        print(f"   Total Images: {summary['total_images']}")
        print(f"   Damaged Roads: {summary['damaged_count']} ({summary['damage_percentage']:.1f}%)")
        print(f"   Clean Roads: {summary['clean_count']} ({summary['clean_percentage']:.1f}%)")
        print(f"   Processing Errors: {summary['error_count']}")
        print(f"\n📁 Output Directories:")
        print(f"   Damaged Images: {self.output_dirs['damaged_images']}")
        print(f"   Detected Images: {self.output_dirs['detected_images']}")
        print(f"   Clean Images: {self.output_dirs['clean_images']}")
        print(f"   Report: {report_path}")
        
        return {
            'summary': summary,
            'area_analysis': area_analysis,
            'damaged_images': damaged_images,
            'clean_images': clean_images,
            'report_path': report_path
        }
    
    def generate_summary_report(self, results, flight_name, input_folder):
        """Generate summary statistics"""
        total_images = len(results)
        damaged_count = sum(1 for r in results if r.get('has_damage', False))
        clean_count = sum(1 for r in results if 'clean_image_path' in r)
        error_count = sum(1 for r in results if 'error' in r)
        
        # Damage type statistics
        damage_type_stats = {}
        total_damages = 0
        confidence_scores = []
        
        for result in results:
            if result.get('has_damage', False):
                for damage_type in result.get('damage_types', []):
                    damage_type_stats[damage_type] = damage_type_stats.get(damage_type, 0) + 1
                
                total_damages += result.get('damage_count', 0)
                confidence_scores.extend(result.get('confidence_scores', []))
        
        # Calculate average confidence
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        return {
            'flight_name': flight_name,
            'input_folder': input_folder,
            'processing_timestamp': datetime.now().isoformat(),
            'total_images': total_images,
            'damaged_count': damaged_count,
            'clean_count': clean_count,
            'error_count': error_count,
            'damage_percentage': (damaged_count / total_images * 100) if total_images > 0 else 0,
            'clean_percentage': (clean_count / total_images * 100) if total_images > 0 else 0,
            'total_damages_detected': total_damages,
            'damage_type_statistics': damage_type_stats,
            'average_confidence': avg_confidence,
            'confidence_threshold_used': self.confidence_threshold
        }
    
    def generate_web_report(self, results_data, output_file=None):
        """Generate comprehensive HTML report for web viewing"""
        damaged_images = results_data['damaged_images']
        summary = results_data['summary']
        area_analysis = results_data.get('area_analysis', {})
        
        # Generate unique filename if not provided
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            flight_name = summary.get('flight_name', 'survey').replace(' ', '_').replace('-', '_')
            output_file = f"output/report_{flight_name}_{timestamp}.html"
        
        # Get proper map center based on area name and damage locations
        area_name = area_analysis.get('area_name', summary.get('flight_name', 'Unknown Area'))
        map_center = self.location_service.get_map_center_for_area(area_name, damaged_images)
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Road Damage Survey Report - {area_name}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        .damage-badge {{ border-radius: 20px; padding: 5px 15px; font-size: 0.8rem; font-weight: bold; }}
        .damage-D00 {{ background-color: #ff6b6b; color: white; }}
        .damage-D10 {{ background-color: #4ecdc4; color: white; }}
        .damage-D20 {{ background-color: #45b7d1; color: white; }}
        .damage-D40 {{ background-color: #f9ca24; color: black; }}
        .damage-Repair {{ background-color: #6c5ce7; color: white; }}
        .damage-Block {{ background-color: #a0a0a0; color: white; }}
        
        .severity-critical {{ background-color: #dc3545; color: white; }}
        .severity-severe {{ background-color: #fd7e14; color: white; }}
        .severity-moderate {{ background-color: #ffc107; color: black; }}
        .severity-minor {{ background-color: #28a745; color: white; }}
        
        .priority-1 {{ background-color: #dc3545; color: white; }}
        .priority-2 {{ background-color: #fd7e14; color: white; }}
        .priority-3 {{ background-color: #ffc107; color: black; }}
        .priority-4 {{ background-color: #28a745; color: white; }}
        
        #map {{ height: 400px; }}
        .image-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; }}
        .damage-card {{ border: 1px solid #ddd; border-radius: 15px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .damage-card img {{ width: 100%; height: 200px; object-fit: cover; cursor: pointer; }}
        .condition-excellent {{ background: linear-gradient(135deg, #28a745, #20c997); }}
        .condition-good {{ background: linear-gradient(135deg, #28a745, #ffc107); }}
        .condition-fair {{ background: linear-gradient(135deg, #ffc107, #fd7e14); }}
        .condition-poor {{ background: linear-gradient(135deg, #fd7e14, #dc3545); }}
        .condition-critical {{ background: linear-gradient(135deg, #dc3545, #6f42c1); }}
        
        .stats-card {{ border-radius: 15px; padding: 20px; margin-bottom: 20px; color: white; }}
        .detail-section {{ background: #f8f9fa; border-radius: 10px; padding: 20px; margin: 20px 0; }}
        .timeline-item {{ border-left: 3px solid #007bff; padding-left: 15px; margin-bottom: 15px; }}
        .cost-breakdown {{ background: white; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        
        .image-modal img {{ max-width: 100%; height: auto; }}
    </style>
</head>
<body>
    <div class="container-fluid">
        <!-- Header -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="text-center py-4" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px;">
                    <h1><i class="fas fa-road"></i> Road Damage Survey Report</h1>
                    <h3>{area_name}</h3>
                    <p class="mb-0">Survey Date: {area_analysis.get('survey_date', datetime.now().strftime('%Y-%m-%d'))[:10]}</p>
                </div>
            </div>
        </div>
        
        <!-- Overall Condition -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="stats-card condition-{area_analysis.get('overall_condition', 'good').lower()}">
                    <div class="row align-items-center">
                        <div class="col-md-8">
                            <h2><i class="fas fa-clipboard-check"></i> Overall Road Condition: {area_analysis.get('overall_condition', 'GOOD')}</h2>
                            <p class="h5">{area_analysis.get('condition_description', 'Assessment complete')}</p>
                        </div>
                        <div class="col-md-4 text-center">
                            <div class="display-4">
                                <i class="fas fa-{'exclamation-triangle' if area_analysis.get('overall_condition') in ['CRITICAL', 'POOR'] else 'check-circle' if area_analysis.get('overall_condition') == 'EXCELLENT' else 'info-circle'}"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        
        # Add summary statistics
        stats = area_analysis.get('summary_statistics', {})
        html_content += f"""
        <!-- Summary Statistics -->
        <div class="row mb-4">
            <div class="col-md-2">
                <div class="card text-center h-100">
                    <div class="card-body">
                        <i class="fas fa-images fa-2x text-primary mb-2"></i>
                        <h3 class="text-primary">{stats.get('total_images_surveyed', 0)}</h3>
                        <p class="mb-0">Images Surveyed</p>
                    </div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card text-center h-100">
                    <div class="card-body">
                        <i class="fas fa-exclamation-triangle fa-2x text-danger mb-2"></i>
                        <h3 class="text-danger">{stats.get('damaged_locations', 0)}</h3>
                        <p class="mb-0">Damaged Locations</p>
                    </div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card text-center h-100">
                    <div class="card-body">
                        <i class="fas fa-percentage fa-2x text-warning mb-2"></i>
                        <h3 class="text-warning">{stats.get('damage_rate_percentage', 0):.1f}%</h3>
                        <p class="mb-0">Damage Rate</p>
                    </div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card text-center h-100">
                    <div class="card-body">
                        <i class="fas fa-rupee-sign fa-2x text-success mb-2"></i>
                        <h3 class="text-success">₹{stats.get('total_repair_cost_usd', 0):,.0f}</h3>
                        <p class="mb-0">Repair Cost</p>
                    </div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card text-center h-100">
                    <div class="card-body">
                        <i class="fas fa-clock fa-2x text-info mb-2"></i>
                        <h3 class="text-info">{stats.get('total_repair_time_hours', 0):.0f}h</h3>
                        <p class="mb-0">Repair Time</p>
                    </div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card text-center h-100">
                    <div class="card-body">
                        <i class="fas fa-calendar fa-2x text-secondary mb-2"></i>
                        <h3 class="text-secondary">{stats.get('estimated_project_duration_days', 0)}</h3>
                        <p class="mb-0">Project Days</p>
                    </div>
                </div>
            </div>
        </div>
        """
        
        # Add detailed analysis sections if damage exists
        if area_analysis.get('summary_statistics', {}).get('damaged_locations', 0) > 0:
            html_content += self.generate_detailed_analysis_html(area_analysis)
        else:
            # Add message for clean area
            html_content += """
        <!-- Clean Area Message -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="alert alert-success">
                    <h4><i class="fas fa-check-circle"></i> Excellent News!</h4>
                    <p class="mb-0">No road damage was detected in this survey area. The road infrastructure appears to be in excellent condition.</p>
                </div>
            </div>
        </div>
        """
        
        # Add damaged images section if any exist
        if damaged_images:
            html_content += f"""
            <!-- Detailed Damage Analysis -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-search"></i> Detailed Damage Analysis ({len(damaged_images)} locations)</h5>
                        </div>
                        <div class="card-body">
                            <div class="image-grid">
            """
            
            # Add each damaged image with detailed analysis
            for i, img_data in enumerate(damaged_images):
                html_content += self.generate_damage_card_html(img_data, i)
            
            html_content += """
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """
        
        # Add recommendations and next steps
        if area_analysis.get('recommendations') and len(area_analysis.get('recommendations', [])) > 0:
            html_content += self.generate_recommendations_html(area_analysis)
        
        # Close HTML and add scripts with proper map centering
        html_content += self.generate_html_footer_with_map(damaged_images, map_center, area_name)
        
        # Save HTML report
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        print(f"📄 Comprehensive web report generated: {output_file}")
        return output_file
    
    def extract_location_info(self, img_data):
        """Extract location information from GPS data or area name"""
        # First try to get GPS coordinates from the image data
        if img_data.get('latitude') and img_data.get('longitude'):
            lat = img_data['latitude']
            lon = img_data['longitude']
            return f"GPS: {lat:.6f}, {lon:.6f}"
        
        # If no GPS data, try to extract from filename
        filename = img_data.get('filename', '')
        lat, lon = self.extract_gps_from_filename(filename)
        if lat and lon:
            return f"GPS: {lat:.6f}, {lon:.6f}"
        
        # Fallback to area name if available
        area_name = getattr(self, 'current_area_name', 'Unknown Location')
        return f"Area: {area_name}"
    
    def get_damage_badge_class(self, damage_type):
        """Get CSS class for damage type badge"""
        if 'D00' in damage_type or 'Longitudinal' in damage_type:
            return 'damage-D00'
        elif 'D10' in damage_type or 'Transverse' in damage_type:
            return 'damage-D10'
        elif 'D20' in damage_type or 'Alligator' in damage_type:
            return 'damage-D20'
        elif 'D40' in damage_type or 'Pothole' in damage_type:
            return 'damage-D40'
        elif 'Repair' in damage_type:
            return 'damage-Repair'
        else:
            return 'damage-Block'
    
    def generate_detailed_analysis_html(self, area_analysis):
        """Generate detailed analysis HTML sections"""
        html = ""
        
        # Budget breakdown
        budget = area_analysis.get('budget_breakdown', {})
        if budget:
            html += f"""
        <!-- Budget Breakdown -->
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-calculator"></i> Budget Breakdown</h5>
                    </div>
                    <div class="card-body">
                        <div class="cost-breakdown">
                            <div class="row">
                                <div class="col-6"><strong>Materials:</strong></div>
                                <div class="col-6 text-end">₹{budget.get('categories', {}).get('materials', 0):,.2f}</div>
                            </div>
                            <div class="row">
                                <div class="col-6"><strong>Labor:</strong></div>
                                <div class="col-6 text-end">₹{budget.get('categories', {}).get('labor', 0):,.2f}</div>
                            </div>
                            <div class="row">
                                <div class="col-6"><strong>Equipment:</strong></div>
                                <div class="col-6 text-end">₹{budget.get('categories', {}).get('equipment', 0):,.2f}</div>
                            </div>
                            <div class="row">
                                <div class="col-6"><strong>Traffic Control:</strong></div>
                                <div class="col-6 text-end">₹{budget.get('categories', {}).get('traffic_control', 0):,.2f}</div>
                            </div>
                            <div class="row">
                                <div class="col-6"><strong>Contingency:</strong></div>
                                <div class="col-6 text-end">₹{budget.get('categories', {}).get('contingency', 0):,.2f}</div>
                            </div>
                            <hr>
                            <div class="row">
                                <div class="col-6"><strong>Total Budget:</strong></div>
                                <div class="col-6 text-end"><strong>₹{budget.get('total_budget', 0):,.2f}</strong></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-users"></i> Resource Requirements</h5>
                    </div>
                    <div class="card-body">
                        <div class="cost-breakdown">
                            <div class="row mb-2">
                                <div class="col-8">Peak Crew Size:</div>
                                <div class="col-4 text-end"><strong>{area_analysis.get('resource_requirements', {}).get('peak_crew_size', 0)} workers</strong></div>
                            </div>
                            <div class="row mb-2">
                                <div class="col-8">Equipment Types:</div>
                                <div class="col-4 text-end">{area_analysis.get('resource_requirements', {}).get('total_equipment_types', 0)} types</div>
                            </div>
                            <div class="row mb-2">
                                <div class="col-8">Trucks Needed:</div>
                                <div class="col-4 text-end">{area_analysis.get('resource_requirements', {}).get('estimated_trucks_needed', 0)} trucks</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        
        return html
    
    def generate_damage_card_html(self, img_data, index):
        """Generate HTML for individual damage card with detailed analysis"""
        import math
        
        damage_types_html = ""
        
        # Basic damage types
        for damage_type in img_data.get('damage_types', []):
            badge_class = self.get_damage_badge_class(damage_type)
            damage_types_html += f'<span class="badge {badge_class} me-1 mb-1">{damage_type.replace("_", " ")}</span>'
        
        # Fix image paths - use Flask routes for serving images
        detected_img_path = img_data.get('detected_image_path', '')
        original_img_path = img_data.get('damaged_image_path', '')
        
        # Convert to Flask-compatible URLs
        if detected_img_path:
            if os.path.isabs(detected_img_path):
                detected_img_path = '/' + os.path.relpath(detected_img_path).replace('\\', '/')
            else:
                detected_img_path = '/' + detected_img_path.replace('\\', '/')
        
        if original_img_path:
            if os.path.isabs(original_img_path):
                original_img_path = '/' + os.path.relpath(original_img_path).replace('\\', '/')
            else:
                original_img_path = '/' + original_img_path.replace('\\', '/')
        
        # Fallback to detected image if original not available
        if not original_img_path:
            original_img_path = detected_img_path
        if not detected_img_path:
            detected_img_path = original_img_path
        
        # Calculate totals from detailed analysis
        total_cost = img_data.get('total_repair_cost', 0)
        total_time = img_data.get('total_repair_time_hours', 0)
        highest_priority = img_data.get('highest_priority', 4)
        most_severe = img_data.get('most_severe', 'minor')
        
        priority_class = f'priority-{highest_priority}'
        severity_class = f'severity-{most_severe}'
        
        # Extract location information from filename or use area name
        location_info = self.extract_location_info(img_data)
        
        html = f"""
                    <div class="damage-card">
                        <img src="{detected_img_path}" alt="Damage {index+1}" onclick="showDamageModal({index})" 
                             onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIE5vdCBGb3VuZDwvdGV4dD48L3N2Zz4='">
                        <div class="p-3">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <h6 class="mb-0">{img_data['filename']}</h6>
                                <span class="badge {priority_class}">Priority {highest_priority}</span>
                            </div>
                            
                            <div class="row mb-2">
                                <div class="col-6">
                                    <small><strong>Damages:</strong> {img_data['damage_count']}</small>
                                </div>
                                <div class="col-6">
                                    <small><strong>Severity:</strong> <span class="badge {severity_class}">{most_severe.title()}</span></small>
                                </div>
                            </div>
                            
                            <div class="mb-2">{damage_types_html}</div>
                            
                            <div class="detail-section">
                                <div class="row text-center">
                                    <div class="col-4">
                                        <div class="border-end">
                                            <strong class="text-success">₹{total_cost:,.0f}</strong>
                                            <br><small>Repair Cost</small>
                                        </div>
                                    </div>
                                    <div class="col-4">
                                        <div class="border-end">
                                            <strong class="text-info">{total_time:.1f}h</strong>
                                            <br><small>Repair Time</small>
                                        </div>
                                    </div>
                                    <div class="col-4">
                                        <strong class="text-warning">{math.ceil(total_time/8) if total_time > 0 else 0}</strong>
                                        <br><small>Work Days</small>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="mt-2 p-2 bg-light rounded">
                                <small class="text-muted">
                                    <i class="fas fa-map-marker-alt"></i>
                                    <strong>Location:</strong> {location_info}
                                </small>
                            </div>
                        </div>
                    </div>
        """
        
        return html
    
    def generate_recommendations_html(self, area_analysis):
        """Generate recommendations section HTML"""
        recommendations = area_analysis.get('recommendations', [])
        
        # Skip if no recommendations or if recommendations is not a list
        if not recommendations or not isinstance(recommendations, list):
            return ""
        
        html = """
        <!-- Recommendations -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-lightbulb"></i> Recommendations & Next Steps</h5>
                    </div>
                    <div class="card-body">
        """
        
        priority_colors = {
            'IMMEDIATE': 'danger',
            'URGENT': 'warning',
            'STRATEGIC': 'info',
            'PLANNING': 'primary',
            'PREVENTIVE': 'success'
        }
        
        for rec in recommendations:
            # Ensure rec is a dictionary
            if isinstance(rec, dict):
                color = priority_colors.get(rec.get('priority', 'PREVENTIVE'), 'info')
                html += f"""
                            <div class="alert alert-{color}">
                                <h6><i class="fas fa-arrow-right"></i> {rec.get('priority', 'RECOMMENDATION')}: {rec.get('action', '')}</h6>
                                <p class="mb-0"><small>{rec.get('reason', '')}</small></p>
                            </div>
                """
        
        html += """
                    </div>
                </div>
            </div>
        </div>
        """
        
        return html
    
    def generate_html_footer_with_map(self, damaged_images, map_center, area_name):
        """Generate HTML footer with scripts and modals (no map)"""
        html = """
    </div>
    
    <!-- Detailed Damage Modal -->
    <div class="modal fade" id="damageModal" tabindex="-1">
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Detailed Damage Analysis</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="damageModalBody">
                    <!-- Damage details will be loaded here -->
                </div>
            </div>
        </div>
    </div>
    
    <!-- Image Modal -->
    <div class="modal fade" id="imageModal" tabindex="-1">
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Image View</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body text-center">
                    <img id="modalImage" src="" class="img-fluid" style="max-height: 80vh;">
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Damage data for modal
        const damageData = """ + json.dumps(damaged_images, indent=2) + f""";
        
        // Show detailed damage modal
        function showDamageModal(index) {{
            const damage = damageData[index];
            const modalBody = document.getElementById('damageModalBody');
            
            // Fix image paths for modal display - use Flask routes
            let originalImagePath = damage.damaged_image_path || damage.detected_image_path;
            let detectedImagePath = damage.detected_image_path;
            
            // Ensure paths start with / for Flask routes
            if (originalImagePath && !originalImagePath.startsWith('/')) {{
                originalImagePath = '/' + originalImagePath;
            }}
            if (detectedImagePath && !detectedImagePath.startsWith('/')) {{
                detectedImagePath = '/' + detectedImagePath;
            }}
            
            let detailsHtml = `
                <div class="row">
                    <div class="col-md-6">
                        <h6>Original Image</h6>
                        <img src="${{originalImagePath}}" 
                             class="img-fluid rounded" 
                             onclick="showImageModal(this.src)"
                             style="cursor: pointer;"
                             onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIE5vdCBGb3VuZDwvdGV4dD48L3N2Zz4='">
                    </div>
                    <div class="col-md-6">
                        <h6>Detected Damages</h6>
                        <img src="${{detectedImagePath}}" 
                             class="img-fluid rounded"
                             onclick="showImageModal(this.src)"
                             style="cursor: pointer;"
                             onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIE5vdCBGb3VuZDwvdGV4dD48L3N2Zz4='">
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-12">
                        <h6>Location Information</h6>
                        <div class="alert alert-info">
                            <i class="fas fa-map-marker-alt"></i>
                            <strong>Location:</strong> ${{damage.latitude && damage.longitude ? 
                                `GPS Coordinates: ${{damage.latitude.toFixed(6)}}, ${{damage.longitude.toFixed(6)}}` : 
                                `Area: ${{'{area_name}'}}`
                            }}
                        </div>
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-12">
                        <h6>Repair Analysis</h6>
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Damage Type</th>
                                        <th>Severity</th>
                                        <th>Area (m²)</th>
                                        <th>Cost (₹)</th>
                                        <th>Time</th>
                                        <th>Method</th>
                                    </tr>
                                </thead>
                                <tbody>
            `;
            
            if (damage.detailed_damage_analysis) {{
                damage.detailed_damage_analysis.forEach(analysis => {{
                    detailsHtml += `
                                    <tr>
                                        <td>${{analysis.damage_type.replace(/_/g, ' ')}}</td>
                                        <td><span class="badge severity-${{analysis.severity}}">${{analysis.severity}}</span></td>
                                        <td>${{analysis.area_sqm}}</td>
                                        <td>₹${{analysis.repair_cost.toFixed(0)}}</td>
                                        <td>${{analysis.repair_time_hours}}h</td>
                                        <td><small>${{analysis.repair_method}}</small></td>
                                    </tr>
                    `;
                }});
            }}
            
            detailsHtml += `
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;
            
            modalBody.innerHTML = detailsHtml;
            new bootstrap.Modal(document.getElementById('damageModal')).show();
        }}
        
        // Show image in modal
        function showImageModal(imageSrc) {{
            document.getElementById('modalImage').src = imageSrc;
            new bootstrap.Modal(document.getElementById('imageModal')).show();
        }}
    </script>
</body>
</html>
        """
        
        return html

def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(description='Batch Road Damage Detection for Drone Images')
    parser.add_argument('input_folder', help='Path to folder containing drone images')
    parser.add_argument('--flight-name', '-n', help='Name of the flight/survey', default=None)
    parser.add_argument('--confidence', '-c', type=float, default=0.3, help='Confidence threshold (0.0-1.0)')
    parser.add_argument('--generate-web-report', '-w', action='store_true', help='Generate HTML web report')
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = BatchRoadDamageProcessor(confidence_threshold=args.confidence)
    
    try:
        # Process the folder
        results = processor.process_folder(args.input_folder, args.flight_name)
        
        # Generate web report if requested
        if args.generate_web_report:
            html_file = processor.generate_web_report(results)
            print(f"🌐 Open the web report: file://{os.path.abspath(html_file)}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    main()