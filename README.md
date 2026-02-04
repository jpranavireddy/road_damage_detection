# Road Damage Detection System

A web-based system for automated road damage detection using UAV images and deep learning techniques, based on the research paper "Automated Road Damage Detection Using UAV Images and Deep Learning Techniques".

## Features

- Upload road images for damage detection
- AI-powered damage classification (Longitudinal cracks, Potholes, Alligator cracks, etc.)
- Location-based damage mapping
- Web dashboard for viewing detected damages
- RESTful API for integration

## System Architecture

```
Frontend (React) → Backend (Flask/FastAPI) → AI Model (YOLOv5/v7) → Database (SQLite/PostgreSQL)
```

## Damage Classes Detected

- D00: Longitudinal cracks
- D10: Transverse cracks  
- D20: Alligator cracks
- D40: Potholes
- Repairs
- Block cracks

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python app.py`
4. Access the web interface at `http://localhost:5000`

## Usage

1. Upload road images through the web interface
2. Add GPS coordinates or location information
3. View detected damages on the interactive map
4. Export damage reports

## Technology Stack

- **Backend**: Flask/FastAPI
- **Frontend**: HTML, CSS, JavaScript (with optional React)
- **AI Model**: YOLOv5/YOLOv7 for object detection
- **Database**: SQLite for development, PostgreSQL for production
- **Mapping**: Leaflet.js for interactive maps# road_damage_detection
