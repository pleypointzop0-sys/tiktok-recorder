import os
from pathlib import Path

class Config:
    # TikTok usernames to monitor
    USERNAMES = [u.strip() for u in os.environ.get("TIKTOK_USERNAMES", "mezopotamya.047").split(",") if u.strip()]
    
    # Check interval in seconds
    CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", "60"))
    
    # Max recording duration in seconds
    MAX_RECORDING_DURATION = int(os.environ.get("MAX_RECORDING_DURATION", "7200"))
    
    # Discord webhook URL
    DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")
    
    # Dropbox access token
    DROPBOX_TOKEN = os.environ.get("DROPBOX_TOKEN", "")
    
    # Recording folder (use /tmp on Render, local otherwise)
    RECORDINGS_FOLDER = os.environ.get("RECORDINGS_FOLDER", "./recordings")
    
    # Enable debug mode
    DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []
        if not cls.USERNAMES:
            errors.append("No usernames configured! Set TIKTOK_USERNAMES")
        if not cls.DISCORD_WEBHOOK_URL:
            errors.append("Discord webhook not configured!")
        if not cls.DROPBOX_TOKEN:
            errors.append("Dropbox token not configured! Uploads will fail.")
        return errors

# Create recordings folder
Path(Config.RECORDINGS_FOLDER).mkdir(parents=True, exist_ok=True)
