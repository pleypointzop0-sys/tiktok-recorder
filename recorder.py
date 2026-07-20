import os
import subprocess
import logging
from datetime import datetime
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class TikTokRecorder:
    def __init__(self, recordings_folder: str, max_duration: int):
        self.recordings_folder = recordings_folder
        self.max_duration = max_duration
        self.active_recordings: Dict[str, dict] = {}
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """Check if FFmpeg is installed"""
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            logger.info("FFmpeg found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("FFmpeg not found! Please install FFmpeg.")
            raise
    
    def start(self, username: str, stream_url: str, notifier=None) -> bool:
        """Start recording a live stream"""
        if username in self.active_recordings:
            logger.info(f"Already recording {username}")
            return False
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.recordings_folder, f"{username}_{timestamp}.ts")
        
        try:
            cmd = [
                "ffmpeg",
                "-i", stream_url,
                "-c", "copy",
                "-bsf:a", "aac_adtstoasc",
                "-t", str(self.max_duration),
                "-y",
                filename
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.active_recordings[username] = {
                "process": process,
                "filename": filename,
                "start_time": datetime.now()
            }
            
            logger.info(f"Started recording {username} -> {os.path.basename(filename)}")
            
            if notifier:
                notifier.notify_live_start(username)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start recording {username}: {e}")
            if notifier:
                notifier.notify_error(username, str(e))
            return False
    
    def stop(self, username: str, notifier=None, uploader=None) -> Optional[str]:
        """Stop recording for a user"""
        if username not in self.active_recordings:
            return None
        
        recording = self.active_recordings[username]
        process = recording["process"]
        filename = recording["filename"]
        start_time = recording["start_time"]
        
        try:
            process.terminate()
            process.wait(timeout=10)
            
            duration = (datetime.now() - start_time).seconds
            file_size = os.path.getsize(filename) if os.path.exists(filename) else 0
            
            if file_size > 0:
                logger.info(f"Stopped recording {username} - {duration}s, {file_size} bytes")
                
                uploaded = False
                if uploader:
                    uploaded = uploader.upload(filename)
                
                if notifier:
                    notifier.notify_live_end(username, filename, duration, file_size)
                
                if uploaded:
                    os.remove(filename)
                    logger.info(f"Deleted local file: {filename}")
                
                del self.active_recordings[username]
                return filename
            else:
                if os.path.exists(filename):
                    os.remove(filename)
                del self.active_recordings[username]
                return None
                
        except subprocess.TimeoutExpired:
            process.kill()
            logger.error(f"Force killed recording for {username}")
            del self.active_recordings[username]
            return None
        except Exception as e:
            logger.error(f"Error stopping recording {username}: {e}")
            if notifier:
                notifier.notify_error(username, str(e))
            return None
    
    def stop_all(self):
        """Stop all active recordings"""
        for username in list(self.active_recordings.keys()):
            self.stop(username)
