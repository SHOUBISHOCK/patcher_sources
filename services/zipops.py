# services/zipops.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import hashlib
import shutil
import time
import zipfile
from pathlib import Path
from typing import Callable

def is_within_directory(base_dir: Path, target: Path) -> bool:
    try:
        base = base_dir.resolve(strict=False)
        targ = target.resolve(strict=False)
    except Exception:
        base = base_dir
        targ = target
    return str(targ).startswith(str(base))

def compute_sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def safe_extract_zip(
    zip_path: Path,
    dest_dir: Path,
    progress_cb: Callable[[int], None],
    log_cb: Callable[[str], None],
    backup_dir: Path,
) -> None:
    """
    Safe ZIP extraction with directory traversal protection and automatic backups.
    """
    with zipfile.ZipFile(zip_path, "r") as zf:
        members = sorted(zf.infolist(), key=lambda i: i.filename)
        total = max(1, len(members))
        done = 0
        for m in members:
            if m.is_dir():
                target_dir = dest_dir / m.filename
                if not is_within_directory(dest_dir, target_dir):
                    raise Exception(f"Unsafe path in ZIP (dir): {m.filename}")
                target_dir.mkdir(parents=True, exist_ok=True)
                log_cb(f"[DIR] {m.filename}")
            else:
                target_file = dest_dir / m.filename
                if not is_within_directory(dest_dir, target_file.parent):
                    raise Exception(f"Unsafe path in ZIP (file): {m.filename}")
                target_file.parent.mkdir(parents=True, exist_ok=True)
                if target_file.exists():
                    rel = target_file.relative_to(dest_dir)
                    backup_path = backup_dir / rel
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(target_file, backup_path)
                    log_cb(f"[BACKUP] {rel}")
                with zf.open(m, "r") as src, open(target_file, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                log_cb(f"[WRITE] {m.filename}")
            done += 1
            progress_cb(int(100 * done / total))
            time.sleep(0.002)
