from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from pathlib import Path
import time

from models.detector import DeepfakeDetector
from utils.video_processor import VideoProcessor
import config
from utils.audio_processor import AudioExtractor

# Initialize FastAPI app
app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    description="Backend API for detecting AI-generated video content"
)

# Add CORS middleware (allows frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components (load once at startup)
detector = None
video_processor = None

@app.on_event("startup")
async def startup_event():
    """Initialize models when server starts"""
    global detector, video_processor, audio_extractor
    print("Starting up API server...")
    detector = DeepfakeDetector()
    video_processor = VideoProcessor(frame_sample_rate=config.FRAME_SAMPLE_RATE)
    audio_extractor = AudioExtractor(output_dir=str(config.UPLOAD_FOLDER / "audio"))  
    print("API ready!")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "AI Video Detection API is running",
        "version": config.API_VERSION
    }

@app.post("/api/detect")
async def detect_video(file: UploadFile = File(...)):
    """
    Main endpoint: Upload video and get AI detection results
    """
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in config.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(config.ALLOWED_EXTENSIONS)}"
            )
        
        # Save uploaded file temporarily
        timestamp = int(time.time())
        temp_filename = f"video_{timestamp}{file_ext}"
        temp_path = config.UPLOAD_FOLDER / temp_filename
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"Processing video: {temp_filename}")
        
        # Get video info
        video_info = video_processor.get_video_info(str(temp_path))
        print(f"Video info: {video_info}")
        
        # Extract frames
        frames = video_processor.extract_frames(
            str(temp_path),
            max_frames=config.MAX_FRAMES_TO_ANALYZE
        )
        
        # Analyze frames with AI model
        detection_result = detector.analyze_video(frames)
        
        # Clean up temp file
        os.remove(temp_path)
        
        # Prepare response
        response = {
            "success": True,
            "video_info": {
                "filename": file.filename,
                "duration_seconds": round(video_info["duration"], 2),
                "fps": round(video_info["fps"], 2),
                "resolution": f"{video_info['width']}x{video_info['height']}"
            },
            "detection_result": {
                "is_ai_generated": detection_result["is_ai_generated"],
                "confidence_score": detection_result["confidence_score"],
                "frames_analyzed": detection_result["frames_analyzed"]
            },
            "detailed_analysis": {
                "avg_fake_probability": detection_result["avg_fake_probability"],
                "avg_real_probability": detection_result["avg_real_probability"]
            }
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Check if all components are loaded"""
    return {
        "status": "healthy",
        "model_loaded": detector is not None,
        "processor_loaded": video_processor is not None
    }

@app.post("/api/extract-audio")
async def extract_audio(file: UploadFile = File(...)):
    """
    Extract audio from video file
    Returns: Audio file information and download path
    """
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in config.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(config.ALLOWED_EXTENSIONS)}"
            )
        
        # Save uploaded file temporarily
        timestamp = int(time.time())
        temp_filename = f"video_{timestamp}{file_ext}"
        temp_path = config.UPLOAD_FOLDER / temp_filename
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"Extracting audio from: {temp_filename}")
        
        # Check if video has audio first
        has_audio = audio_extractor.check_has_audio(str(temp_path))
        
        if not has_audio:
            os.remove(temp_path)
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "message": "Video file does not contain an audio track",
                    "has_audio": False,
                    "filename": file.filename
                }
            )
        
        # Extract audio
        result = audio_extractor.extract_audio(str(temp_path))
        
        if not result['success']:
            os.remove(temp_path)
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "message": result['message'],
                    "has_audio": False,
                    "filename": file.filename
                }
            )
        
        # Get audio info
        audio_info = audio_extractor.get_audio_info(result['audio_path'])
        
        # Clean up video file (keep audio)
        os.remove(temp_path)
        
        response = {
            "success": True,
            "message": "Audio extracted successfully",
            "has_audio": True,
            "audio_info": audio_info,
            "audio_filename": Path(result['audio_path']).name,
            "original_filename": file.filename
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        # Clean up temp files
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/detect-with-audio")
async def detect_video_with_audio(file: UploadFile = File(...)):
    """
    Enhanced endpoint: Detect AI-generated video AND extract audio (if present)
    """
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in config.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(config.ALLOWED_EXTENSIONS)}"
            )
        
        # Save uploaded file temporarily
        timestamp = int(time.time())
        temp_filename = f"video_{timestamp}{file_ext}"
        temp_path = config.UPLOAD_FOLDER / temp_filename
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"Processing video with audio extraction: {temp_filename}")
        
        # 1. Get video info
        video_info = video_processor.get_video_info(str(temp_path))
        
        # 2. Extract and analyze frames (video detection)
        frames = video_processor.extract_frames(
            str(temp_path),
            max_frames=config.MAX_FRAMES_TO_ANALYZE
        )
        detection_result = detector.analyze_video(frames)
        
        # 3. Try to extract audio (may not exist)
        has_audio = audio_extractor.check_has_audio(str(temp_path))
        audio_result = None
        audio_info_dict = {}
        
        if has_audio:
            try:
                audio_result = audio_extractor.extract_audio(str(temp_path))
                if audio_result['success']:
                    audio_info_dict = audio_extractor.get_audio_info(audio_result['audio_path'])
            except Exception as audio_error:
                print(f"⚠️ Audio extraction failed: {audio_error}")
                has_audio = False
        
        # Clean up temp video file
        os.remove(temp_path)
        
        # Prepare comprehensive response
        response = {
            "success": True,
            "video_info": {
                "filename": file.filename,
                "duration_seconds": round(video_info["duration"], 2),
                "fps": round(video_info["fps"], 2),
                "resolution": f"{video_info['width']}x{video_info['height']}"
            },
            "detection_result": {
                "is_ai_generated": detection_result["is_ai_generated"],
                "confidence_score": detection_result["confidence_score"],
                "frames_analyzed": detection_result["frames_analyzed"]
            },
            "audio_info": {
                "has_audio": has_audio,
                "extracted": audio_result['success'] if audio_result else False,
                "message": audio_result['message'] if audio_result else "No audio track in video"
            },
            "detailed_analysis": {
                "avg_fake_probability": detection_result["avg_fake_probability"],
                "avg_real_probability": detection_result["avg_real_probability"]
            }
        }
        
        # Add audio details if extraction was successful
        if has_audio and audio_result and audio_result['success']:
            response["audio_info"].update({
                "filename": Path(audio_result['audio_path']).name,
                "duration_seconds": round(audio_info_dict.get("duration", 0), 2),
                "sample_rate": audio_info_dict.get("sample_rate", 0),
                "size_mb": round(audio_info_dict.get("size_mb", 0), 2)
            })
        
        return JSONResponse(content=response)
    
    except Exception as e:
        # Clean up temp files
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))