# utils/image_processor.py
import os
from PIL import Image
import numpy as np

class ImageProcessor:
    def __init__(self):
        """Initialize image processor"""
        pass
    
    def load_image(self, image_path: str) -> np.ndarray:
        """
        Load and preprocess image for analysis
        Returns: Image as numpy array
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        try:
            # Open image with PIL
            img = Image.open(image_path)
            
            # Convert to RGB if needed (handles RGBA, grayscale, etc.)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Convert to numpy array
            img_array = np.array(img)
            
            return img_array
            
        except Exception as e:
            raise ValueError(f"Failed to load image: {str(e)}")
    
    def get_image_info(self, image_path: str) -> dict:
        """Get basic image information"""
        with Image.open(image_path) as img:
            info = {
                "width": img.size[0],
                "height": img.size[1],
                "format": img.format,
                "mode": img.mode,
                "size_mb": os.path.getsize(image_path) / (1024 * 1024)
            }
        
        return info
    
    def resize_for_model(self, image: np.ndarray, target_size: tuple = (224, 224)) -> np.ndarray:
        """
        Resize image to model input size
        Args:
            image: numpy array
            target_size: (width, height) tuple
        """
        img_pil = Image.fromarray(image)
        img_resized = img_pil.resize(target_size, Image.LANCZOS)
        return np.array(img_resized)