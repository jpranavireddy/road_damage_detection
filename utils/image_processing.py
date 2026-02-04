"""
Image processing utilities for road damage detection
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance
import os

class ImageProcessor:
    """Utility class for image processing operations"""
    
    @staticmethod
    def resize_image(image_path, target_size=(640, 640), maintain_aspect=True):
        """
        Resize image to target size
        
        Args:
            image_path (str): Path to input image
            target_size (tuple): Target size (width, height)
            maintain_aspect (bool): Whether to maintain aspect ratio
            
        Returns:
            numpy.ndarray: Resized image
        """
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        if maintain_aspect:
            h, w = image.shape[:2]
            target_w, target_h = target_size
            
            # Calculate scaling factor
            scale = min(target_w / w, target_h / h)
            new_w, new_h = int(w * scale), int(h * scale)
            
            # Resize image
            resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
            
            # Create padded image
            padded = np.zeros((target_h, target_w, 3), dtype=np.uint8)
            y_offset = (target_h - new_h) // 2
            x_offset = (target_w - new_w) // 2
            padded[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
            
            return padded
        else:
            return cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)
    
    @staticmethod
    def enhance_image(image_path, brightness=1.0, contrast=1.0, sharpness=1.0):
        """
        Enhance image quality
        
        Args:
            image_path (str): Path to input image
            brightness (float): Brightness factor (1.0 = no change)
            contrast (float): Contrast factor (1.0 = no change)
            sharpness (float): Sharpness factor (1.0 = no change)
            
        Returns:
            PIL.Image: Enhanced image
        """
        image = Image.open(image_path)
        
        # Apply enhancements
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(brightness)
        
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast)
        
        if sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(sharpness)
        
        return image
    
    @staticmethod
    def preprocess_for_detection(image_path, target_size=(640, 640)):
        """
        Preprocess image for damage detection
        
        Args:
            image_path (str): Path to input image
            target_size (tuple): Target size for detection model
            
        Returns:
            numpy.ndarray: Preprocessed image
        """
        # Load and resize image
        image = ImageProcessor.resize_image(image_path, target_size)
        
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Normalize pixel values
        image_normalized = image_rgb.astype(np.float32) / 255.0
        
        return image_normalized
    
    @staticmethod
    def apply_clahe(image_path, clip_limit=2.0, tile_grid_size=(8, 8)):
        """
        Apply Contrast Limited Adaptive Histogram Equalization (CLAHE)
        
        Args:
            image_path (str): Path to input image
            clip_limit (float): Clipping limit for contrast enhancement
            tile_grid_size (tuple): Size of the grid for histogram equalization
            
        Returns:
            numpy.ndarray: Enhanced image
        """
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        
        # Convert back to BGR
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        return enhanced
    
    @staticmethod
    def detect_edges(image_path, low_threshold=50, high_threshold=150):
        """
        Detect edges in image using Canny edge detection
        
        Args:
            image_path (str): Path to input image
            low_threshold (int): Lower threshold for edge detection
            high_threshold (int): Upper threshold for edge detection
            
        Returns:
            numpy.ndarray: Edge map
        """
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        
        # Apply Canny edge detection
        edges = cv2.Canny(blurred, low_threshold, high_threshold)
        
        return edges
    
    @staticmethod
    def save_processed_image(image, output_path):
        """
        Save processed image to file
        
        Args:
            image (numpy.ndarray or PIL.Image): Image to save
            output_path (str): Output file path
        """
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        if isinstance(image, np.ndarray):
            cv2.imwrite(output_path, image)
        else:
            image.save(output_path)
    
    @staticmethod
    def get_image_info(image_path):
        """
        Get basic information about an image
        
        Args:
            image_path (str): Path to image
            
        Returns:
            dict: Image information
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            height, width, channels = image.shape
            file_size = os.path.getsize(image_path)
            
            return {
                'width': width,
                'height': height,
                'channels': channels,
                'file_size': file_size,
                'format': os.path.splitext(image_path)[1].lower()
            }
        except Exception as e:
            print(f"Error getting image info: {e}")
            return None
    
    @staticmethod
    def create_thumbnail(image_path, output_path, size=(150, 150)):
        """
        Create thumbnail of image
        
        Args:
            image_path (str): Path to input image
            output_path (str): Path for thumbnail
            size (tuple): Thumbnail size
        """
        try:
            image = Image.open(image_path)
            image.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Create output directory if needed
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            image.save(output_path, optimize=True, quality=85)
            return True
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            return False