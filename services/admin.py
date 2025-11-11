# services/admin.py
# -*- coding: utf-8 -*-
import os
import ctypes

def is_admin() -> bool:
    """Return True if process has admin privileges (Windows), else False."""
    if os.name != "nt":
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False
