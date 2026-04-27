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
import json
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

    Supports two modes via the FIREBASE_CREDENTIALS environment variable:
      1. File path  — value is a path to a JSON file (local dev)
      2. JSON string — value is the raw JSON content (HF Spaces / production)

    Raises:
        ValueError: If FIREBASE_CREDENTIALS env variable is not set.
    """
    try:
        firebase_admin.get_app()
        # App already initialised — nothing to do.
    except ValueError:
        # No default app yet — initialise now.
        cred_value = os.getenv("FIREBASE_CREDENTIALS")

        if not cred_value:
            raise ValueError(
                "FIREBASE_CREDENTIALS environment variable is not set. "
                "Set it to the path of your Firebase service-account JSON file, "
                "or the raw JSON string of the credentials."
            )

        # Mode 1: file path (local development)
        if os.path.isfile(cred_value):
            cred = credentials.Certificate(cred_value)

        # Mode 2: raw JSON string (HF Spaces / server deployment)
        else:
            try:
                cred_dict = json.loads(cred_value)
                cred = credentials.Certificate(cred_dict)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    "FIREBASE_CREDENTIALS is not a valid file path or JSON string."
                ) from exc

        firebase_admin.initialize_app(cred)


def get_db() -> firestore.client:
    """
    Return a Firestore client, ensuring Firebase is initialised first.

    Returns:
        A google.cloud.firestore.Client instance ready for use.
    """
    _init_firebase()
    return firestore.client()
