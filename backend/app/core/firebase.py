import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, auth
from app.core.config import settings
from app.core.logging import logger

_db_client = None

def init_firebase():
    global _db_client
    if firebase_admin._apps:
        _db_client = firestore.client()
        return _db_client

    try:
        if settings.FIREBASE_CREDENTIALS_PATH and os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            project_id = getattr(cred, "project_id", None) or settings.FIREBASE_PROJECT_ID
            firebase_admin.initialize_app(cred, {"projectId": project_id})
            logger.info(f"Firebase Admin initialized via service account file (project: {project_id}).")
        elif settings.FIREBASE_PRIVATE_KEY and settings.FIREBASE_CLIENT_EMAIL:
            private_key = settings.FIREBASE_PRIVATE_KEY.replace('\\n', '\n')
            cred_dict = {
                "type": "service_account",
                "project_id": settings.FIREBASE_PROJECT_ID,
                "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID or "default_key_id",
                "private_key": private_key,
                "client_email": settings.FIREBASE_CLIENT_EMAIL,
                "client_id": "123456789",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
            }
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {"projectId": settings.FIREBASE_PROJECT_ID})
            logger.info("Firebase Admin initialized via environment variables.")
        else:
            logger.warning("Firebase credentials missing. Using local in-memory fallback store.")
            return None
        return None
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
        return None

def get_firestore_client():
    global _db_client
    if _db_client is None:
        init_firebase()
        if firebase_admin._apps:
            try:
                _db_client = firestore.client()
            except Exception as e:
                logger.warning(f"Firestore client init fallback: {e}")
                _db_client = None
    return _db_client


def verify_firebase_token(id_token: str) -> dict:
    """Verifies Firebase ID token or fallback synthetic token."""
    try:
        if firebase_admin._apps:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        else:
            # Fallback mock decoder for dev testing when Firebase is unconfigured
            if id_token.startswith("mock_token_"):
                uid = id_token.replace("mock_token_", "")
                return {
                    "uid": uid,
                    "email": f"{uid}@example.com",
                    "name": uid.capitalize(),
                    "role": "admin" if uid == "admin" else "user"
                }
            raise ValueError("Firebase App not initialized and non-mock token provided")
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise ValueError(f"Invalid authentication token: {str(e)}")
