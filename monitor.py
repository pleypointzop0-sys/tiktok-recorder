import requests
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

class TikTokMonitor:
    def __init__(self, usernames: list, check_interval: int):
        self.usernames = usernames
        self.check_interval = check_interval
        self.last_status = {}
    
    def check_live(self, username: str) -> Optional[str]:
        """Check if user is live and return stream URL"""
        try:
            url = f"https://www.tiktok.com/@{username}/live"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                if 'live.douyin.com' in response.text or 'webcast' in response.text:
                    return f"https://pull-l3.tiktok.com/live/{username}/playlist.m3u8"
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking {username}: {e}")
            return None
    
    def monitor_loop(self, on_live_callback, on_offline_callback):
        """Main monitoring loop"""
        logger.info(f"Monitoring: {', '.join(self.usernames)}")
        
        while True:
            try:
                for username in self.usernames:
                    stream_url = self.check_live(username)
                    
                    if stream_url and self.last_status.get(username) != "live":
                        logger.info(f"{username} is LIVE!")
                        on_live_callback(username, stream_url)
                        self.last_status[username] = "live"
                        
                    elif not stream_url and self.last_status.get(username) == "live":
                        logger.info(f"{username} went offline")
                        on_offline_callback(username)
                        self.last_status[username] = "offline"
                
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
            
            time.sleep(self.check_interval)
