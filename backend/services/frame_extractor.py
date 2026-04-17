"""
Frame Extractor Service

Extracts frames from video files at configurable intervals using OpenCV,
and loads single images using PIL. Returns standardized frame dictionaries
containing frame metadata and PIL Image objects.
"""

import cv2
import numpy as np
from PIL import Image
from typing import Optional


def extract_frames(video_path: str, interval_seconds: int = 5) -> list[dict]:
    """
    Extract frames from a video file at regular time intervals.

    Uses OpenCV to read the video and captures one frame every
    `interval_seconds` seconds. Each extracted frame is converted
    from OpenCV's BGR format to an RGB PIL Image.

    Args:
        video_path: Absolute or relative path to the video file.
        interval_seconds: Time gap (in seconds) between extracted frames.
                          Defaults to 5 seconds.

    Returns:
        A list of dicts, each containing:
            - frame_index (int): Sequential index of the extracted frame.
            - timestamp (float): Timestamp in seconds where the frame was captured.
            - image (PIL.Image.Image): The extracted frame as a PIL Image object.

        Returns an empty list if the video cannot be opened or read.

    Raises:
        No exceptions are raised; errors are handled gracefully and logged
        to stdout. Corrupt or unreadable videos return an empty list.
    """
    frames: list[dict] = []

    try:
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print(f"[frame_extractor] Error: Cannot open video file: {video_path}")
            return frames

        fps: float = cap.get(cv2.CAP_PROP_FPS)
        total_frame_count: int = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if fps <= 0:
            print(f"[frame_extractor] Error: Invalid FPS ({fps}) for video: {video_path}")
            cap.release()
            return frames

        duration_seconds: float = total_frame_count / fps
        frame_interval: int = int(fps * interval_seconds)

        if frame_interval <= 0:
            frame_interval = 1

        frame_index: int = 0
        current_frame_number: int = 0

        while current_frame_number < total_frame_count:
            # Seek to the target frame position
            cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_number)
            ret, frame = cap.read()

            if not ret:
                # Frame could not be read — skip and continue
                current_frame_number += frame_interval
                continue

            # Convert BGR (OpenCV default) to RGB for PIL
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)

            timestamp: float = round(current_frame_number / fps, 3)

            frames.append({
                "frame_index": frame_index,
                "timestamp": timestamp,
                "image": pil_image,
            })

            frame_index += 1
            current_frame_number += frame_interval

        cap.release()

    except cv2.error as e:
        print(f"[frame_extractor] OpenCV error processing '{video_path}': {e}")
    except Exception as e:
        print(f"[frame_extractor] Unexpected error processing '{video_path}': {e}")

    return frames


def extract_single_image(image_path: str) -> dict:
    """
    Load a single image file and return it in the same dict format
    used by extract_frames.

    Args:
        image_path: Absolute or relative path to the image file.

    Returns:
        A dict containing:
            - frame_index (int): Always 0.
            - timestamp (float): Always 0.0.
            - image (PIL.Image.Image): The loaded image as a PIL Image object.

    Raises:
        FileNotFoundError: If the image file does not exist.
        PIL.UnidentifiedImageError: If the file is not a valid image.
        Exception: Any other unexpected error during image loading.
    """
    try:
        image = Image.open(image_path)
        # Force-load pixel data so the file handle can be closed
        image.load()

        return {
            "frame_index": 0,
            "timestamp": 0.0,
            "image": image,
        }
    except FileNotFoundError:
        print(f"[frame_extractor] Error: Image file not found: {image_path}")
        raise
    except Exception as e:
        print(f"[frame_extractor] Error loading image '{image_path}': {e}")
        raise
