import base64
import hashlib
import zipfile
import tempfile
import os
import logging
from pathlib import Path

# Setup a module-level logger that writes to a file in the user's temp directory.
_log_dir = Path(tempfile.gettempdir()) / "ins2doi_patcher_logs"
_log_dir.mkdir(parents=True, exist_ok=True)
_log_file = _log_dir / "installer.log"

logger = logging.getLogger("ins2doi.utils")
if not logger.handlers:
    fh = logging.FileHandler(_log_file, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.setLevel(logging.INFO)

def decode_embedded_zip(b64_data: str, expected_sha256: str, label: str = "Patch"):
    """
    Decode base64-embedded zip data, verify its SHA-256, and write it to a temporary file.
    Returns the path to the temporary zip file.
    Raises ValueError on mismatch or decoding errors.
    """
    logger.info("Decoding %s...", label)
    try:
        raw = base64.b64decode(b64_data)
    except Exception as e:
        logger.exception("Base64 decoding failed for %s", label)
        raise

    sha = hashlib.sha256(raw).hexdigest()
    if sha != expected_sha256:
        logger.error("SHA-256 mismatch for %s. Expected %s, got %s", label, expected_sha256, sha)
        raise ValueError(f"SHA-256 mismatch for {label}! Expected: {expected_sha256}, Got: {sha}")

    # Use NamedTemporaryFile but close so other processes can read it on Windows.
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    try:
        temp_zip.write(raw)
        temp_zip.flush()
    finally:
        temp_zip.close()

    logger.info("%s verified (%d bytes) -> %s", label, len(raw), temp_zip.name)
    return temp_zip.name

def extract_zip(zip_path: str, target_dir: str):
    """
    Extract the given zip file to the target directory. Creates the target dir if missing.
    """
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    logger.info("Extracting %s to %s", os.path.basename(zip_path), str(target))
    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(str(target))
    except Exception:
        logger.exception("Failed to extract %s", zip_path)
        raise
    logger.info("Extraction complete: %s", str(target))
