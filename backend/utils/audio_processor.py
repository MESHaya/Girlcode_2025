"""
Audio Processor - Extract audio from video files
"""
import ffmpeg
import os
from pathlib import Path

class AudioExtractor:
    def __init__(self, output_dir="temp_audio"):
        """
        Initialize audio extractor
        Args:
            output_dir: Directory to store extracted audio files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
    
    def check_has_audio(self, video_path: str) -> bool:
        """
        Check if video file has an audio stream
        Args:
            video_path: Path to video file
        Returns:
            True if audio exists, False otherwise
        """
        try:
            probe = ffmpeg.probe(video_path)
            audio_streams = [s for s in probe['streams'] if s['codec_type'] == 'audio']
            has_audio = len(audio_streams) > 0
            
            if has_audio:
                print(f"✅ Audio stream detected")
            else:
                print(f"⚠️ No audio stream found")
            
            return has_audio
        except Exception as e:
            print(f"⚠️ Error checking audio: {e}")
            return False
    
    def extract_audio(self, video_path: str, sample_rate: int = 16000) -> dict:
        """
        Extract audio from video file and save as WAV
        Args:
            video_path: Path to video file
            sample_rate: Audio sample rate (default: 16000 Hz)
        Returns:
            dict with 'success', 'audio_path', and 'message' keys
        """
        # Validate input file exists
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        try:
            # First, check if video has audio stream
            print(f"🔍 Checking for audio stream in: {Path(video_path).name}")
            probe = ffmpeg.probe(video_path)
            
            # Look for audio streams
            audio_streams = [s for s in probe['streams'] if s['codec_type'] == 'audio']
            
            if not audio_streams:
                print(f"⚠️ No audio stream found in video")
                return {
                    'success': False,
                    'audio_path': None,
                    'message': 'Video has no audio track',
                    'has_audio': False
                }
            
            # Generate output filename
            video_name = Path(video_path).stem
            audio_path = self.output_dir / f"{video_name}.wav"
            
            print(f"🎵 Extracting audio from: {Path(video_path).name}")
            print(f"   Audio codec: {audio_streams[0].get('codec_name', 'unknown')}")
            
            # Extract audio using ffmpeg
            stream = ffmpeg.input(video_path)
            audio = stream.audio  # Select only audio stream
            stream = ffmpeg.output(
                audio,
                str(audio_path),
                acodec='pcm_s16le',  # WAV format (uncompressed)
                ac=1,                 # Mono channel (reduces file size)
                ar=str(sample_rate)   # Sample rate (16kHz good for speech)
            )
            
            # Run ffmpeg command
            ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
            
            # Verify output file was created
            if not audio_path.exists():
                raise Exception("Audio file was not created")
            
            file_size = audio_path.stat().st_size / (1024 * 1024)  # Size in MB
            print(f"✅ Audio extracted successfully: {audio_path.name} ({file_size:.2f} MB)")
            
            return {
                'success': True,
                'audio_path': str(audio_path),
                'message': 'Audio extracted successfully',
                'has_audio': True
            }
            
        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            print(f"❌ FFmpeg error: {error_message}")
            
            # Check if it's specifically the "no audio" error
            if "does not contain any stream" in error_message or "Output file does not contain any stream" in error_message:
                return {
                    'success': False,
                    'audio_path': None,
                    'message': 'Video file does not contain an audio track',
                    'has_audio': False
                }
            
            raise Exception(f"Failed to extract audio: {error_message}")
        except Exception as e:
            print(f"❌ Error extracting audio: {e}")
            raise
    
    def get_audio_info(self, audio_path: str) -> dict:
        """
        Get information about audio file
        Args:
            audio_path: Path to audio file
        Returns:
            Dictionary with audio metadata
        """
        try:
            probe = ffmpeg.probe(audio_path)
            audio_info = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
            
            return {
                "codec": audio_info.get('codec_name', 'unknown'),
                "sample_rate": int(audio_info.get('sample_rate', 0)),
                "channels": int(audio_info.get('channels', 0)),
                "duration": float(probe['format'].get('duration', 0)),
                "size_mb": os.path.getsize(audio_path) / (1024 * 1024)
            }
        except Exception as e:
            print(f"⚠️ Could not get audio info: {e}")
            return {}
    
    def get_video_audio_info(self, video_path: str) -> dict:
        """
        Get audio stream information from video file
        Args:
            video_path: Path to video file
        Returns:
            Dictionary with audio stream info or None if no audio
        """
        try:
            probe = ffmpeg.probe(video_path)
            audio_streams = [s for s in probe['streams'] if s['codec_type'] == 'audio']
            
            if not audio_streams:
                return None
            
            audio_stream = audio_streams[0]
            return {
                "codec": audio_stream.get('codec_name', 'unknown'),
                "sample_rate": int(audio_stream.get('sample_rate', 0)),
                "channels": int(audio_stream.get('channels', 0)),
                "bit_rate": int(audio_stream.get('bit_rate', 0))
            }
        except Exception as e:
            print(f"⚠️ Error getting video audio info: {e}")
            return None
    
    def cleanup(self, audio_path: str) -> bool:
        """
        Delete temporary audio file
        Args:
            audio_path: Path to audio file to delete
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
                print(f"🗑️ Cleaned up: {Path(audio_path).name}")
                return True
            return False
        except Exception as e:
            print(f"⚠️ Error cleaning up audio file: {e}")
            return False
    
    def cleanup_all(self) -> int:
        """
        Clean up all audio files in output directory
        Returns:
            Number of files deleted
        """
        count = 0
        try:
            for file in self.output_dir.glob("*.wav"):
                file.unlink()
                count += 1
            if count > 0:
                print(f"🗑️ Cleaned up {count} audio file(s)")
        except Exception as e:
            print(f"⚠️ Error during cleanup: {e}")
        return count


# Test function
if __name__ == "__main__":
    # Quick test of the audio extractor
    extractor = AudioExtractor()
    
    # Test with a video file (replace with your actual test file)
    test_video = "test_video.mp4"
    
    if os.path.exists(test_video):
        try:
            # Check if video has audio
            has_audio = extractor.check_has_audio(test_video)
            print(f"\nVideo has audio: {has_audio}")
            
            if has_audio:
                # Get video audio info
                video_audio_info = extractor.get_video_audio_info(test_video)
                print(f"\n📊 Video Audio Stream Info:")
                for key, value in video_audio_info.items():
                    print(f"   {key}: {value}")
                
                # Extract audio
                result = extractor.extract_audio(test_video)
                
                if result['success']:
                    print(f"\n✅ Success! Audio saved to: {result['audio_path']}")
                    
                    # Get extracted audio info
                    info = extractor.get_audio_info(result['audio_path'])
                    print(f"\n📊 Extracted Audio Info:")
                    for key, value in info.items():
                        print(f"   {key}: {value}")
                else:
                    print(f"\n⚠️ {result['message']}")
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
    else:
        print(f"⚠️ Test video not found: {test_video}")
        print("Place a test video file in the backend directory to test audio extraction")