from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict, List

from backend.services.gemini_service import analyze_match

router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    original_title: str
    matches: List[Dict[str, Any]]


class AnalyzeResponse(BaseModel):
    analyzed_matches: List[Dict[str, Any]]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_results(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    For each match in the DetectionReport, call Gemini to determine the
    modification type, infringement risk level, and a recommendation.

    Accepts:
        {
            "original_title": str,
            "matches": [ { ...match fields... }, ... ]
        }

    Returns:
        {
            "analyzed_matches": [
                {
                    ...original match fields...,
                    "modification_type": str,
                    "risk_level": str,
                    "recommendation": str
                },
                ...
            ]
        }
    """
    analyzed: List[Dict[str, Any]] = []

    for match in request.matches:
        # Extract the fields Gemini needs; fall back to sensible defaults
        matched_title = str(match.get("matched_title", match.get("title", "Unknown")))
        similarity = float(match.get("similarity", 0.0))
        source = str(match.get("source", "Unknown"))

        gemini_analysis = analyze_match(
            original_title=request.original_title,
            matched_title=matched_title,
            similarity=similarity,
            source=source,
        )

        analyzed.append({**match, **gemini_analysis})

    return AnalyzeResponse(analyzed_matches=analyzed)
