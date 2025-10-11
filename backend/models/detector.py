# this file is for detector model
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import numpy as np
from typing import List, Dict

class DeepfakeDetector:
    def __init__(self, model_name: str = "dima806/deepfake_vs_real_image_detection"):
        """
        Initialize the deepfake detection model
        Using a pre-trained model from HuggingFace
        """
        print("Loading AI detection model...")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        # Load processor and model
        self.processor = AutoImageProcessor.from_pretrained(model_name)
        self.model = AutoModelForImageClassification.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
        
        print("Model loaded successfully!")
    
    def detect_frame(self, frame: np.ndarray) -> Dict[str, float]:
        """
        Detect if a single frame is AI-generated
        Returns: Dictionary with 'real' and 'fake' probabilities
        """
        # Convert numpy array to PIL Image
        if isinstance(frame, np.ndarray):
            frame = Image.fromarray(frame)
        
        # Preprocess image
        inputs = self.processor(images=frame, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Run inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # Get probabilities
        probs = probabilities[0].cpu().numpy()
        
        # Assuming model outputs [fake, real] probabilities
        result = {
            "fake_probability": float(probs[0]),
            "real_probability": float(probs[1])
        }
        
        return result
    
    def analyze_video(self, frames: List[np.ndarray]) -> Dict:
        """
        Analyze multiple frames and aggregate results
        Returns: Overall detection result with confidence score
        """
        if not frames:
            raise ValueError("No frames provided for analysis")
        
        results = []
        
        print(f"Analyzing {len(frames)} frames...")
        
        for i, frame in enumerate(frames):
            result = self.detect_frame(frame)
            results.append(result)
            print(f"Frame {i+1}/{len(frames)}: Fake={result['fake_probability']:.2%}")
        
        # Aggregate results
        avg_fake_prob = np.mean([r['fake_probability'] for r in results])
        avg_real_prob = np.mean([r['real_probability'] for r in results])
        
        # Determine final classification
        is_ai_generated = avg_fake_prob > 0.5
        confidence_score = max(avg_fake_prob, avg_real_prob) * 100
        
        return {
            "is_ai_generated": bool(is_ai_generated),
            "confidence_score": round(confidence_score, 2),
            "avg_fake_probability": round(avg_fake_prob, 4),
            "avg_real_probability": round(avg_real_prob, 4),
            "frames_analyzed": len(frames),
            "frame_results": results
        }