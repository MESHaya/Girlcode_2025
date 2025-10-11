import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Upload settings
UPLOAD_FOLDER = BASE_DIR.parent / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}

# Model settings
FRAME_SAMPLE_RATE = 30  # Extract 1 frame every 30 frames
MAX_FRAMES_TO_ANALYZE = 10  # Analyze max 10 frames per video

# API settings
API_TITLE = "AI Video Detection API"
API_VERSION = "1.0.0"