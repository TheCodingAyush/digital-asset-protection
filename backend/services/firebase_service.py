"""
Firebase Service

Initialises the Firebase Admin SDK once and exposes a helper to
obtain the Firestore client.  The credentials JSON path is read from
the FIREBASE_CREDENTIALS environment variable (loaded via python-dotenv).

Usage
-----
    from services.firebase_service import get_db

    db = get_db()
    db.collection("dataset").document("some-id").set({...})
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()


def _init_firebase() -> None:
    """
    Initialise the Firebase Admin SDK if it has not been initialised yet.

    Uses firebase_admin.get_app() to check for an existing default app so
    that subsequent imports never trigger a second initialisation (singleton
    pattern).

    Raises:
        ValueError: If FIREBASE_CREDENTIALS env variable is not set.
        FileNotFoundError: If the credentials file does not exist at the
                           specified path.
    """
    try:
        firebase_admin.get_app()
        # App already initialised — nothing to do.
    except ValueError:
        # No default app yet — initialise now.
        cred_path = os.getenv("FIREBASE_CREDENTIALS")

        if not cred_path:
            raise ValueError(
                "FIREBASE_CREDENTIALS environment variable is not set. "
                "Set it to the path of your Firebase service-account JSON file."
            )

        if not os.path.isfile(cred_path):
            raise FileNotFoundError(
                f"Firebase credentials file not found at: {cred_path}"
            )

        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)


def get_db() -> firestore.client:
    """
    Return a Firestore client, ensuring Firebase is initialised first.

    Returns:
        A google.cloud.firestore.Client instance ready for use.
    """
    _init_firebase()
    return firestore.client()
