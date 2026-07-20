import requests
import logging
from datetime import datetime
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class DiscordNotifier:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.enabled = bool(webhook_url and webhook_url != "")
    
    def send(self, content: str, embed: Optional[Dict] = None):
        """Send message to Discord"""
        if not self.enabled:
            logger.debug("Discord notifier disabled")
            return
        
        try:
            payload = {"content": content}
            if embed:
                payload["embeds"] = [embed]
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Discord notification sent")
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {e}")
    
    def notify_live_start(self, username: str):
        """Send live start notification"""
        embed = {
            "title": f"🔴 {username} is LIVE!",
            "color": 0xFF0000,
            "description": f"Recording started at {datetime.now().strftime('%H:%M:%S')}",
            "timestamp": datetime.now().isoformat(),
            "footer": {"text": "TikTok Live Recorder"}
        }
        self.send(f"@everyone **{username}** went live!", embed)
    
    def notify_live_end(self, username: str, filename: str, duration: int, file_size: int):
        """Send live end notification"""
        duration_min = duration / 60
        size_mb = file_size / (1024 * 1024)
        
        embed = {
            "title": f"✅ {username} finished streaming",
            "color": 0x00FF00,
            "fields": [
                {"name": "Duration", "value": f"{duration_min:.1f} minutes", "inline": True},
                {"name": "File Size", "value": f"{size_mb:.1f} MB", "inline": True},
                {"name": "Filename", "value": os.path.basename(filename), "inline": False}
            ],
            "timestamp": datetime.now().isoformat(),
            "footer": {"text": "TikTok Live Recorder"}
        }
        self.send(f"Recording saved: {os.path.basename(filename)}", embed)
    
    def notify_error(self, username: str, error: str):
        """Send error notification"""
        embed = {
            "title": f"⚠️ Error - {username}",
            "color": 0xFFA500,
            "description": error[:1000],
            "timestamp": datetime.now().isoformat()
        }
        self.send(f"Error recording {username}", embed)
