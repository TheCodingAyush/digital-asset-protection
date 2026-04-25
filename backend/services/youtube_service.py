"""
YouTube Service

Integrates YouTube Data API v3 for content matching. Provides functionality
to search for videos and compare thumbnails using pHash and CLIP embeddings.
"""

import os
import requests
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

from services.phash_service import generate_phash, compare_phash
from services.clip_service import generate_embedding, cosine_similarity

# Load environment variables
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"


def search_youtube_thumbnails(query: str, max_results: int = 5) -> list[dict]:
    """
    Search YouTube for videos and extract their metadata and high-quality thumbnails.

    Args:
        query: The search term.
        max_results: Maximum number of results to return.

    Returns:
        A list of dicts containing:
            - video_id (str)
            - title (str)
            - thumbnail_url (str)
            - channel_title (str)
            - video_url (str)
    """
    if not YOUTUBE_API_KEY:
        print("[youtube_service] Warning: YOUTUBE_API_KEY not found in environment.")
        return []

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY
    }

    try:
        response = requests.get(YOUTUBE_SEARCH_URL, params=params)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("items", []):
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            
            # Use high quality thumbnail if available
            thumbnail_url = snippet["thumbnails"].get("high", {}).get("url")
            if not thumbnail_url:
                thumbnail_url = snippet["thumbnails"].get("default", {}).get("url")

            results.append({
                "video_id": video_id,
                "title": snippet["title"],
                "thumbnail_url": thumbnail_url,
                "channel_title": snippet["channelTitle"],
                "video_url": f"https://www.youtube.com/watch?v={video_id}"
            })

        return results
    except Exception as e:
        print(f"[youtube_service] Error searching YouTube: {e}")
        return []


def compare_youtube(
    query: str,
    query_embedding: list[float],
    query_phash: str,
    max_results: int = 5
) -> list[dict]:
    """
    Search YouTube and compare results against a query frame using pHash and CLIP.

    Args:
        query: Search term for YouTube.
        query_embedding: CLIP embedding of the query frame.
        query_phash: pHash of the query frame.
        max_results: Max results to fetch from YouTube.

    Returns:
        A list of matched results sorted by similarity descending.
    """
    thumbnails = search_youtube_thumbnails(query, max_results)
    matches = []

    for thumb in thumbnails:
        try:
            # Download thumbnail
            response = requests.get(thumb["thumbnail_url"])
            response.raise_for_status()
            
            # Convert to PIL Image
            img = Image.open(BytesIO(response.content))
            
            # Generate pHash and CLIP embedding
            thumb_phash = generate_phash(img)
            thumb_embedding = generate_embedding(img)
            
            # Compare
            phash_result = compare_phash(query_phash, thumb_phash)
            sim = cosine_similarity(query_embedding, thumb_embedding)
            
            print(f"[youtube_service] Video: {thumb['video_id']}, Title: {thumb['title'][:30]}..., Similarity: {sim:.4f}")

            # Threshold: cosine_similarity > 0.3 (Lowered for broader matching)
            if sim > 0.3:
                matches.append({
                    "id": thumb["video_id"],
                    "title": thumb["title"],
                    "url": thumb["video_url"],
                    "source": "YouTube",
                    "similarity": round(sim, 4),
                    "phash_distance": phash_result["distance"],
                    "thumbnail_url": thumb["thumbnail_url"]
                })
        except Exception as e:
            print(f"[youtube_service] Error processing thumbnail for {thumb['video_id']}: {e}")
            continue

    # Sort by similarity descending
    matches.sort(key=lambda x: x["similarity"], reverse=True)
    return matches
