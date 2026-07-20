#!/usr/bin/env python3
"""
TikTok Live Recorder - Main Application
"""
import os
import sys
import threading
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from config import Config
from notifier import DiscordNotifier
from uploader import DropboxUploader
from recorder import TikTokRecorder
from monitor import TikTokMonitor

# Setup logging
logging.basicConfig(
    level=logging.DEBUG if Config.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tiktok_recorder.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PingHandler(BaseHTTPRequestHandler):
    """Simple web server for keep-alive pings"""
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    
    def log_message(self, format, *args):
        pass  # Suppress web server logs

def start_web_server():
    """Start web server for Render keep-alive"""
    try:
        port = int(os.environ.get("PORT", 10000))
        server = HTTPServer(('0.0.0.0', port), PingHandler)
        logger.info(f"Web server started on port {port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Web server error: {e}")

def main():
    """Main application entry point"""
    logger.info("=" * 60)
    logger.info("TikTok Live Recorder starting...")
    logger.info(f"Monitoring: {Config.USERNAMES}")
    logger.info(f"Recordings folder: {Config.RECORDINGS_FOLDER}")
    logger.info("=" * 60)
    
    # Validate configuration
    errors = Config.validate()
    if errors:
        for error in errors:
            logger.error(error)
        if any("usernames" in e.lower() for e in errors):
            logger.warning("Using default username: mezopotamya.047")
            Config.USERNAMES = ["mezopotamya.047"]
    
    # Initialize components
    notifier = DiscordNotifier(Config.DISCORD_WEBHOOK_URL)
    uploader = DropboxUploader(Config.DROPBOX_TOKEN)
    recorder = TikTokRecorder(Config.RECORDINGS_FOLDER, Config.MAX_RECORDING_DURATION)
    monitor = TikTokMonitor(Config.USERNAMES, Config.CHECK_INTERVAL)
    
    # Send startup notification
    notifier.send("🎥 **TikTok Live Recorder is online!**\nMonitoring: " + ", ".join(Config.USERNAMES))
    
    # Callback functions
    def on_live(username: str, stream_url: str):
        recorder.start(username, stream_url, notifier)
    
    def on_offline(username: str):
        recorder.stop(username, notifier, uploader)
    
    # Start monitoring
    try:
        monitor.monitor_loop(on_live, on_offline)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        recorder.stop_all()
        notifier.send("🛑 **TikTok Recorder shutting down...**")
        logger.info("Goodbye!")

if __name__ == "__main__":
    # Start web server in background thread
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()
    
    # Run main in main thread
    main()
