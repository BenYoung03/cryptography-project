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
            key_path = os.getenv(
                "GOOGLE_APPLICATION_CREDENTIALS",
                os.path.join(
                    os.path.dirname(__file__),
                    "cyllenian-d6aec-firebase-adminsdk-fbsvc-518f7a31c5.json"
                )
            )
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
        
        log.info("Successfully connected to Firebase")
        return True
        
    except FileNotFoundError:
        log.error("Firebase service account key file not found")
        return False
    except FirebaseError as e:
        log.error(f"Firebase error: {e}")
        return False
    except Exception as e:
        log.error(f"Firebase init error: {e}")
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
        log.warning("Firebase auth rejected token for UID %s: %s", uid, repr(e))
        return False
