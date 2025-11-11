# services/resource_path.py
# -*- coding: utf-8 -*-
from pathlib import Path
import sys

def project_root() -> Path:
    """
    Returns the project root when running from source.
    Under PyInstaller, returns the temporary _MEIPASS directory.
    """
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return Path(base)
    # services/ -> project root is parent of parent?
    return Path(__file__).resolve().parents[1]

def resource_path(*parts: str) -> Path:
    """
    Build path to resources/assets/... supporting PyInstaller.
    """
    base = project_root()
    # In source: <root>/resources/...
    # In PyInstaller: we also bundle into resources/...
    return base.joinpath("resources", *parts)
