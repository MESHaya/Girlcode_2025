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
        
        # DEBUG: Print model labels to verify order
        print(f"🔍 Model config labels: {self.model.config.id2label}")
        print(f"🔍 Raw probabilities: {probs}")
        
        # Check the actual label mapping
        # The model should tell us which index is fake vs real
        if hasattr(self.model.config, 'id2label'):
            label_0 = self.model.config.id2label[0].lower()
            label_1 = self.model.config.id2label[1].lower()
            
            # Correctly assign based on actual labels
            if 'fake' in label_0:
                fake_prob = float(probs[0])
                real_prob = float(probs[1])
            else:  # 'fake' is in label_1
                fake_prob = float(probs[1])
                real_prob = float(probs[0])
        else:
            # Fallback: assume [fake, real] order
            fake_prob = float(probs[0])
            real_prob = float(probs[1])
        
        result = {
            "fake_probability": fake_prob,
            "real_probability": real_prob
        }
        
        print(f"📊 Result: Fake={fake_prob:.2%}, Real={real_prob:.2%}")
        
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
    
    def analyze_image(self, image_path: str) -> Dict:
        """
        Analyze a single image for AI generation
        Args:
            image_path: Path to image file
        Returns:
            Dictionary with detection results
        """
        try:
            print(f"🖼️ Analyzing image: {image_path}")
            
            # Load image
            img = Image.open(image_path)
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Convert to numpy array for detect_frame
            img_array = np.array(img)
            print(f"✓ Image loaded: {img_array.shape}")
            
            # Use existing detect_frame method
            result = self.detect_frame(img_array)
            
            fake_prob = result['fake_probability']
            real_prob = result['real_probability']
            
            # Determine if AI-generated (threshold: 0.5)
            is_ai = fake_prob > 0.5
            confidence = fake_prob if is_ai else real_prob
            
            detection_result = {
                "is_ai_generated": bool(is_ai),
                "confidence_score": round(confidence * 100, 2),
                "fake_probability": round(fake_prob * 100, 2),
                "real_probability": round(real_prob * 100, 2),
                "analysis_type": "single_image"
            }
            
            print(f"✓ Analysis complete: {'AI' if is_ai else 'Human'} ({confidence*100:.1f}%)")
            
            return detection_result
            
        except Exception as e:
            print(f"❌ Error analyzing image: {str(e)}")
            import traceback
            traceback.print_exc()
            raise