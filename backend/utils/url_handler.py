"""
URL Handler - Download videos and documents from URLs
"""
import requests
import yt_dlp
import os
import validators
from pathlib import Path
from typing import Dict, Optional
import time

class URLHandler:
    def __init__(self, download_dir: str = "downloads"):
        """
        Initialize URL handler
        Args:
            download_dir: Directory to store downloaded files
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True, parents=True)
        
        # Supported platforms for video download
        self.video_platforms = [
            'youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com',
            'tiktok.com', 'instagram.com', 'facebook.com', 'twitter.com',
            'x.com', 'reddit.com'
        ]
        
        # Supported document extensions
        self.document_extensions = ['.pdf', '.docx', '.doc', '.txt']
        
        # Video extensions
        self.video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
    
    def validate_url(self, url: str) -> bool:
        """
        Validate if string is a valid URL
        """
        return validators.url(url) is True
    
    def detect_content_type(self, url: str) -> str:
        """
        Detect if URL is video, document, or direct file
        Returns: 'video_platform', 'direct_video', 'document', 'unknown'
        """
        url_lower = url.lower()
        
        # Check if it's a known video platform
        for platform in self.video_platforms:
            if platform in url_lower:
                return 'video_platform'
        
        # Check if URL ends with video extension
        for ext in self.video_extensions:
            if url_lower.endswith(ext):
                return 'direct_video'
        
        # Check if URL ends with document extension
        for ext in self.document_extensions:
            if url_lower.endswith(ext):
                return 'document'
        
        return 'unknown'
    
    def download_video_from_platform(self, url: str) -> Dict:
        """
        Download video from social media platforms using yt-dlp
        Args:
            url: Video URL
        Returns:
            Dictionary with download info
        """
        timestamp = int(time.time())
        output_template = str(self.download_dir / f'video_{timestamp}.%(ext)s')
        
        ydl_opts = {
            'format': 'best[ext=mp4]/best',  # Prefer mp4
            'outtmpl': output_template,
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'max_filesize': 100 * 1024 * 1024,  # 100MB limit
        }
        
        try:
            print(f"📥 Downloading video from: {url}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Get the downloaded filename
                filename = ydl.prepare_filename(info)
                
                if not os.path.exists(filename):
                    raise Exception("Download completed but file not found")
                
                file_size = os.path.getsize(filename) / (1024 * 1024)  # MB
                
                print(f"✅ Video downloaded: {Path(filename).name} ({file_size:.2f} MB)")
                
                return {
                    'success': True,
                    'filepath': filename,
                    'filename': Path(filename).name,
                    'size_mb': round(file_size, 2),
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'platform': info.get('extractor', 'Unknown')
                }
        
        except Exception as e:
            print(f"❌ Error downloading video: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to download video from URL'
            }
    
    def download_direct_file(self, url: str, file_type: str = 'video') -> Dict:
        """
        Download direct file from URL (videos or documents)
        Args:
            url: Direct file URL
            file_type: 'video' or 'document'
        Returns:
            Dictionary with download info
        """
        try:
            print(f"📥 Downloading {file_type} from: {url}")
            
            # Get file extension from URL
            url_path = Path(url)
            extension = url_path.suffix or '.mp4'
            
            # Generate filename
            timestamp = int(time.time())
            filename = f"{file_type}_{timestamp}{extension}"
            filepath = self.download_dir / filename
            
            # Download with progress
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(filepath, 'wb') as f:
                if total_size == 0:
                    f.write(response.content)
                else:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
            
            file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
            
            print(f"✅ {file_type.capitalize()} downloaded: {filename} ({file_size:.2f} MB)")
            
            return {
                'success': True,
                'filepath': str(filepath),
                'filename': filename,
                'size_mb': round(file_size, 2),
                'type': file_type
            }
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Error downloading file: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to download {file_type} from URL'
            }
        except Exception as e:
            print(f"❌ Error: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Unexpected error downloading {file_type}'
            }
    
    def download_from_url(self, url: str) -> Dict:
        """
        Smart download - detects content type and downloads accordingly
        Args:
            url: URL to download from
        Returns:
            Dictionary with download result
        """
        # Validate URL
        if not self.validate_url(url):
            return {
                'success': False,
                'error': 'Invalid URL format',
                'message': 'Please provide a valid URL'
            }
        
        # Detect content type
        content_type = self.detect_content_type(url)
        print(f"🔍 Detected content type: {content_type}")
        
        # Download based on type
        if content_type == 'video_platform':
            return self.download_video_from_platform(url)
        elif content_type == 'direct_video':
            return self.download_direct_file(url, file_type='video')
        elif content_type == 'document':
            return self.download_direct_file(url, file_type='document')
        else:
            # Try to download as direct file
            print("⚠️ Unknown content type, attempting direct download...")
            return self.download_direct_file(url, file_type='unknown')
    
    def cleanup(self, filepath: str) -> bool:
        """
        Delete downloaded file
        """
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"🗑️ Cleaned up: {Path(filepath).name}")
                return True
            return False
        except Exception as e:
            print(f"⚠️ Error cleaning up file: {e}")
            return False


# Test function
if __name__ == "__main__":
    handler = URLHandler()
    
    # Test URLs
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # YouTube video
        "https://example.com/video.mp4",  # Direct video
        "https://example.com/document.pdf"  # Direct document
    ]
    
    print("Testing URL Handler\n" + "="*50)
    
    for url in test_urls:
        print(f"\n🧪 Testing: {url}")
        content_type = handler.detect_content_type(url)
        print(f"   Content type: {content_type}")