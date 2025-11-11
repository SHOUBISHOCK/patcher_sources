# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_submodules

# --- automatic recursive data collection ---
def collect_all_subdirs(base_dir: str):
    """Recursively include all non-hidden subdirectories for PyInstaller."""
    datas = []
    for root, dirs, files in os.walk(base_dir):
        # Skip hidden/system folders and __pycache__
        if any(p.startswith('.') or p == '__pycache__' for p in root.split(os.sep)):
            continue
        rel_path = os.path.relpath(root, base_dir)
        if rel_path == '.':
            continue
        datas.append((root, rel_path))
    return datas


# Use current working directory instead of __file__
project_root = os.getcwd()

# Collect all folders recursively (ui, installer, workers, core, services, etc.)
all_datas = collect_all_subdirs(project_root)

# Automatically gather all PySide6 submodules
hidden_pyside = collect_submodules('PySide6')

# --- PyInstaller build specification ---
block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=all_datas + [
        ('INS2DOI Community Patcher.ico', '.'),
    ],
    hiddenimports=hidden_pyside,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='INS2DOI_Community_Patcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Hide console window
    base="Win32GUI",
    windowed=True,   # <— explicitly enforces GUI-only
    icon='INS2DOI Community Patcher.ico',
)
