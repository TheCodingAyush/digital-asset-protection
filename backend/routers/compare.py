"""
Compare Router

Implements the two-stage content matching pipeline:
  Stage 1 — pHash (perceptual hash) filtering for fast candidate narrowing.
  Stage 2 — CLIP embedding cosine similarity for precise ranking.

Results are deduplicated and returned as a DetectionReport.
"""

import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.phash_service import batch_compare_phash
from services.clip_service import batch_compare_clip
from services.firebase_service import get_db
from services.youtube_service import compare_youtube
import asyncio

router = APIRouter()


# ── Request / Response Models ────────────────────────────────────────────────

class QueryFrame(BaseModel):
    """A single frame from the user's uploaded content."""
    phash: str
    embedding: list[float]


class DatasetItem(BaseModel):
    """A single item in the reference dataset to compare against."""
    id: str
    phash: str
    embedding: list[float]
    source: str
    title: str
    url: str


class CompareRequest(BaseModel):
    """Payload for the /compare endpoint."""
    query_frames: list[QueryFrame]
    dataset: list[DatasetItem]


class MatchResult(BaseModel):
    """A single matched item from the dataset."""
    id: str
    title: str
    url: str
    source: str
    similarity: float
    phash_distance: int


class DetectionReport(BaseModel):
    """Aggregated comparison results."""
    matches: list[MatchResult]
    total_matches: int
    scan_time_seconds: float


class UnifiedCompareRequest(BaseModel):
    """Payload for the /compare/unified endpoint."""
    query: str
    query_frames: list[QueryFrame]


# ── Route ────────────────────────────────────────────────────────────────────

@router.post("/", response_model=DetectionReport)
async def compare_content(request: CompareRequest):
    """
    Compare uploaded query frames against a reference dataset using a
    two-stage pipeline:

    **Stage 1 — pHash pre-filter:**
    For each query frame, batch_compare_phash narrows the dataset to
    candidates with a Hamming distance < 15.

    **Stage 2 — CLIP verification:**
    For each Stage-1 candidate, cosine similarity of CLIP embeddings
    is computed. Only candidates with similarity > 0.85 are kept.

    Results from all query frames are aggregated, deduplicated by
    dataset item ID (keeping the best score per item), and sorted by
    similarity descending.
    """
    start_time = time.perf_counter()

    if not request.query_frames:
        raise HTTPException(status_code=400, detail="query_frames must not be empty.")

    if not request.dataset:
        raise HTTPException(status_code=400, detail="dataset must not be empty.")

    # Extract dataset-level lists for batch operations
    dataset_phashes: list[str] = [item.phash for item in request.dataset]
    dataset_embeddings: list[list[float]] = [item.embedding for item in request.dataset]

    # Accumulate best match per dataset item ID
    # Key: dataset item id → MatchResult dict (keeps the best similarity)
    best_matches: dict[str, dict] = {}

    for query_frame in request.query_frames:
        # ── Stage 1: pHash candidate filtering ───────────────────────
        phash_candidates = batch_compare_phash(query_frame.phash, dataset_phashes)

        if not phash_candidates:
            continue

        # Build filtered embedding list + index mapping for Stage 2
        candidate_indices: list[int] = [c["index"] for c in phash_candidates]
        candidate_embeddings: list[list[float]] = [
            dataset_embeddings[i] for i in candidate_indices
        ]

        # Map from position-in-filtered-list → original dataset index
        phash_distance_by_original_idx: dict[int, int] = {
            c["index"]: c["distance"] for c in phash_candidates
        }

        # ── Stage 2: CLIP embedding verification ─────────────────────
        clip_matches = batch_compare_clip(query_frame.embedding, candidate_embeddings)

        for clip_match in clip_matches:
            # clip_match["index"] is relative to candidate_embeddings
            original_idx = candidate_indices[clip_match["index"]]
            dataset_item = request.dataset[original_idx]

            phash_dist = phash_distance_by_original_idx[original_idx]
            similarity = clip_match["similarity"]

            # Keep the best similarity score per dataset item
            existing = best_matches.get(dataset_item.id)
            if existing is None or similarity > existing["similarity"]:
                best_matches[dataset_item.id] = {
                    "id": dataset_item.id,
                    "title": dataset_item.title,
                    "url": dataset_item.url,
                    "source": dataset_item.source,
                    "similarity": similarity,
                    "phash_distance": phash_dist,
                }

    # Sort by similarity descending
    sorted_matches = sorted(
        best_matches.values(),
        key=lambda m: m["similarity"],
        reverse=True,
    )

    match_results = [MatchResult(**m) for m in sorted_matches]
    scan_time = round(time.perf_counter() - start_time, 4)

    return DetectionReport(
        matches=match_results,
        total_matches=len(match_results),
        scan_time_seconds=scan_time,
    )


# ── Auto-compare (Firestore dataset) ─────────────────────────────────────────

class AutoCompareRequest(BaseModel):
    """Payload for /compare/auto — only query_frames needed; dataset is fetched from Firestore."""
    query_frames: list[QueryFrame]


@router.post("/auto", response_model=DetectionReport)
async def compare_auto(request: AutoCompareRequest):
    """
    Compare uploaded query frames against the full dataset stored in Firestore.

    The dataset is fetched from the `dataset` Firestore collection at request
    time. The same two-stage pHash + CLIP pipeline used by POST /compare/ is
    then applied automatically.

    **Stage 1 — pHash pre-filter:** Hamming distance < 15
    **Stage 2 — CLIP verification:** Cosine similarity > 0.85

    Returns:
        A DetectionReport identical in shape to POST /compare/.
    """
    from fastapi import HTTPException as _HTTPException

    start_time = time.perf_counter()

    if not request.query_frames:
        raise _HTTPException(status_code=400, detail="query_frames must not be empty.")

    # ── Fetch dataset from Firestore ──────────────────────────────────────────
    try:
        db = get_db()
        docs = db.collection("dataset").stream()
        raw_items = [doc.to_dict() for doc in docs]
    except Exception as e:
        raise _HTTPException(
            status_code=500,
            detail=f"Failed to fetch dataset from Firestore: {e}",
        )

    if not raw_items:
        raise _HTTPException(
            status_code=400,
            detail="Firestore dataset collection is empty. Add items via POST /dataset/add first.",
        )

    # Deserialise into DatasetItem objects for type safety
    try:
        dataset = [DatasetItem(**item) for item in raw_items]
    except Exception as e:
        raise _HTTPException(
            status_code=500,
            detail=f"Firestore dataset contains malformed documents: {e}",
        )

    # ── Reuse the same two-stage pipeline ────────────────────────────────────
    dataset_phashes: list[str] = [item.phash for item in dataset]
    dataset_embeddings: list[list[float]] = [item.embedding for item in dataset]
    best_matches: dict[str, dict] = {}

    for query_frame in request.query_frames:
        phash_candidates = batch_compare_phash(query_frame.phash, dataset_phashes)

        if not phash_candidates:
            continue

        candidate_indices: list[int] = [c["index"] for c in phash_candidates]
        candidate_embeddings: list[list[float]] = [
            dataset_embeddings[i] for i in candidate_indices
        ]
        phash_distance_by_original_idx: dict[int, int] = {
            c["index"]: c["distance"] for c in phash_candidates
        }

        clip_matches = batch_compare_clip(query_frame.embedding, candidate_embeddings)

        for clip_match in clip_matches:
            original_idx = candidate_indices[clip_match["index"]]
            dataset_item = dataset[original_idx]

            phash_dist = phash_distance_by_original_idx[original_idx]
            similarity = clip_match["similarity"]

            existing = best_matches.get(dataset_item.id)
            if existing is None or similarity > existing["similarity"]:
                best_matches[dataset_item.id] = {
                    "id": dataset_item.id,
                    "title": dataset_item.title,
                    "url": dataset_item.url,
                    "source": dataset_item.source,
                    "similarity": similarity,
                    "phash_distance": phash_dist,
                }

    sorted_matches = sorted(
        best_matches.values(),
        key=lambda m: m["similarity"],
        reverse=True,
    )

    match_results = [MatchResult(**m) for m in sorted_matches]
    scan_time = round(time.perf_counter() - start_time, 4)

    return DetectionReport(
        matches=match_results,
        total_matches=len(match_results),
        scan_time_seconds=scan_time,
    )


@router.post("/unified", response_model=DetectionReport)
async def compare_unified(request: UnifiedCompareRequest):
    """
    Unified comparison endpoint that runs both Firestore dataset matching
    and YouTube search matching in parallel.

    Results are combined, deduplicated by ID (keeping best similarity),
    and sorted by similarity descending.
    """
    start_time = time.perf_counter()

    if not request.query_frames:
        raise HTTPException(status_code=400, detail="query_frames must not be empty.")

    async def run_dataset_compare():
        # ── Fetch dataset from Firestore ──────────────────────────────────────
        try:
            db = get_db()
            docs = db.collection("dataset").stream()
            raw_items = [doc.to_dict() for doc in docs]
        except Exception as e:
            print(f"[unified] Firestore error: {e}")
            return []

        if not raw_items:
            return []

        dataset = [DatasetItem(**item) for item in raw_items]
        dataset_phashes: list[str] = [item.phash for item in dataset]
        dataset_embeddings: list[list[float]] = [item.embedding for item in dataset]
        
        matches = {}
        for query_frame in request.query_frames:
            phash_candidates = batch_compare_phash(query_frame.phash, dataset_phashes)
            if not phash_candidates: continue

            candidate_indices = [c["index"] for c in phash_candidates]
            candidate_embeddings = [dataset_embeddings[i] for i in candidate_indices]
            phash_dist_map = {c["index"]: c["distance"] for c in phash_candidates}

            clip_matches = batch_compare_clip(query_frame.embedding, candidate_embeddings)
            for clip_match in clip_matches:
                idx = candidate_indices[clip_match["index"]]
                item = dataset[idx]
                sim = clip_match["similarity"]
                
                if item.id not in matches or sim > matches[item.id]["similarity"]:
                    matches[item.id] = {
                        "id": item.id,
                        "title": item.title,
                        "url": item.url,
                        "source": "Dataset",  # Tag as Dataset
                        "similarity": sim,
                        "phash_distance": phash_dist_map[idx],
                    }
        return list(matches.values())

    async def run_youtube_compare():
        # YouTube comparison (run in thread because it's sync and heavy)
        best_matches = {}
        for frame in request.query_frames:
            # We use a thread to avoid blocking the event loop
            yt_matches = await asyncio.to_thread(
                compare_youtube,
                query=request.query,
                query_embedding=frame.embedding,
                query_phash=frame.phash
            )
            for m in yt_matches:
                if m["id"] not in best_matches or m["similarity"] > best_matches[m["id"]]["similarity"]:
                    best_matches[m["id"]] = m
        return list(best_matches.values())

    # Run both in parallel
    dataset_results, youtube_results = await asyncio.gather(
        run_dataset_compare(),
        run_youtube_compare()
    )

    # Combine and deduplicate
    combined: dict[str, dict] = {}
    for res in dataset_results + youtube_results:
        item_id = res["id"]
        if item_id not in combined or res["similarity"] > combined[item_id]["similarity"]:
            combined[item_id] = res

    # Sort and format
    sorted_matches = sorted(
        combined.values(),
        key=lambda x: x["similarity"],
        reverse=True
    )
    
    match_results = [MatchResult(**m) for m in sorted_matches]
    scan_time = round(time.perf_counter() - start_time, 4)

    return DetectionReport(
        matches=match_results,
        total_matches=len(match_results),
        scan_time_seconds=scan_time,
    )
