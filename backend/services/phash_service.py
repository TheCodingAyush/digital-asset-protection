"""
Perceptual Hash (pHash) Service

Provides utilities for generating perceptual hashes from PIL Images
and comparing them to detect visually similar content. Uses the
imagehash library for hash computation.
"""

import imagehash
from PIL import Image

# Hamming distance threshold below which two images are considered similar.
SIMILARITY_THRESHOLD: int = 15


def generate_phash(image: Image.Image) -> str:
    """
    Generate a perceptual hash (pHash) for a given PIL Image.

    The perceptual hash is robust to minor visual changes such as
    resizing, compression artifacts, and slight color shifts, making
    it ideal for near-duplicate image detection.

    Args:
        image: A PIL Image object to hash.

    Returns:
        The perceptual hash as a hexadecimal string.
    """
    phash = imagehash.phash(image)
    return str(phash)


def compare_phash(hash1: str, hash2: str) -> dict:
    """
    Compare two perceptual hash strings and compute their similarity.

    The comparison uses Hamming distance — the number of differing bits
    between the two hashes. A lower distance indicates higher visual
    similarity.

    Args:
        hash1: First perceptual hash as a hexadecimal string.
        hash2: Second perceptual hash as a hexadecimal string.

    Returns:
        A dict containing:
            - distance (int): Hamming distance between the two hashes.
            - is_similar (bool): True if distance < SIMILARITY_THRESHOLD (15).
    """
    h1 = imagehash.hex_to_hash(hash1)
    h2 = imagehash.hex_to_hash(hash2)
    distance: int = h1 - h2

    return {
        "distance": distance,
        "is_similar": distance < SIMILARITY_THRESHOLD,
    }


def batch_compare_phash(query_hash: str, hash_list: list[str]) -> list[dict]:
    """
    Compare a query hash against a list of candidate hashes and return
    only the similar matches, sorted by distance ascending.

    Args:
        query_hash: The reference perceptual hash as a hexadecimal string.
        hash_list: A list of candidate perceptual hashes to compare against.

    Returns:
        A list of dicts for matches with distance < SIMILARITY_THRESHOLD (15),
        each containing:
            - hash (str): The candidate hash string.
            - distance (int): Hamming distance from the query hash.
            - index (int): Original index of this hash in hash_list.

        Results are sorted by distance in ascending order (most similar first).
    """
    query = imagehash.hex_to_hash(query_hash)
    matches: list[dict] = []

    for idx, candidate_hex in enumerate(hash_list):
        candidate = imagehash.hex_to_hash(candidate_hex)
        distance: int = query - candidate

        if distance < SIMILARITY_THRESHOLD:
            matches.append({
                "hash": candidate_hex,
                "distance": distance,
                "index": idx,
            })

    matches.sort(key=lambda m: m["distance"])
    return matches
