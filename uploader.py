import os
import logging
import dropbox
from pathlib import Path

logger = logging.getLogger(__name__)

class DropboxUploader:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.enabled = bool(access_token and access_token != "")
        
        if self.enabled:
            try:
                self.dbx = dropbox.Dropbox(access_token)
                self.dbx.users_get_current_account()
                logger.info("Dropbox connection successful")
            except Exception as e:
                logger.error(f"Dropbox connection failed: {e}")
                self.enabled = False
    
    def upload(self, local_path: str, remote_path: str = None) -> bool:
        """Upload file to Dropbox"""
        if not self.enabled:
            logger.warning("Dropbox uploader disabled")
            return False
        
        try:
            if not remote_path:
                remote_path = f"/{os.path.basename(local_path)}"
            
            logger.info(f"Uploading {local_path} to Dropbox{remote_path}")
            
            with open(local_path, "rb") as f:
                self.dbx.files_upload(
                    f.read(),
                    remote_path,
                    mode=dropbox.files.WriteMode.overwrite
                )
            
            logger.info(f"Successfully uploaded {os.path.basename(local_path)}")
            return True
            
        except Exception as e:
            logger.error(f"Dropbox upload failed: {e}")
            return False
