# this file is for video processing utilities

import cv2
import os
from typing import List
import numpy as np
from PIL import Image

class VideoProcessor:
    def __init__(self, frame_sample_rate: int = 30):
        """
        Initialize video processor
        frame_sample_rate: Extract 1 frame every N frames (e.g., 30 = 1 frame per second at 30fps)
        """
        self.frame_sample_rate = frame_sample_rate
    
    def extract_frames(self, video_path: str, max_frames: int = 10) -> List[np.ndarray]:
        """
        Extract frames from video for analysis
        Returns: List of frames as numpy arrays
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        cap = cv2.VideoCapture(video_path)
        frames = []
        frame_count = 0
        extracted_count = 0
        
        try:
            while cap.isOpened() and extracted_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Sample frames at specified rate
                if frame_count % self.frame_sample_rate == 0:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(frame_rgb)
                    extracted_count += 1
                
                frame_count += 1
        
        finally:
            cap.release()
        
        if len(frames) == 0:
            raise ValueError("No frames could be extracted from video")
        
        return frames
    
    def get_video_info(self, video_path: str) -> dict:
        """Get basic video information"""
        cap = cv2.VideoCapture(video_path)
        
        info = {
            "fps": cap.get(cv2.CAP_PROP_FPS),
            "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "duration": 0
        }
        
        if info["fps"] > 0:
            info["duration"] = info["frame_count"] / info["fps"]
        
        cap.release()
        return info