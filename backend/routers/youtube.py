"""
YouTube Router

Provides endpoints for searching and comparing content on YouTube.
"""

import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.youtube_service import compare_youtube
from routers.compare import QueryFrame, MatchResult, DetectionReport

router = APIRouter()


class YoutubeCompareRequest(BaseModel):
    """Payload for the /youtube/compare endpoint."""
    query: str
    query_frames: list[QueryFrame]


@router.post("/compare", response_model=DetectionReport)
async def compare_youtube_endpoint(request: YoutubeCompareRequest):
    """
    Compare uploaded query frames against YouTube search results.

    The process:
    1. Search YouTube for the given query.
    2. For each query frame, compare against YouTube thumbnails.
    3. Deduplicate matches by video_id, keeping the best similarity score.
    4. Return a DetectionReport.
    """
    start_time = time.perf_counter()

    if not request.query_frames:
        raise HTTPException(status_code=400, detail="query_frames must not be empty.")

    if not request.query:
        raise HTTPException(status_code=400, detail="query must not be empty.")

    # Key: video_id -> MatchResult dict (keeps the best similarity)
    best_matches: dict[str, dict] = {}

    for frame in request.query_frames:
        # Run comparison for this frame
        matches = compare_youtube(
            query=request.query,
            query_embedding=frame.embedding,
            query_phash=frame.phash,
            max_results=5
        )

        for match in matches:
            video_id = match["id"]
            similarity = match["similarity"]

            # Keep the best similarity score per video_id
            existing = best_matches.get(video_id)
            if existing is None or similarity > existing["similarity"]:
                best_matches[video_id] = match

    # Sort by similarity descending
    sorted_matches = sorted(
        best_matches.values(),
        key=lambda m: m["similarity"],
        reverse=True,
    )

    # Convert to MatchResult models
    # Note: match dict from youtube_service already has the required fields
    # but we might need to filter out 'thumbnail_url' if it's not in MatchResult
    match_results = []
    for m in sorted_matches:
        # MatchResult expected fields: id, title, url, source, similarity, phash_distance
        match_results.append(MatchResult(
            id=m["id"],
            title=m["title"],
            url=m["url"],
            source=m["source"],
            similarity=m["similarity"],
            phash_distance=m["phash_distance"]
        ))

    scan_time = round(time.perf_counter() - start_time, 4)

    return DetectionReport(
        matches=match_results,
        total_matches=len(match_results),
        scan_time_seconds=scan_time,
    )
