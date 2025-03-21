import firebase_admin
from firebase_admin import credentials, auth
from .config import settings
import json
import tempfile
import os
import logging

_firebase_app = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_firebase():
    """Initialize Firebase Admin SDK with credentials from settings."""
    global _firebase_app
    
    try:
        if _firebase_app:
            return _firebase_app

        cred_dict = json.loads(settings.FIREBASE_CREDENTIALS) if settings.FIREBASE_CREDENTIALS else None
        if cred_dict:
            # Create a temporary file to store the credentials
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                json.dump(cred_dict, temp_file)
                temp_file_path = temp_file.name

            try:
                cred = credentials.Certificate(temp_file_path)
                _firebase_app = firebase_admin.initialize_app(cred)
            finally:
                # Clean up the temporary file
                os.unlink(temp_file_path)
        else:
            raise ValueError("Firebase credentials not found in settings")
        
        return _firebase_app
    except Exception as e:
        raise ValueError(f"Failed to initialize Firebase: {str(e)}")

def get_firebase_app():
    """Get the initialized Firebase app instance."""
    global _firebase_app
    if not _firebase_app:
        _firebase_app = initialize_firebase()
    return _firebase_app

def verify_firebase_token(token: str):
    """Verify a Firebase ID token."""
    try:
        # Ensure Firebase is initialized
        get_firebase_app()
        
        # Log the token for debugging
        logger.info(f"Verifying token: {token[:20]}...")
        
        # Verify the token
        decoded_token = auth.verify_id_token(token)
        
        # Log the decoded token
        logger.info(f"Decoded token: {decoded_token}")
        
        return decoded_token
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        return None 