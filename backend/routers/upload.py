"""
Upload Router

Handles video and image uploads. For each uploaded file, frames are
extracted, and perceptual hashes + CLIP embeddings are generated per
frame. Results are returned in a structured UploadResponse.
"""

import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from services.frame_extractor import extract_frames, extract_single_image
from services.phash_service import generate_phash
from services.clip_service import generate_embedding
from utils.file_handler import save_upload, cleanup_file

router = APIRouter()

# Upload destination
UPLOAD_DIR = "tmp/uploads"

# Allowed extensions
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov"}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


# ── Response Models ──────────────────────────────────────────────────────────

class FrameData(BaseModel):
    """Individual frame analysis result."""
    timestamp: float
    phash: str
    embedding: list[float]


class UploadResponse(BaseModel):
    """Response returned after processing an uploaded file."""
    file_id: str
    file_type: str
    frame_count: int
    frames: list[FrameData]


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_extension(filename: str | None) -> str:
    """Extract lowercased file extension from a filename."""
    if not filename:
        return ""
    import os
    return os.path.splitext(filename)[1].lower()


# ── Routes ───────────────────────────────────────────────────────────────────

@router.post("/video", response_model=UploadResponse)
async def upload_video(file: UploadFile = File(...)):
    """
    Upload a video file (.mp4, .mov).

    The video is saved to disk, frames are extracted at 5-second intervals,
    and each frame is processed to produce a perceptual hash and a CLIP
    embedding. The temporary file is cleaned up after processing.
    """
    ext = _get_extension(file.filename)
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid video format '{ext}'. Allowed: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}",
        )

    file_path: str | None = None
    try:
        # Save uploaded file to disk
        file_path = save_upload(file, UPLOAD_DIR)

        # Extract frames at 5-second intervals
        raw_frames = extract_frames(file_path, interval_seconds=5)

        if not raw_frames:
            raise HTTPException(
                status_code=422,
                detail="Could not extract any frames from the uploaded video. The file may be corrupt.",
            )

        # Process each frame: pHash + CLIP embedding
        frame_results: list[FrameData] = []
        for frame in raw_frames:
            phash = generate_phash(frame["image"])
            embedding = generate_embedding(frame["image"])
            frame_results.append(
                FrameData(
                    timestamp=frame["timestamp"],
                    phash=phash,
                    embedding=embedding,
                )
            )

        file_id = uuid.uuid4().hex

        return UploadResponse(
            file_id=file_id,
            file_type="video",
            frame_count=len(frame_results),
            frames=frame_results,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video processing failed: {e}")
    finally:
        # Clean up the temporary file
        if file_path:
            cleanup_file(file_path)


@router.post("/image", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """
    Upload a single image file (.jpg, .png).

    The image is saved to disk, loaded via PIL, and processed to produce
    a perceptual hash and a CLIP embedding. The temporary file is cleaned
    up after processing.
    """
    ext = _get_extension(file.filename)
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image format '{ext}'. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}",
        )

    file_path: str | None = None
    try:
        # Save uploaded file to disk
        file_path = save_upload(file, UPLOAD_DIR)

        # Load the image
        image_data = extract_single_image(file_path)

        # Generate pHash + CLIP embedding
        phash = generate_phash(image_data["image"])
        embedding = generate_embedding(image_data["image"])

        file_id = uuid.uuid4().hex

        return UploadResponse(
            file_id=file_id,
            file_type="image",
            frame_count=1,
            frames=[
                FrameData(
                    timestamp=0.0,
                    phash=phash,
                    embedding=embedding,
                )
            ],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {e}")
    finally:
        if file_path:
            cleanup_file(file_path)
