"""
Dataset Router

Manages the reference dataset stored in Firestore.  Each document in the
`dataset` collection represents one indexed media asset with its pHash and
CLIP embedding, used by the comparison pipeline.

Endpoints
---------
POST   /dataset/add       — persist a new DatasetItem to Firestore
GET    /dataset/          — retrieve all items from Firestore
DELETE /dataset/{item_id} — remove a single item by document ID
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.firebase_service import get_db

router = APIRouter()

# Firestore collection name
_COLLECTION = "dataset"


# ── Schema ────────────────────────────────────────────────────────────────────

class DatasetItem(BaseModel):
    """A single indexed media asset."""
    id: str
    title: str
    url: str
    source: str
    phash: str
    embedding: list[float]


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/add", status_code=201)
async def add_dataset_item(item: DatasetItem) -> dict:
    """
    Persist a new DatasetItem to Firestore.

    The document is stored under `dataset/{item.id}` so that the client
    controls the document ID (allowing idempotent upserts).

    Returns:
        A confirmation dict with the stored document ID.
    """
    try:
        db = get_db()
        db.collection(_COLLECTION).document(item.id).set(item.model_dump())
        return {"status": "added", "id": item.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add dataset item: {e}")


@router.get("/")
async def get_dataset() -> dict:
    """
    Fetch and return all documents from the Firestore `dataset` collection.

    Returns:
        A dict with a `dataset` key containing a list of all DatasetItem dicts.
    """
    try:
        db = get_db()
        docs = db.collection(_COLLECTION).stream()
        items = [doc.to_dict() for doc in docs]
        return {"dataset": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dataset: {e}")


@router.delete("/{item_id}")
async def delete_dataset_item(item_id: str) -> dict:
    """
    Delete a single document from the Firestore `dataset` collection by ID.

    Args:
        item_id: The Firestore document ID (same value that was used in add).

    Returns:
        A confirmation dict with the deleted document ID.

    Raises:
        HTTP 404 if no document with the given ID exists.
    """
    try:
        db = get_db()
        doc_ref = db.collection(_COLLECTION).document(item_id)

        if not doc_ref.get().exists:
            raise HTTPException(
                status_code=404,
                detail=f"Dataset item '{item_id}' not found.",
            )

        doc_ref.delete()
        return {"status": "deleted", "id": item_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete dataset item: {e}")
