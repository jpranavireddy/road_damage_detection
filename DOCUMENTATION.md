# Road Damage Detection System - Documentation

## Overview

This system implements automated road damage detection using UAV images and deep learning techniques, based on the research paper "Automated Road Damage Detection Using UAV Images and Deep Learning Techniques" by Silva et al.

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   AI Model     │
│   (Web UI)      │◄──►│   (Flask API)   │◄──►│  (YOLOv5/v7)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │    Database     │
                       │   (SQLite)      │
                       └─────────────────┘
```

## Features

### 1. Image Upload and Processing
- **Drag & Drop Interface**: Easy image upload with visual feedback
- **Multiple Format Support**: JPG, PNG, JPEG, GIF, BMP, TIFF
- **Image Preprocessing**: Automatic resizing and enhancement
- **Location Integration**: GPS coordinates and location names

### 2. AI-Powered Damage Detection
- **Deep Learning Models**: YOLOv4, YOLOv5, YOLOv7 support
- **Damage Classification**: 6 types of road damage
  - D00: Longitudinal Cracks
  - D10: Transverse Cracks
  - D20: Alligator Cracks
  - D40: Potholes
  - Repairs
  - Block Cracks
- **Confidence Scoring**: Reliability metrics for each detection
- **Bounding Box Visualization**: Visual damage localization

### 3. Interactive Dashboard
- **Real-time Statistics**: Total reports, damages, trends
- **Interactive Map**: Leaflet.js-powered damage location mapping
- **Data Visualization**: Charts and graphs for damage analysis
- **Report Management**: Detailed view of all detection reports

### 4. RESTful API
- **Upload Endpoint**: `/api/upload` - Process new images
- **Reports Endpoint**: `/api/reports` - Retrieve all reports
- **Statistics Endpoint**: `/api/stats` - Get system statistics
- **Individual Report**: `/api/reports/<id>` - Get specific report

## Installation Guide

### Prerequisites
- Python 3.8 or higher
- pip package manager
- 4GB+ RAM (recommended for AI model)
- Modern web browser

### Quick Installation
```bash
# Clone or download the project
cd road-damage-detection

# Run the installation script
python install.py

# Start the application
python run.py
```

### Manual Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p uploads static/detected_images models

# Initialize database
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Run the application
python run.py
```

## Configuration

### Environment Variables (.env)
```env
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
DATABASE_URL=sqlite:///road_damage.db
MODEL_PATH=models/road_damage_model.pt
CONFIDENCE_THRESHOLD=0.5
MAX_CONTENT_LENGTH=16777216
```

### Model Configuration
The system supports multiple YOLO model versions:
- **YOLOv4**: Legacy support, lower accuracy
- **YOLOv5**: Balanced performance and accuracy
- **YOLOv7**: Latest version, highest accuracy
- **YOLOv5 + Transformer**: Enhanced prediction head

## API Documentation

### Upload Image
```http
POST /api/upload
Content-Type: multipart/form-data

Parameters:
- image: Image file (required)
- latitude: GPS latitude (optional)
- longitude: GPS longitude (optional)
- location_name: Location description (optional)

Response:
{
  "success": true,
  "report_id": 123,
  "detections": {
    "detections": [...],
    "damage_types": [...],
    "confidence_scores": [...]
  },
  "message": "Detected 3 damage(s)"
}
```

### Get Reports
```http
GET /api/reports

Response:
[
  {
    "id": 1,
    "image_path": "uploads/image.jpg",
    "detected_image_path": "static/detected_images/detected_image.jpg",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "location_name": "Main Street",
    "damage_types": ["D40_Pothole", "D00_Longitudinal_Crack"],
    "confidence_scores": [0.85, 0.72],
    "detection_count": 2,
    "timestamp": "2024-01-15T10:30:00"
  }
]
```

### Get Statistics
```http
GET /api/stats

Response:
{
  "total_reports": 150,
  "total_damages": 287,
  "damage_type_stats": {
    "D40_Pothole": 45,
    "D00_Longitudinal_Crack": 38,
    "D20_Alligator_Crack": 22
  }
}
```

## Database Schema

### DamageReport Table
```sql
CREATE TABLE damage_report (
    id INTEGER PRIMARY KEY,
    image_path VARCHAR(255) NOT NULL,
    detected_image_path VARCHAR(255),
    latitude FLOAT,
    longitude FLOAT,
    location_name VARCHAR(255),
    damage_types TEXT,  -- JSON array
    confidence_scores TEXT,  -- JSON array
    detection_count INTEGER DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Model Training Guide

### Dataset Preparation
Based on the research paper methodology:

1. **Data Collection**
   - UAV images at 50m altitude
   - High resolution (3840x2160 pixels)
   - Various lighting and weather conditions

2. **Data Annotation**
   - Use tools like Roboflow or LabelImg
   - Annotate bounding boxes for each damage type
   - Maintain class balance across damage types

3. **Data Augmentation**
   - Rotation: -15° to +15°
   - Brightness adjustment
   - Contrast enhancement
   - Mosaic augmentation (YOLOv5/v7)

### Training Process
```bash
# YOLOv5 Training
python train.py --data road_damage.yaml --cfg yolov5s.yaml --weights yolov5s.pt --epochs 300

# YOLOv7 Training
python train.py --data road_damage.yaml --cfg yolov7.yaml --weights yolov7.pt --epochs 300
```

### Model Performance (from paper)
- **YOLOv4**: 26.8% mAP@0.5
- **YOLOv5**: 59.9% mAP@0.5
- **YOLOv7**: 73.2% mAP@0.5
- **YOLOv5 + Transformer**: 65.7% mAP@0.5

## Deployment Guide

### Development Deployment
```bash
python run.py
# Access at http://localhost:5000
```

### Production Deployment

#### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Using Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

#### Environment Configuration
```env
FLASK_ENV=production
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:password@localhost/road_damage
```

## Troubleshooting

### Common Issues

1. **Model Loading Errors**
   ```
   Error: Could not load model
   Solution: Ensure model file exists and is compatible
   ```

2. **Memory Issues**
   ```
   Error: CUDA out of memory
   Solution: Reduce batch size or use CPU inference
   ```

3. **Database Connection Errors**
   ```
   Error: Database locked
   Solution: Check file permissions and close other connections
   ```

### Performance Optimization

1. **Image Processing**
   - Resize images to 640x640 for faster inference
   - Use CLAHE for low-light image enhancement
   - Implement image caching

2. **Model Optimization**
   - Use TensorRT for GPU acceleration
   - Implement model quantization
   - Use smaller model variants for real-time processing

3. **Database Optimization**
   - Add indexes on frequently queried columns
   - Use connection pooling
   - Implement data archiving for old reports

## Testing

### Run Test Suite
```bash
python test_system.py
```

### Manual Testing
1. Upload test images through web interface
2. Verify detection results
3. Check dashboard functionality
4. Test API endpoints

## Contributing

### Code Structure
```
road-damage-detection/
├── app.py                 # Main Flask application
├── run.py                 # Application runner
├── config.py              # Configuration settings
├── models/
│   ├── damage_detector.py # AI model wrapper
│   └── __init__.py
├── templates/             # HTML templates
├── static/               # CSS, JS, images
├── utils/                # Utility functions
├── uploads/              # Uploaded images
└── requirements.txt      # Dependencies
```

### Development Guidelines
1. Follow PEP 8 style guidelines
2. Add docstrings to all functions
3. Write unit tests for new features
4. Update documentation for API changes

## License

This project is based on the research paper:
"Automated Road Damage Detection Using UAV Images and Deep Learning Techniques"
by Silva et al., published in IEEE Access.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the test results
3. Check system logs in the console
4. Ensure all dependencies are installed correctly

## Future Enhancements

1. **Real-time Processing**: Live video stream analysis
2. **Mobile App**: Native mobile application
3. **Advanced Analytics**: Predictive maintenance algorithms
4. **Multi-language Support**: Internationalization
5. **Cloud Integration**: AWS/Azure deployment options
6. **Batch Processing**: Multiple image upload and processing