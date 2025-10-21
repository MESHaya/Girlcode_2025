"""
Enhanced video processing with proper preprocessing for AI detection
"""

import cv2
import os
from typing import List, Tuple
import numpy as np
from PIL import Image

class VideoProcessor:
    def __init__(self, frame_sample_rate: int = 30):
        """
        Initialize video processor
        frame_sample_rate: Extract 1 frame every N frames (e.g., 30 = 1 frame per second at 30fps)
        """
        self.frame_sample_rate = frame_sample_rate
        # Standard input size for most deepfake detection models
        self.target_size = (224, 224)  
    
    def extract_frames(self, video_path: str, max_frames: int = 10) -> List[np.ndarray]:
        """
        Extract and preprocess frames from video for analysis
        Returns: List of preprocessed frames as numpy arrays
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        cap = cv2.VideoCapture(video_path)
        frames = []
        frame_count = 0
        extracted_count = 0
        
        # Get total frames for better sampling
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate frame indices to extract (evenly distributed)
        frame_indices = self._calculate_frame_indices(total_frames, max_frames)
        
        try:
            while cap.isOpened() and extracted_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Only process frames at calculated indices
                if frame_count in frame_indices:
                    # Preprocess frame properly
                    processed_frame = self._preprocess_frame(frame)
                    frames.append(processed_frame)
                    extracted_count += 1
                    print(f"✓ Extracted frame {extracted_count}/{max_frames}")
                
                frame_count += 1
        
        finally:
            cap.release()
        
        if len(frames) == 0:
            raise ValueError("No frames could be extracted from video")
        
        print(f"✅ Extracted {len(frames)} frames for analysis")
        return frames
    
    def _calculate_frame_indices(self, total_frames: int, max_frames: int) -> set:
        """
        Calculate which frame indices to extract (evenly distributed)
        This ensures we sample from beginning, middle, and end of video
        """
        if total_frames <= max_frames:
            return set(range(total_frames))
        
        # Evenly distribute frame extraction
        step = total_frames // max_frames
        indices = set()
        
        for i in range(max_frames):
            frame_idx = i * step
            indices.add(frame_idx)
        
        return indices
    
    def _preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Preprocess frame for AI detection model
        Steps:
        1. Convert BGR to RGB
        2. Resize to target size
        3. Normalize pixel values
        4. Detect and crop face (if possible)
        """
        # Convert BGR (OpenCV) to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Try to detect and crop face first
        face_frame = self._detect_and_crop_face(frame_rgb)
        
        if face_frame is not None:
            frame_rgb = face_frame
            print("  → Face detected and cropped")
        
        # Resize to target size (224x224 for most models)
        resized = cv2.resize(frame_rgb, self.target_size, interpolation=cv2.INTER_CUBIC)
        
        # Normalize pixel values to [0, 1]
        normalized = resized.astype(np.float32) / 255.0
        
        return normalized
    
    def _detect_and_crop_face(self, frame: np.ndarray) -> np.ndarray:
        """
        Detect face in frame and crop to focus on face region
        This improves detection accuracy for deepfakes
        """
        try:
            # Load Haar Cascade for face detection
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            if len(faces) > 0:
                # Get largest face
                largest_face = max(faces, key=lambda f: f[2] * f[3])
                x, y, w, h = largest_face
                
                # Add margin around face (20% on each side)
                margin = int(0.2 * max(w, h))
                x1 = max(0, x - margin)
                y1 = max(0, y - margin)
                x2 = min(frame.shape[1], x + w + margin)
                y2 = min(frame.shape[0], y + h + margin)
                
                # Crop face region
                face_crop = frame[y1:y2, x1:x2]
                
                if face_crop.size > 0:
                    return face_crop
            
        except Exception as e:
            print(f"  ⚠ Face detection failed: {e}")
        
        return None
    
    def get_video_info(self, video_path: str) -> dict:
        """Get detailed video information"""
        cap = cv2.VideoCapture(video_path)
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        info = {
            "fps": fps,
            "frame_count": frame_count,
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "duration": frame_count / fps if fps > 0 else 0,
            "codec": int(cap.get(cv2.CAP_PROP_FOURCC))
        }
        
        cap.release()
        
        print(f"📹 Video Info: {info['width']}x{info['height']} @ {info['fps']:.1f}fps, "
              f"{info['duration']:.1f}s ({frame_count} frames)")
        
        return info
    
    def extract_keyframes(self, video_path: str, max_frames: int = 10) -> List[np.ndarray]:
        """
        Extract keyframes based on scene changes (more intelligent sampling)
        """
        cap = cv2.VideoCapture(video_path)
        frames = []
        prev_frame = None
        frame_count = 0
        threshold = 30.0  # Scene change threshold
        
        try:
            while cap.isOpened() and len(frames) < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert to grayscale for comparison
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Check if this is a keyframe (scene change)
                if prev_frame is None or self._is_scene_change(prev_frame, gray, threshold):
                    processed_frame = self._preprocess_frame(frame)
                    frames.append(processed_frame)
                    print(f"✓ Keyframe detected at frame {frame_count}")
                
                prev_frame = gray
                frame_count += 1
        
        finally:
            cap.release()
        
        # If we didn't get enough keyframes, fall back to regular extraction
        if len(frames) < max_frames:
            print(f"⚠ Only {len(frames)} keyframes found, extracting additional frames...")
            return self.extract_frames(video_path, max_frames)
        
        return frames
    
    def _is_scene_change(self, frame1: np.ndarray, frame2: np.ndarray, threshold: float) -> bool:
        """Detect scene changes using frame difference"""
        # Calculate mean absolute difference
        diff = cv2.absdiff(frame1, frame2)
        mean_diff = np.mean(diff)
        return mean_diff > threshold