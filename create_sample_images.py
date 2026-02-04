#!/usr/bin/env python3
"""
Create sample drone road images for testing the batch processing system
"""

import cv2
import numpy as np
import os
from datetime import datetime, timedelta
import random

def create_sample_road_image(width=640, height=640, has_damage=False, damage_type='pothole'):
    """Create a synthetic road image with or without damage"""
    
    # Create base road surface
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Road surface (dark gray asphalt)
    road_color = (60, 60, 60)
    image[:, :] = road_color
    
    # Add some texture to make it look more realistic
    noise = np.random.normal(0, 10, (height, width, 3))
    image = np.clip(image.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    
    # Add road markings
    # Center line
    cv2.line(image, (width//2, 0), (width//2, height), (255, 255, 255), 4)
    
    # Lane markings (dashed lines)
    for y in range(0, height, 40):
        cv2.line(image, (width//4, y), (width//4, y+20), (255, 255, 255), 2)
        cv2.line(image, (3*width//4, y), (3*width//4, y+20), (255, 255, 255), 2)
    
    # Add edge lines
    cv2.line(image, (50, 0), (50, height), (255, 255, 255), 3)
    cv2.line(image, (width-50, 0), (width-50, height), (255, 255, 255), 3)
    
    if has_damage:
        if damage_type == 'pothole':
            # Create potholes (dark circular areas)
            for _ in range(random.randint(1, 3)):
                center_x = random.randint(100, width-100)
                center_y = random.randint(100, height-100)
                radius = random.randint(15, 40)
                cv2.circle(image, (center_x, center_y), radius, (20, 20, 20), -1)
                # Add some irregular edges
                cv2.circle(image, (center_x, center_y), radius-5, (10, 10, 10), -1)
        
        elif damage_type == 'crack':
            # Create cracks (dark lines)
            for _ in range(random.randint(1, 4)):
                start_x = random.randint(0, width)
                start_y = random.randint(0, height//2)
                end_x = random.randint(0, width)
                end_y = random.randint(height//2, height)
                
                # Create jagged crack line
                points = []
                steps = 10
                for i in range(steps + 1):
                    t = i / steps
                    x = int(start_x + t * (end_x - start_x) + random.randint(-20, 20))
                    y = int(start_y + t * (end_y - start_y) + random.randint(-10, 10))
                    points.append((x, y))
                
                for i in range(len(points) - 1):
                    cv2.line(image, points[i], points[i+1], (30, 30, 30), random.randint(2, 5))
        
        elif damage_type == 'alligator':
            # Create alligator cracks (interconnected cracks)
            center_x = random.randint(width//4, 3*width//4)
            center_y = random.randint(height//4, 3*height//4)
            
            # Create multiple intersecting cracks
            for angle in range(0, 360, 45):
                end_x = center_x + int(60 * np.cos(np.radians(angle)))
                end_y = center_y + int(60 * np.sin(np.radians(angle)))
                cv2.line(image, (center_x, center_y), (end_x, end_y), (25, 25, 25), 3)
            
            # Add some random connecting lines
            for _ in range(5):
                x1 = center_x + random.randint(-40, 40)
                y1 = center_y + random.randint(-40, 40)
                x2 = center_x + random.randint(-40, 40)
                y2 = center_y + random.randint(-40, 40)
                cv2.line(image, (x1, y1), (x2, y2), (25, 25, 25), 2)
    
    # Add some environmental elements
    # Shadows from trees/buildings
    if random.random() > 0.7:
        shadow_overlay = np.zeros_like(image)
        cv2.ellipse(shadow_overlay, 
                   (random.randint(0, width), random.randint(0, height//2)), 
                   (random.randint(50, 150), random.randint(20, 60)), 
                   random.randint(0, 180), 0, 180, (0, 0, 0), -1)
        image = cv2.addWeighted(image, 0.8, shadow_overlay, 0.2, 0)
    
    # Add slight blur to simulate camera motion
    if random.random() > 0.8:
        image = cv2.GaussianBlur(image, (3, 3), 0)
    
    return image

def create_sample_dataset(output_dir='sample_drone_images', num_images=20):
    """Create a sample dataset of drone road images"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # GPS coordinates for a sample area (around New York City)
    base_lat = 40.7128
    base_lon = -74.0060
    
    print(f"Creating {num_images} sample drone road images...")
    
    damage_types = ['pothole', 'crack', 'alligator']
    
    for i in range(num_images):
        # Randomly decide if this image has damage (30% chance)
        has_damage = random.random() < 0.3
        damage_type = random.choice(damage_types) if has_damage else None
        
        # Create the image
        image = create_sample_road_image(has_damage=has_damage, damage_type=damage_type)
        
        # Generate GPS coordinates (simulate drone flight path)
        lat = base_lat + (i * 0.001) + random.uniform(-0.0005, 0.0005)
        lon = base_lon + (i * 0.001) + random.uniform(-0.0005, 0.0005)
        
        # Generate timestamp (simulate images taken over time)
        timestamp = datetime.now() - timedelta(days=random.randint(0, 30), 
                                             hours=random.randint(0, 23),
                                             minutes=random.randint(0, 59))
        
        # Create filename with GPS and timestamp info
        filename = f"drone_img_{i+1:03d}_lat{lat:.6f}_lon{lon:.6f}_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = os.path.join(output_dir, filename)
        
        # Save image
        cv2.imwrite(filepath, image)
        
        status = "DAMAGED" if has_damage else "CLEAN"
        damage_info = f" ({damage_type})" if has_damage else ""
        print(f"  {i+1:2d}. {filename} - {status}{damage_info}")
    
    print(f"\n✅ Created {num_images} sample images in '{output_dir}' directory")
    print(f"📍 GPS coordinates range: {base_lat:.4f} to {base_lat + num_images*0.001:.4f}, {base_lon:.4f} to {base_lon + num_images*0.001:.4f}")
    print(f"🚁 Ready for batch processing!")
    
    return output_dir

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Create sample drone road images for testing')
    parser.add_argument('--count', '-c', type=int, default=20, help='Number of images to create')
    parser.add_argument('--output', '-o', default='sample_drone_images', help='Output directory')
    
    args = parser.parse_args()
    
    create_sample_dataset(args.output, args.count)