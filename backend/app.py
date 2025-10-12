from fastapi import FastAPI, File, UploadFile, HTTPException,Query
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
from utils.url_handler import URLHandler
from utils.document_processor import DocumentProcessor
from models.text_detector import TextAIDetector
from pydantic import BaseModel
from utils.language_handler import LanguageHandler
from utils.multilingual_helper import MultilingualHelper
from utils.auto_translator import AutoTranslator
from utils.image_processor import ImageProcessor



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

url_handler = None
document_processor = None
text_detector = None

class URLRequest(BaseModel):
    url: str

@app.on_event("startup")
async def startup_event():
    """Initialize models when server starts"""
    global detector, video_processor, audio_extractor, url_handler, document_processor, text_detector, language_handler, multilingual_helper,image_processor
    
    print("Starting up API server...")
    
    # Load models
    detector = DeepfakeDetector()
    video_processor = VideoProcessor(frame_sample_rate=config.FRAME_SAMPLE_RATE)
    audio_extractor = AudioExtractor(output_dir=str(config.UPLOAD_FOLDER / "audio"))
    url_handler = URLHandler(download_dir=str(config.UPLOAD_FOLDER / "downloads"))
    document_processor = DocumentProcessor()
    text_detector = TextAIDetector()
    language_handler = LanguageHandler()
    multilingual_helper = MultilingualHelper()
    image_processor = ImageProcessor() 

    # Pre-generate translations for South African languages (optional but recommended)
    # This happens in the background and caches translations
    print("\n Preparing multilingual support...")
    try:
        # Only pre-generate for SA languages to save time
        sa_languages = ['zu', 'xh', 'st', 'af', 'nso', 'tn']
        multilingual_helper.pre_generate_translations(sa_languages)
    except Exception as e:
        print(f" Could not pre-generate translations: {e}")
        print("Translations will be generated on-demand")
    
    print("\n API ready with multilingual support!")

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
from fastapi import FastAPI, File, UploadFile, HTTPException, Query

@app.post("/api/detect-with-audio")
async def detect_video_with_audio(
    file: UploadFile = File(...), 
    language: str = Query(default='en')
):
    """Enhanced endpoint: Detect AI-generated video with multilingual support"""
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
        
        print(f"Processing video: {temp_filename} (Language: {language})")
        
        # Get video info
        video_info = video_processor.get_video_info(str(temp_path))
        
        # Extract and analyze frames
        frames = video_processor.extract_frames(
            str(temp_path),
            max_frames=config.MAX_FRAMES_TO_ANALYZE
        )
        detection_result = detector.analyze_video(frames)
        
        # Try to extract audio
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
        
        # Format with multilingual support
        formatted_result = multilingual_helper.format_full_response(
            detection_result,
            language=language,
            include_warnings=True
        )
        
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
                "is_ai_generated": formatted_result["is_ai_generated"],
                "confidence_score": formatted_result["confidence_score"],
                "message": formatted_result["message"],
                "confidence_label": formatted_result["confidence_label"],
                "warning": formatted_result.get("warning", ""),
                "language": formatted_result["language"],
                "language_name": formatted_result["language_name"],
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
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/detect-image")
async def detect_image(
    file: UploadFile = File(...), 
    language: str = Query(default='en')
):
    """Detect if an uploaded image is AI-generated with multilingual support"""
    try:
        file_ext = Path(file.filename).suffix.lower()
        allowed_image_formats = ['.jpg', '.jpeg', '.png', '.webp', '.bmp']
        
        if file_ext not in allowed_image_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_image_formats)}"
            )
        
        timestamp = int(time.time())
        temp_filename = f"image_{timestamp}{file_ext}"
        temp_path = config.UPLOAD_FOLDER / temp_filename
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"Processing image: {temp_filename} (Language: {language})")
        
        # Analyze image
        detection_result = detector.analyze_image(str(temp_path))
        
        # Get image info
        from PIL import Image
        with Image.open(temp_path) as img:
            width, height = img.size
            format_name = img.format
            file_size_mb = os.path.getsize(temp_path) / (1024 * 1024)
        
        os.remove(temp_path)
        
        # Format with multilingual support
        formatted_result = multilingual_helper.format_full_response(
            detection_result,
            language=language,
            include_warnings=True
        )
        
        response = {
            "success": True,
            "image_info": {
                "filename": file.filename,
                "resolution": f"{width}x{height}",
                "format": format_name,
                "size_mb": round(file_size_mb, 2)
            },
            "detection_result": {
                "is_ai_generated": formatted_result["is_ai_generated"],
                "confidence_score": formatted_result["confidence_score"],
                "message": formatted_result["message"],
                "confidence_label": formatted_result["confidence_label"],
                "warning": formatted_result.get("warning", ""),
                "language": formatted_result["language"],
                "language_name": formatted_result["language_name"],
                "analysis_type": detection_result["analysis_type"]
            },
            "detailed_analysis": {
                "fake_probability": detection_result["fake_probability"],
                "real_probability": detection_result["real_probability"]
            }
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/detect-document")
async def detect_document(
    file: UploadFile = File(...), 
    language: str = Query(default='en')
):
    """Detect AI-generated text from uploaded document with multilingual support"""
    try:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ['.pdf', '.docx', '.doc', '.txt']:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: .pdf, .docx, .txt"
            )
        
        timestamp = int(time.time())
        temp_filename = f"document_{timestamp}{file_ext}"
        temp_path = config.UPLOAD_FOLDER / temp_filename
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"Processing document: {temp_filename} (Language: {language})")
        
        # Extract text
        extraction_result = document_processor.extract_text(str(temp_path))
        
        if not extraction_result['success']:
            os.remove(temp_path)
            raise HTTPException(
                status_code=400,
                detail=extraction_result.get('message', 'Failed to extract text')
            )
        
        # Chunk text for analysis
        text_chunks = document_processor.chunk_text(extraction_result['text'])
        
        # Analyze with AI detector
        detection_result = text_detector.analyze_document(text_chunks)
        
        os.remove(temp_path)
        
        # Format with multilingual support
        formatted_result = multilingual_helper.format_full_response(
            detection_result,
            language=language,
            include_warnings=True
        )
        
        response = {
            "success": True,
            "document_info": {
                "filename": file.filename,
                "file_type": file_ext,
                "word_count": extraction_result['word_count'],
                "character_count": extraction_result['character_count'],
                "sentence_count": extraction_result['sentence_count']
            },
            "detection_result": {
                "is_ai_generated": formatted_result["is_ai_generated"],
                "confidence_score": formatted_result["confidence_score"],
                "message": formatted_result["message"],
                "confidence_label": formatted_result["confidence_label"],
                "warning": formatted_result.get("warning", ""),
                "language": formatted_result["language"],
                "language_name": formatted_result["language_name"],
                "chunks_analyzed": detection_result["chunks_analyzed"]
            },
            "detailed_analysis": {
                "avg_ai_probability": detection_result["avg_ai_probability"],
                "avg_human_probability": detection_result["avg_human_probability"]
            }
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/detect-video-url")
async def detect_video_from_url(request: URLRequest):
    """
    Detect AI-generated content from video URL
    Supports: YouTube, TikTok, Instagram, direct video links, etc.
    """
    temp_path = None
    
    try:
        url = request.url
        print(f"📥 Processing video from URL: {url}")
        
        # Download video from URL
        download_result = url_handler.download_from_url(url)
        
        if not download_result['success']:
            raise HTTPException(
                status_code=400,
                detail=download_result.get('message', 'Failed to download video')
            )
        
        temp_path = download_result['filepath']
        
        # Get video info
        video_info = video_processor.get_video_info(temp_path)
        
        # Extract and analyze frames
        frames = video_processor.extract_frames(
            temp_path,
            max_frames=config.MAX_FRAMES_TO_ANALYZE
        )
        detection_result = detector.analyze_video(frames)
        
        # Try to extract audio
        has_audio = audio_extractor.check_has_audio(temp_path)
        audio_result = None
        audio_info_dict = {}
        
        if has_audio:
            try:
                audio_result = audio_extractor.extract_audio(temp_path)
                if audio_result['success']:
                    audio_info_dict = audio_extractor.get_audio_info(audio_result['audio_path'])
            except Exception as audio_error:
                print(f"⚠️ Audio extraction failed: {audio_error}")
                has_audio = False
        
        # Clean up downloaded video
        url_handler.cleanup(temp_path)
        
        # Prepare response
        response = {
            "success": True,
            "source": "url",
            "url": url,
            "download_info": {
                "platform": download_result.get('platform', 'Unknown'),
                "title": download_result.get('title', 'Unknown'),
                "size_mb": download_result.get('size_mb', 0)
            },
            "video_info": {
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
                "extracted": audio_result['success'] if audio_result else False
            }
        }
        
        if has_audio and audio_result and audio_result['success']:
            response["audio_info"].update({
                "duration_seconds": round(audio_info_dict.get("duration", 0), 2),
                "sample_rate": audio_info_dict.get("sample_rate", 0)
            })
        
        return JSONResponse(content=response)
    
    except Exception as e:
        if temp_path and os.path.exists(temp_path):
            url_handler.cleanup(temp_path)
        
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/detect-document-url")
async def detect_document_from_url(request: URLRequest):
    """
    Detect AI-generated text from document URL
    Supports: PDF, DOCX, TXT files
    """
    temp_path = None
    
    try:
        url = request.url
        print(f"📥 Processing document from URL: {url}")
        
        # Download document from URL
        download_result = url_handler.download_from_url(url)
        
        if not download_result['success']:
            raise HTTPException(
                status_code=400,
                detail=download_result.get('message', 'Failed to download document')
            )
        
        temp_path = download_result['filepath']
        
        # Extract text from document
        extraction_result = document_processor.extract_text(temp_path)
        
        if not extraction_result['success']:
            raise HTTPException(
                status_code=400,
                detail=extraction_result.get('message', 'Failed to extract text')
            )
        
        # Chunk text for analysis
        text_chunks = document_processor.chunk_text(extraction_result['text'])
        
        # Analyze with AI detector
        detection_result = text_detector.analyze_document(text_chunks)
        
        # Clean up downloaded file
        url_handler.cleanup(temp_path)
        
        # Prepare response
        response = {
            "success": True,
            "source": "url",
            "url": url,
            "document_info": {
                "filename": extraction_result['filename'],
                "file_type": extraction_result['file_type'],
                "word_count": extraction_result['word_count'],
                "character_count": extraction_result['character_count'],
                "sentence_count": extraction_result['sentence_count']
            },
            "detection_result": {
                "is_ai_generated": detection_result["is_ai_generated"],
                "confidence_score": detection_result["confidence_score"],
                "chunks_analyzed": detection_result["chunks_analyzed"]
            },
            "detailed_analysis": {
                "avg_ai_probability": detection_result["avg_ai_probability"],
                "avg_human_probability": detection_result["avg_human_probability"]
            }
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        if temp_path and os.path.exists(temp_path):
            url_handler.cleanup(temp_path)
        
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/detect-document")
async def detect_document(file: UploadFile = File(...)):
    """
    Detect AI-generated text from uploaded document
    Supports: PDF, DOCX, TXT files
    """
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ['.pdf', '.docx', '.doc', '.txt']:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: .pdf, .docx, .txt"
            )
        
        # Save uploaded file temporarily
        timestamp = int(time.time())
        temp_filename = f"document_{timestamp}{file_ext}"
        temp_path = config.UPLOAD_FOLDER / temp_filename
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"Processing document: {temp_filename}")
        
        # Extract text
        extraction_result = document_processor.extract_text(str(temp_path))
        
        if not extraction_result['success']:
            os.remove(temp_path)
            raise HTTPException(
                status_code=400,
                detail=extraction_result.get('message', 'Failed to extract text')
            )
        
        # Chunk text for analysis
        text_chunks = document_processor.chunk_text(extraction_result['text'])
        
        # Analyze with AI detector
        detection_result = text_detector.analyze_document(text_chunks)
        
        # Clean up temp file
        os.remove(temp_path)
        
        # Prepare response
        response = {
            "success": True,
            "document_info": {
                "filename": file.filename,
                "file_type": file_ext,
                "word_count": extraction_result['word_count'],
                "character_count": extraction_result['character_count'],
                "sentence_count": extraction_result['sentence_count']
            },
            "detection_result": {
                "is_ai_generated": detection_result["is_ai_generated"],
                "confidence_score": detection_result["confidence_score"],
                "chunks_analyzed": detection_result["chunks_analyzed"]
            },
            "detailed_analysis": {
                "avg_ai_probability": detection_result["avg_ai_probability"],
                "avg_human_probability": detection_result["avg_human_probability"]
            }
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    # Add these endpoints to your app.py file (after the existing endpoints)
# ============================================
# LANGUAGE & TRANSLATION ENDPOINTS
# ============================================

@app.get("/api/languages")
async def get_supported_languages():
    """Get list of all supported languages"""
    try:
        languages = multilingual_helper.get_supported_languages()
        return JSONResponse(content={
            "success": True,
            "languages": languages,
            "total": len(languages)
        })
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/translations/{language}")
async def get_translations(language: str):
    """Get all UI translations for a specific language"""
    try:
        if not multilingual_helper.validate_language_code(language):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language: {language}"
            )
        
        translations = multilingual_helper.get_all_translations(language)
        
        return JSONResponse(content={
            "success": True,
            "language": language,
            "translations": translations
        })
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Update the video detection endpoint to support language parameter
@app.post("/api/detect-with-audio")
async def detect_video_with_audio(file: UploadFile = File(...), language: str = 'en'):
    """Enhanced endpoint: Detect AI-generated video with multilingual support"""
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
        
        print(f"Processing video: {temp_filename} (Language: {language})")
        
        # Get video info
        video_info = video_processor.get_video_info(str(temp_path))
        
        # Extract and analyze frames
        frames = video_processor.extract_frames(
            str(temp_path),
            max_frames=config.MAX_FRAMES_TO_ANALYZE
        )
        detection_result = detector.analyze_video(frames)
        
        # Try to extract audio
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
        
        # Format with multilingual support
        formatted_result = multilingual_helper.format_full_response(
            detection_result,
            language=language,
            include_warnings=True
        )
        
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
                "is_ai_generated": formatted_result["is_ai_generated"],
                "confidence_score": formatted_result["confidence_score"],
                "message": formatted_result["message"],
                "confidence_label": formatted_result["confidence_label"],
                "warning": formatted_result.get("warning", ""),
                "language": formatted_result["language"],
                "language_name": formatted_result["language_name"],
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
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Add similar updates for image and document endpoints
@app.post("/api/detect-image")
async def detect_image(file: UploadFile = File(...), language: str = 'en'):
    """Detect if an uploaded image is AI-generated with multilingual support"""
    try:
        file_ext = Path(file.filename).suffix.lower()
        allowed_image_formats = ['.jpg', '.jpeg', '.png', '.webp', '.bmp']
        
        if file_ext not in allowed_image_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_image_formats)}"
            )
        
        timestamp = int(time.time())
        temp_filename = f"image_{timestamp}{file_ext}"
        temp_path = config.UPLOAD_FOLDER / temp_filename
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"Processing image: {temp_filename} (Language: {language})")
        
        # Analyze image
        detection_result = detector.analyze_image(str(temp_path))
        
        # Get image info
        from PIL import Image
        with Image.open(temp_path) as img:
            width, height = img.size
            format_name = img.format
            file_size_mb = os.path.getsize(temp_path) / (1024 * 1024)
        
        os.remove(temp_path)
        
        # Format with multilingual support
        formatted_result = multilingual_helper.format_full_response(
            detection_result,
            language=language,
            include_warnings=True
        )
        
        response = {
            "success": True,
            "image_info": {
                "filename": file.filename,
                "resolution": f"{width}x{height}",
                "format": format_name,
                "size_mb": round(file_size_mb, 2)
            },
            "detection_result": {
                "is_ai_generated": formatted_result["is_ai_generated"],
                "confidence_score": formatted_result["confidence_score"],
                "message": formatted_result["message"],
                "confidence_label": formatted_result["confidence_label"],
                "warning": formatted_result.get("warning", ""),
                "language": formatted_result["language"],
                "language_name": formatted_result["language_name"],
                "analysis_type": detection_result["analysis_type"]
            },
            "detailed_analysis": {
                "fake_probability": detection_result["fake_probability"],
                "real_probability": detection_result["real_probability"]
            }
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/detect-document")
async def detect_document(file: UploadFile = File(...), language: str = 'en'):
    """Detect AI-generated text from uploaded document with multilingual support"""
    try:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ['.pdf', '.docx', '.doc', '.txt']:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: .pdf, .docx, .txt"
            )
        
        timestamp = int(time.time())
        temp_filename = f"document_{timestamp}{file_ext}"
        temp_path = config.UPLOAD_FOLDER / temp_filename
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"Processing document: {temp_filename} (Language: {language})")
        
        # Extract text
        extraction_result = document_processor.extract_text(str(temp_path))
        
        if not extraction_result['success']:
            os.remove(temp_path)
            raise HTTPException(
                status_code=400,
                detail=extraction_result.get('message', 'Failed to extract text')
            )
        
        # Chunk text for analysis
        text_chunks = document_processor.chunk_text(extraction_result['text'])
        
        # Analyze with AI detector
        detection_result = text_detector.analyze_document(text_chunks)
        
        os.remove(temp_path)
        
        # Format with multilingual support
        formatted_result = multilingual_helper.format_full_response(
            detection_result,
            language=language,
            include_warnings=True
        )
        
        response = {
            "success": True,
            "document_info": {
                "filename": file.filename,
                "file_type": file_ext,
                "word_count": extraction_result['word_count'],
                "character_count": extraction_result['character_count'],
                "sentence_count": extraction_result['sentence_count']
            },
            "detection_result": {
                "is_ai_generated": formatted_result["is_ai_generated"],
                "confidence_score": formatted_result["confidence_score"],
                "message": formatted_result["message"],
                "confidence_label": formatted_result["confidence_label"],
                "warning": formatted_result.get("warning", ""),
                "language": formatted_result["language"],
                "language_name": formatted_result["language_name"],
                "chunks_analyzed": detection_result["chunks_analyzed"]
            },
            "detailed_analysis": {
                "avg_ai_probability": detection_result["avg_ai_probability"],
                "avg_human_probability": detection_result["avg_human_probability"]
            }
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))