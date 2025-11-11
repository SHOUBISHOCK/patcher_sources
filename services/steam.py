# services/steam.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import os
import re
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger("services.steam")

def _get_registry_value(root, path: str, name: str) -> Optional[str]:
    """Read REG_SZ from Windows registry."""
    if os.name != "nt":
        return None
    try:
        import winreg  # type: ignore
        key = winreg.OpenKey(root, path)
        val, _ = winreg.QueryValueEx(key, name)
        winreg.CloseKey(key)
        return val
    except Exception:
        return None

def find_steam_base_paths() -> List[Path]:
    """
    Discover Steam base installations via registry and common locations.
    Returns unique existing Paths.
    """
    logger.debug("find_steam_base_paths()")
    paths: List[Path] = []

    if os.name == "nt":
        try:
            import winreg  # type: ignore
            sp = _get_registry_value(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamPath")
            if sp:
                p = Path(sp)
                if p.exists():
                    paths.append(p)
                    logger.debug("SteamPath registry: %s", p)
        except Exception:
            logger.exception("Registry lookup for SteamPath failed")

    # Heuristics
    for p in [
        Path(r"C:\Program Files (x86)\Steam"),
        Path(r"C:\Program Files\Steam"),
        Path(r"D:\SteamLibrary"),
        Path(r"E:\SteamLibrary"),
    ]:
        try:
            if p.exists():
                paths.append(p)
                logger.debug("Heuristic path: %s", p)
        except Exception:
            pass

    # De-dup by resolved string
    uniq: List[Path] = []
    seen = set()
    for p in paths:
        try:
            key = str(p.resolve())
        except Exception:
            key = str(p)
        if key not in seen:
            uniq.append(p)
            seen.add(key)
    logger.debug("find_steam_base_paths() -> %d", len(uniq))
    return uniq

def parse_libraryfolders_vdf(vdf_path: Path) -> List[Path]:
    """
    Very small parser: extracts library 'path' entries from libraryfolders.vdf.
    """
    logger.debug("parse_libraryfolders_vdf(%s)", vdf_path)
    libs: List[Path] = []
    try:
        text = vdf_path.read_text(encoding="utf-8", errors="ignore")
        # Matches: "N" { ... "path" "X:\SteamLibrary" ... }
        pattern = r'"\d+"\s*{\s*[^}]*?"path"\s*"([^"]+)"'
        matches = list(re.finditer(pattern, text, re.IGNORECASE | re.DOTALL))
        for m in matches:
            path = m.group(1).replace("\\\\", "\\")
            p = Path(path)
            try:
                if p.exists():
                    libs.append(p)
                    logger.debug("VDF library path: %s", p)
            except Exception:
                pass
    except re.error:
        logger.exception("Regex error while parsing %s", vdf_path)
    except Exception:
        logger.exception("Failed to parse %s", vdf_path)
    return libs

def find_steam_common_dirs() -> List[Path]:
    """
    Returns candidate '<library>/steamapps/common' directories from all known libraries.
    """
    commons: List[Path] = []
    try:
        bases = find_steam_base_paths()
        for base in bases:
            sa = base / "steamapps"
            if sa.exists():
                commons.append(sa / "common")
            vdf = sa / "libraryfolders.vdf"
            if vdf.exists():
                for lib in parse_libraryfolders_vdf(vdf):
                    sa2 = lib / "steamapps"
                    if sa2.exists():
                        commons.append(sa2 / "common")
    except Exception:
        logger.exception("find_steam_common_dirs() unexpected error")

    # unique + existing
    uniq: List[Path] = []
    seen = set()
    for c in commons:
        try:
            if c.exists():
                key = str(c.resolve())
            else:
                continue
        except Exception:
            key = str(c)
        if key not in seen:
            uniq.append(c)
            seen.add(key)
    logger.debug("find_steam_common_dirs() -> %d", len(uniq))
    return uniq

def auto_detect_game_dir(game_folder_name: str) -> Optional[Path]:
    """Try to locate '<library>/steamapps/common/<game_folder_name>'."""
    try:
        for common in find_steam_common_dirs():
            candidate = common / game_folder_name
            if candidate.exists() and candidate.is_dir():
                return candidate
    except Exception:
        logger.exception("auto_detect_game_dir(%r) failed", game_folder_name)
    return None
