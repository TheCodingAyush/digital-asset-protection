"""
File Handler Utilities

Provides helper functions for saving uploaded files to disk with
unique filenames and safely cleaning up temporary files.
"""

import os
import uuid
import shutil


def save_upload(file, destination_folder: str) -> str:
    """
    Save an uploaded file to the specified destination folder with a
    unique filename generated via UUID to prevent collisions.

    The original file extension is preserved. The destination folder
    is created automatically if it does not already exist.

    Args:
        file: A file-like object with `filename` and `file` attributes
              (e.g., FastAPI's UploadFile).
        destination_folder: Directory path where the file should be saved.

    Returns:
        The full absolute path to the saved file.
    """
    os.makedirs(destination_folder, exist_ok=True)

    # Preserve original extension
    original_extension = os.path.splitext(file.filename)[1] if file.filename else ""
    unique_filename = f"{uuid.uuid4().hex}{original_extension}"
    file_path = os.path.join(destination_folder, unique_filename)

    # Write the uploaded file contents to disk
    with open(file_path, "wb") as dest:
        # If the file object supports read() (e.g., SpooledTemporaryFile),
        # read in chunks to handle large files efficiently.
        if hasattr(file, "file"):
            shutil.copyfileobj(file.file, dest)
        else:
            shutil.copyfileobj(file, dest)

    return file_path


def cleanup_file(file_path: str) -> None:
    """
    Safely delete a file from disk.

    If the file does not exist, the error is silently ignored.
    Other OS-level errors (e.g., permission denied) are re-raised.

    Args:
        file_path: Path to the file to delete.
    """
    try:
        os.remove(file_path)
    except FileNotFoundError:
        # File already gone — nothing to do
        pass
