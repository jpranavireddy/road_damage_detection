import cv2
import numpy as np
from ultralytics import YOLO
import os
from PIL import Image, ImageDraw, ImageFont

class DamageDetector:
    def __init__(self, model_path=None):
        """
        Initialize the damage detector with YOLOv8 model
        """
        # Damage class mapping based on the paper
        self.damage_classes = {
            0: 'D00_Longitudinal_Crack',
            1: 'D10_Transverse_Crack', 
            2: 'D20_Alligator_Crack',
            3: 'D40_Pothole',
            4: 'Repair',
            5: 'Block_Crack'
        }
        
        # Colors for different damage types
        self.colors = {
            'D00_Longitudinal_Crack': (255, 0, 0),    # Red
            'D10_Transverse_Crack': (0, 255, 0),      # Green
            'D20_Alligator_Crack': (0, 0, 255),       # Blue
            'D40_Pothole': (255, 255, 0),             # Yellow
            'Repair': (255, 0, 255),                  # Magenta
            'Block_Crack': (0, 255, 255)              # Cyan
        }
        
        # Load model (using YOLOv8 pretrained model for now)
        # In production, you would load your custom trained model
        try:
            if model_path and os.path.exists(model_path):
                self.model = YOLO(model_path)
            else:
                # Use a general object detection model as fallback
                # You should replace this with your trained road damage model
                self.model = YOLO('yolov8n.pt')
                print("Warning: Using general YOLOv8 model. Please provide trained road damage model.")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
    
    def detect_damage(self, image_path, confidence_threshold=0.5):
        """
        Detect road damage in the given image
        
        Args:
            image_path (str): Path to the input image
            confidence_threshold (float): Minimum confidence for detections
            
        Returns:
            dict: Detection results with damage types, locations, and confidence scores
        """
        if not self.model:
            return {
                'detections': [],
                'damage_types': [],
                'confidence_scores': [],
                'image_shape': None
            }
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Run inference
            results = self.model(image_path, conf=confidence_threshold)
            
            detections = []
            damage_types = []
            confidence_scores = []
            
            # Process results
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        # Map class ID to damage type (for demo purposes)
                        # In your trained model, these would be actual damage classes
                        damage_type = self._map_class_to_damage(class_id)
                        
                        detection = {
                            'bbox': [float(x1), float(y1), float(x2), float(y2)],
                            'confidence': float(confidence),
                            'damage_type': damage_type,
                            'class_id': class_id
                        }
                        
                        detections.append(detection)
                        damage_types.append(damage_type)
                        confidence_scores.append(float(confidence))
            
            return {
                'detections': detections,
                'damage_types': list(set(damage_types)),  # Unique damage types
                'confidence_scores': confidence_scores,
                'image_shape': image.shape
            }
            
        except Exception as e:
            print(f"Error in damage detection: {e}")
            return {
                'detections': [],
                'damage_types': [],
                'confidence_scores': [],
                'image_shape': None
            }
    
    def _map_class_to_damage(self, class_id):
        """
        Map YOLO class ID to damage type
        This is a demo mapping - replace with your actual trained model classes
        """
        # For demo purposes, map some common YOLO classes to damage types
        demo_mapping = {
            0: 'D40_Pothole',           # person -> pothole (demo)
            1: 'D00_Longitudinal_Crack', # bicycle -> crack (demo)
            2: 'D10_Transverse_Crack',   # car -> transverse crack (demo)
            3: 'D20_Alligator_Crack',    # motorcycle -> alligator crack (demo)
            4: 'Repair',                 # airplane -> repair (demo)
            5: 'Block_Crack'             # bus -> block crack (demo)
        }
        
        return demo_mapping.get(class_id, f'Unknown_Damage_{class_id}')
    
    def save_detected_image(self, image_path, detections, output_path):
        """
        Save image with detection bounding boxes and labels
        
        Args:
            image_path (str): Path to original image
            detections (dict): Detection results from detect_damage()
            output_path (str): Path to save the annotated image
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return False
            
            # Convert BGR to RGB for PIL
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image_rgb)
            draw = ImageDraw.Draw(pil_image)
            
            # Try to load a font
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            # Draw detections
            for detection in detections['detections']:
                bbox = detection['bbox']
                damage_type = detection['damage_type']
                confidence = detection['confidence']
                
                # Get color for this damage type
                color = self.colors.get(damage_type, (255, 255, 255))
                
                # Draw bounding box
                draw.rectangle(bbox, outline=color, width=3)
                
                # Draw label
                label = f"{damage_type}: {confidence:.2f}"
                text_bbox = draw.textbbox((0, 0), label, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                # Background for text
                draw.rectangle(
                    [bbox[0], bbox[1] - text_height - 5, bbox[0] + text_width + 10, bbox[1]],
                    fill=color
                )
                
                # Text
                draw.text((bbox[0] + 5, bbox[1] - text_height - 2), label, fill=(0, 0, 0), font=font)
            
            # Save image
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            pil_image.save(output_path)
            return True
            
        except Exception as e:
            print(f"Error saving detected image: {e}")
            return False
    
    def get_damage_statistics(self, detections):
        """
        Get statistics about detected damages
        
        Args:
            detections (dict): Detection results
            
        Returns:
            dict: Statistics about damage types and severity
        """
        if not detections['detections']:
            return {'total_damages': 0, 'damage_breakdown': {}}
        
        damage_breakdown = {}
        total_damages = len(detections['detections'])
        
        for detection in detections['detections']:
            damage_type = detection['damage_type']
            confidence = detection['confidence']
            
            if damage_type not in damage_breakdown:
                damage_breakdown[damage_type] = {
                    'count': 0,
                    'avg_confidence': 0,
                    'max_confidence': 0,
                    'min_confidence': 1.0
                }
            
            damage_breakdown[damage_type]['count'] += 1
            damage_breakdown[damage_type]['max_confidence'] = max(
                damage_breakdown[damage_type]['max_confidence'], confidence
            )
            damage_breakdown[damage_type]['min_confidence'] = min(
                damage_breakdown[damage_type]['min_confidence'], confidence
            )
        
        # Calculate average confidence for each damage type
        for damage_type in damage_breakdown:
            confidences = [d['confidence'] for d in detections['detections'] 
                          if d['damage_type'] == damage_type]
            damage_breakdown[damage_type]['avg_confidence'] = sum(confidences) / len(confidences)
        
        return {
            'total_damages': total_damages,
            'damage_breakdown': damage_breakdown
        }