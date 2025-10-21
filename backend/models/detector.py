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
        print("🔄 Loading AI detection model...")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"✓ Using device: {self.device}")
        
        # Load processor and model
        self.processor = AutoImageProcessor.from_pretrained(model_name)
        self.model = AutoModelForImageClassification.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
        
        # Verify and store label mapping
        self.label_map = self._verify_labels()
        
        # Detection threshold (can be adjusted)
        self.threshold = 0.5  # 50% - balanced threshold
        
        print("✅ Model loaded successfully!")
        print(f"📋 Label mapping: {self.label_map}")
    
    def _verify_labels(self) -> Dict[str, int]:
        """
        Verify the model's label mapping and return correct indices
        Returns: dict with 'fake_idx' and 'real_idx'
        """
        if hasattr(self.model.config, 'id2label'):
            labels = self.model.config.id2label
            print(f"🏷️ Model labels: {labels}")
            
            # Find which index corresponds to fake/real
            fake_idx = None
            real_idx = None
            
            for idx, label in labels.items():
                label_lower = label.lower()
                if 'fake' in label_lower or 'ai' in label_lower or 'generated' in label_lower:
                    fake_idx = idx
                elif 'real' in label_lower or 'authentic' in label_lower or 'human' in label_lower:
                    real_idx = idx
            
            # Fallback if labels are ambiguous
            if fake_idx is None or real_idx is None:
                print("⚠️ Could not determine labels, using defaults: 0=Fake, 1=Real")
                fake_idx = 0
                real_idx = 1
            
            return {
                'fake_idx': fake_idx,
                'real_idx': real_idx,
                'labels': labels
            }
        else:
            # Default mapping
            print("⚠️ No label mapping found, using default: 0=Fake, 1=Real")
            return {
                'fake_idx': 0,
                'real_idx': 1,
                'labels': {0: 'Fake', 1: 'Real'}
            }
    
    def detect_frame(self, frame: np.ndarray, verbose: bool = False) -> Dict[str, float]:
        """
        Detect if a single frame is AI-generated
        Args:
            frame: Image as numpy array or PIL Image
            verbose: Print detailed information
        Returns: Dictionary with 'fake_probability' and 'real_probability'
        """
        # Convert numpy array to PIL Image
        if isinstance(frame, np.ndarray):
            # Ensure proper format (H, W, C) and uint8
            if frame.dtype != np.uint8:
                frame = (frame * 255).astype(np.uint8)
            frame = Image.fromarray(frame)
        
        # Resize if image is too large (for speed)
        max_size = 512
        if max(frame.size) > max_size:
            frame.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Preprocess image
        inputs = self.processor(images=frame, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Run inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # Get probabilities
        probs = probabilities[0].cpu().numpy()
        
        # Extract fake and real probabilities using verified indices
        fake_idx = self.label_map['fake_idx']
        real_idx = self.label_map['real_idx']
        
        fake_prob = float(probs[fake_idx])
        real_prob = float(probs[real_idx])
        
        if verbose:
            print(f"  🔍 Raw logits: {outputs.logits[0].cpu().numpy()}")
            print(f"  📊 Probabilities: Fake={fake_prob:.2%}, Real={real_prob:.2%}")
        
        return {
            "fake_probability": fake_prob,
            "real_probability": real_prob
        }
    
    def analyze_video(self, frames: List[np.ndarray]) -> Dict:
        """
        Analyze multiple frames and aggregate results with intelligent weighting
        Returns: Overall detection result with confidence score
        """
        if not frames:
            raise ValueError("No frames provided for analysis")
        
        print(f"\n🎬 Analyzing {len(frames)} frames...")
        
        results = []
        fake_probs = []
        real_probs = []
        
        for i, frame in enumerate(frames):
            result = self.detect_frame(frame, verbose=False)
            results.append(result)
            
            fake_probs.append(result['fake_probability'])
            real_probs.append(result['real_probability'])
            
            # Show progress
            status = "🚨 FAKE" if result['fake_probability'] > self.threshold else "✅ Real"
            print(f"  Frame {i+1}/{len(frames)}: {status} (Fake: {result['fake_probability']:.1%})")
        
        # Statistical analysis
        avg_fake_prob = np.mean(fake_probs)
        max_fake_prob = np.max(fake_probs)
        median_fake_prob = np.median(fake_probs)
        std_fake_prob = np.std(fake_probs)
        
        # Count how many frames are classified as fake
        fake_frame_count = sum(1 for fp in fake_probs if fp > self.threshold)
        fake_frame_ratio = fake_frame_count / len(frames)
        
        print(f"\n📊 Statistics:")
        print(f"  • Average fake probability: {avg_fake_prob:.1%}")
        print(f"  • Maximum fake probability: {max_fake_prob:.1%}")
        print(f"  • Median fake probability: {median_fake_prob:.1%}")
        print(f"  • Frames classified as fake: {fake_frame_count}/{len(frames)} ({fake_frame_ratio:.1%})")
        
        # Decision logic with multiple criteria
        # Video is AI-generated if:
        # 1. Average fake prob > threshold, OR
        # 2. More than 30% of frames are fake, OR
        # 3. Max fake prob is very high (>0.8) and avg is above 0.4
        
        is_ai_generated = (
            avg_fake_prob > self.threshold or
            fake_frame_ratio > 0.3 or
            (max_fake_prob > 0.8 and avg_fake_prob > 0.4)
        )
        
        # Calculate confidence score
        if is_ai_generated:
            # Confidence is based on how strongly fake it appears
            confidence_score = avg_fake_prob * 0.6 + max_fake_prob * 0.4
        else:
            # Confidence is based on how strongly real it appears
            avg_real_prob = np.mean(real_probs)
            confidence_score = avg_real_prob * 0.7 + (1 - max_fake_prob) * 0.3
        
        result = {
            "is_ai_generated": bool(is_ai_generated),
            "confidence_score": round(confidence_score * 100, 2),
            "avg_fake_probability": round(avg_fake_prob, 4),
            "avg_real_probability": round(np.mean(real_probs), 4),
            "max_fake_probability": round(max_fake_prob, 4),
            "median_fake_probability": round(median_fake_prob, 4),
            "std_fake_probability": round(std_fake_prob, 4),
            "fake_frame_count": fake_frame_count,
            "fake_frame_ratio": round(fake_frame_ratio, 4),
            "frames_analyzed": len(frames),
            "frame_results": results
        }
        
        # Print final result
        verdict = "🚨 AI-GENERATED" if is_ai_generated else "✅ LIKELY HUMAN-CREATED"
        print(f"\n{verdict}")
        print(f"Confidence: {confidence_score*100:.1f}%")
        
        return result
    
    def analyze_image(self, image_path: str) -> Dict:
        """
        Analyze a single image for AI generation
        Args:
            image_path: Path to image file
        Returns:
            Dictionary with detection results
        """
        try:
            print(f"\n🖼️ Analyzing image: {image_path}")
            
            # Load image
            img = Image.open(image_path)
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            print(f"✓ Image loaded: {img.size}, mode: {img.mode}")
            
            # Convert to numpy array for detect_frame
            img_array = np.array(img)
            
            # Analyze the image
            result = self.detect_frame(img_array, verbose=True)
            
            fake_prob = result['fake_probability']
            real_prob = result['real_probability']
            
            # Determine if AI-generated
            is_ai = fake_prob > self.threshold
            confidence = fake_prob if is_ai else real_prob
            
            detection_result = {
                "is_ai_generated": bool(is_ai),
                "confidence_score": round(confidence * 100, 2),
                "fake_probability": round(fake_prob * 100, 2),
                "real_probability": round(real_prob * 100, 2),
                "analysis_type": "single_image"
            }
            
            verdict = "🚨 AI-Generated" if is_ai else "✅ Human-Created"
            print(f"\n{verdict} (Confidence: {confidence*100:.1f}%)")
            
            return detection_result
            
        except Exception as e:
            print(f"❌ Error analyzing image: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def set_threshold(self, threshold: float):
        """
        Adjust detection threshold
        Args:
            threshold: Value between 0.0 and 1.0
                      Lower = more sensitive (catches more AI)
                      Higher = more conservative (fewer false positives)
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0")
        
        self.threshold = threshold
        print(f"🎚️ Detection threshold updated to {threshold:.2f}")
        print(f"   Lower = more sensitive, Higher = more conservative")
    
    def batch_analyze(self, image_paths: List[str]) -> List[Dict]:
        """
        Analyze multiple images in batch
        Args:
            image_paths: List of image file paths
        Returns:
            List of detection results
        """
        results = []
        
        print(f"\n📦 Batch analyzing {len(image_paths)} images...")
        
        for i, path in enumerate(image_paths):
            print(f"\n[{i+1}/{len(image_paths)}]")
            try:
                result = self.analyze_image(path)
                results.append({
                    "path": path,
                    "result": result,
                    "success": True
                })
            except Exception as e:
                print(f"❌ Failed: {str(e)}")
                results.append({
                    "path": path,
                    "error": str(e),
                    "success": False
                })
        
        # Summary
        successful = sum(1 for r in results if r['success'])
        ai_count = sum(1 for r in results if r['success'] and r['result']['is_ai_generated'])
        
        print(f"\n📊 Batch Summary:")
        print(f"  • Total: {len(image_paths)}")
        print(f"  • Successful: {successful}")
        print(f"  • AI-generated: {ai_count}")
        print(f"  • Human-created: {successful - ai_count}")
        
        return results