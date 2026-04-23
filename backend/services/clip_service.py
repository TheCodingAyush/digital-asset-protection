"""
CLIP Embedding Service

Provides image embedding generation and similarity comparison using
OpenAI's CLIP (ViT-B/32) model via HuggingFace Transformers. The model
is lazily loaded on first use and cached globally for subsequent calls.
"""

import numpy as np
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

# ---------------------------------------------------------------------------
# Global model cache — populated on first call to load_clip_model()
# ---------------------------------------------------------------------------
_model: CLIPModel | None = None
_processor: CLIPProcessor | None = None

# HuggingFace model identifier
_MODEL_ID: str = "openai/clip-vit-base-patch32"

# Minimum cosine similarity to consider two images a match
SIMILARITY_THRESHOLD: float = 0.85


def load_clip_model() -> tuple:
    """
    Load the CLIP model and processor onto CPU, caching them globally
    so subsequent calls return the already-loaded instances.

    The model is downloaded from HuggingFace on the first invocation
    and kept in memory for the lifetime of the process.

    Returns:
        A tuple of (CLIPModel, CLIPProcessor).
    """
    global _model, _processor

    if _model is None or _processor is None:
        print(f"[clip_service] Loading CLIP model '{_MODEL_ID}' on CPU …")
        _model = CLIPModel.from_pretrained(_MODEL_ID)
        _processor = CLIPProcessor.from_pretrained(_MODEL_ID)
        _model.eval()  # inference-only mode
        print("[clip_service] CLIP model loaded successfully.")

    return _model, _processor


def generate_embedding(image: Image.Image) -> list[float]:
    """
    Generate a normalised CLIP image embedding for a given PIL Image.

    The embedding is L2-normalised so that cosine similarity can be
    computed via a simple dot product.

    Args:
        image: A PIL Image object (any mode — will be converted internally).

    Returns:
        A list of floats representing the normalised embedding vector.
    """
    model, processor = load_clip_model()

    # Ensure RGB (CLIP expects 3-channel input)
    if image.mode != "RGB":
        image = image.convert("RGB")

    inputs = processor(images=image, return_tensors="pt")

    # Run inference without gradient tracking
    import torch
    with torch.no_grad():
        outputs = model.get_image_features(**inputs)

    # Convert to numpy and L2-normalise
    embedding = outputs.pooler_output.squeeze().tolist()
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm

    return embedding.tolist()


def cosine_similarity(emb1: list[float], emb2: list[float]) -> float:
    """
    Compute the cosine similarity between two embedding vectors.

    Both vectors are expected to be the same length. If either vector
    has zero magnitude the function returns 0.0.

    Args:
        emb1: First embedding as a list of floats.
        emb2: Second embedding as a list of floats.

    Returns:
        A float in the range [0, 1] representing cosine similarity.
        Values closer to 1 indicate higher visual similarity.
    """
    a = np.array(emb1, dtype=np.float32)
    b = np.array(emb2, dtype=np.float32)

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    similarity = float(np.dot(a, b) / (norm_a * norm_b))

    # Clamp to [0, 1] to guard against floating-point drift
    return max(0.0, min(1.0, similarity))


def batch_compare_clip(
    query_embedding: list[float],
    embedding_list: list[list[float]],
) -> list[dict]:
    """
    Compare a query embedding against a list of candidate embeddings
    and return only those exceeding the similarity threshold.

    Args:
        query_embedding: The reference embedding as a list of floats.
        embedding_list: A list of candidate embeddings to compare against.

    Returns:
        A list of dicts for matches with similarity > SIMILARITY_THRESHOLD
        (0.85), each containing:
            - index (int): Original index of the candidate in embedding_list.
            - similarity (float): Cosine similarity score.

        Results are sorted by similarity in descending order (best match first).
    """
    query = np.array(query_embedding, dtype=np.float32)
    norm_q = np.linalg.norm(query)

    if norm_q == 0:
        return []

    matches: list[dict] = []

    for idx, candidate in enumerate(embedding_list):
        cand = np.array(candidate, dtype=np.float32)
        norm_c = np.linalg.norm(cand)

        if norm_c == 0:
            continue

        sim = float(np.dot(query, cand) / (norm_q * norm_c))
        sim = max(0.0, min(1.0, sim))

        if sim > SIMILARITY_THRESHOLD:
            matches.append({
                "index": idx,
                "similarity": round(sim, 6),
            })

    matches.sort(key=lambda m: m["similarity"], reverse=True)
    return matches
