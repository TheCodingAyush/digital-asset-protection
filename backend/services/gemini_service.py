import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Load API key from environment variable and configure the client
_api_key = os.getenv("GEMINI_API_KEY")
if _api_key:
    genai.configure(api_key=_api_key)

# Use the gemini-1.5-flash model
_model = genai.GenerativeModel("gemini-2.0-flash")


def analyze_match(
    original_title: str,
    matched_title: str,
    similarity: float,
    source: str,
) -> dict:
    """
    Send a prompt to Gemini to analyze a potential media asset match and
    return structured infringement analysis.

    Args:
        original_title: Title of the original protected asset.
        matched_title:  Title of the matched (potentially infringing) asset.
        similarity:     Similarity score between 0.0 and 1.0.
        source:         Platform / source where the match was found.

    Returns:
        A dict with keys:
            - modification_type: str  (cropped/trimmed/filtered/reposted/unknown)
            - risk_level:        str  (high/medium/low/unknown)
            - recommendation:    str  (one-line action recommendation)
    """
    _fallback = {
        "modification_type": "unknown",
        "risk_level": "unknown",
        "recommendation": "Manual review required",
    }

    if not _api_key:
        return _fallback

    prompt = (
        f"Given an original media asset '{original_title}' was found matching "
        f"'{matched_title}' from {source} with {similarity:.0%} similarity, analyze:\n"
        "1. Likely modification type (cropped/trimmed/filtered/reposted/unknown)\n"
        "2. Infringement risk level (high/medium/low)\n"
        "3. One line recommendation\n"
        "Respond in JSON only:\n"
        '{"modification_type": "...", "risk_level": "...", "recommendation": "..."}'
    )

    try:
        response = _model.generate_content(prompt)
        raw_text = response.text.strip()

        # Strip optional markdown code fences if the model wraps the JSON
        if raw_text.startswith("```"):
            lines = raw_text.splitlines()
            # Remove opening fence (```json or ```) and closing fence (```)
            raw_text = "\n".join(
                line for line in lines if not line.strip().startswith("```")
            ).strip()

        result = json.loads(raw_text)

        # Validate expected keys are present
        return {
            "modification_type": str(result.get("modification_type", "unknown")),
            "risk_level": str(result.get("risk_level", "unknown")),
            "recommendation": str(result.get("recommendation", "Manual review required")),
        }

    except Exception as e:
        pass
        return _fallback
