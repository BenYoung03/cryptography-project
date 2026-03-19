import firebase_admin
from firebase_admin import credentials
from firebase_admin.exceptions import FirebaseError
import os
import logging

log = logging.getLogger("uvicorn.error")

def initialize_firebase():
    try:
        # Check if already initialized
        if not firebase_admin._apps:
            key_path = os.path.join(os.path.dirname(__file__), 'cyllenian-d6aec-firebase-adminsdk-fbsvc-518f7a31c5.json')
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
        
        log.info("Successfully connected to Firebase")
        
    except FileNotFoundError:
        log.error("Firebase service account key file not found")
        return None
    except FirebaseError as e:
        log.error(f"Firebase error: {e}")
        return None
    except Exception as e:
        log.error(f"Firebase init error: {e}")
        return None