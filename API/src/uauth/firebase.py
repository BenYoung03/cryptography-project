import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin.exceptions import FirebaseError
import os
import logging

log = logging.getLogger("uvicorn.error")

def initialize_firebase():
    try:
        # Check if already initialized
        if not firebase_admin._apps:
            key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if not key_path: 
                log.error("[FIREBASE] GOOGLE_APPLICATION_CREDENTIALS env var not set")
                return False
            if not os.path.exists(key_path):
                log.error("[FIREBASE] no service info found at: %s", key_path)
                return False

            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
        
        log.info("[FIREBASE] Successfully connected to Firebase")
        return True
    
    except FirebaseError as e:
        log.error(f"[FIREBASE] error: {e}")
        return False
    
    except Exception as e:
        log.error(f"[FIREBASE] init error: {e}")
        return False

async def auth_user(uid: str, jwt: str) -> bool:
    if not uid or not jwt:
        return False

    if not firebase_admin._apps and not initialize_firebase():
        return False

    try:
        decoded = auth.verify_id_token(jwt)
        return decoded.get("uid") == uid
    except Exception as e:
        log.warning("[FIREBASE] auth rejected token for UID %s: %s", uid, repr(e))
        return False
