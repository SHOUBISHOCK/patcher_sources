from typing import Dict, Optional
import base64
import tempfile
from pathlib import Path
import sys

# -------------------- Embedded ZIP placeholders --------------------

# Map: game key -> steam folder name
GAME_FOLDERS = {
    "dayofinfamy": "dayofinfamy",
    "insurgency2": "insurgency2",
}

# Mapping between patcher keys and human titles (for shared scan results)
GKEY_TO_TITLE = {
    "dayofinfamy": "Day of Infamy",
    "insurgency2": "Insurgency 2",
}

# Replace with your actual base64 strings and SHA-256 values (hex, lowercase)
ZIP_DOI_B64 = ""  
ZIP_DOI_SHA256 = ""  

ZIP_INS_B64 = ""
ZIP_INS_SHA256 = ""

EMBEDDED_ZIPS: Dict[str, Dict[str, str]] = {
    "dayofinfamy": {"b64": ZIP_DOI_B64, "sha256": ZIP_DOI_SHA256, "name": "doi_patch.zip"},
    "insurgency2": {"b64": ZIP_INS_B64, "sha256": ZIP_INS_SHA256, "name": "ins_patch.zip"},
}

def get_embedded_zip_path(game_key: str) -> Optional[Path]:
    """
    Decode embedded base64 ZIP to a temp file and verify SHA-256 (if provided).
    Returns path or None if no embedded ZIP.
    """
    meta = EMBEDDED_ZIPS.get(game_key)
    if not meta or not meta.get("b64"):
        return None
    data = base64.b64decode(meta["b64"])
    tmp = Path(tempfile.gettempdir()) / f"{meta.get('name', game_key)}"
    with open(tmp, "wb") as f:
        f.write(data)
    expected = (meta.get("sha256") or "").strip().lower()
    if expected:
        got = compute_sha256(tmp)
        if got != expected:
            raise Exception(f"ZIP SHA-256 mismatch: expected {expected}, got {got}")
    return tmp

def get_bundled_zip_path(game_key: str) -> Optional[Path]:
    """
    If you bundle with --add-data, look for the ZIP under assets/.
    """
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    name = EMBEDDED_ZIPS.get(game_key, {}).get("name") or f"{game_key}.zip"
    candidate = base / "assets" / name
    return candidate if candidate.exists() else None