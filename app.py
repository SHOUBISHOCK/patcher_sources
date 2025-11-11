# app.py
# -*- coding: utf-8 -*-
import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.main_window import MainWindow

from installer.utils import decode_embedded_zip, extract_zip
from installer import embedded_ins_patch, embedded_doi_patch


def _hide_console_window():
    if os.name == "nt":
        try:
            import ctypes
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 0)
        except Exception:
            pass


def apply_patches():
    """
    Decode and extract the embedded patches to ~/Desktop/patch_output.
    This should be called manually from the GUI, not on startup.
    """
    base_dir = os.path.expanduser("~/Desktop/patch_output")
    os.makedirs(base_dir, exist_ok=True)

    ins_zip = decode_embedded_zip(
        embedded_ins_patch.BASE64_DATA, embedded_ins_patch.SHA256, "Insurgency Patch"
    )
    doi_zip = decode_embedded_zip(
        embedded_doi_patch.BASE64_DATA, embedded_doi_patch.SHA256, "Day of Infamy Patch"
    )

    extract_zip(ins_zip, os.path.join(base_dir, "ins_patch"))
    extract_zip(doi_zip, os.path.join(base_dir, "doi_patch"))

    # Cleanup
    os.unlink(ins_zip)
    os.unlink(doi_zip)


def main():
    _hide_console_window()
    app = QApplication(sys.argv)

    ICON_FILENAME = "INS2DOI Community Patcher.ico"
    base_dir = Path(sys._MEIPASS) if getattr(sys, "frozen", False) else Path(__file__).resolve().parent

    icon_path = base_dir / ICON_FILENAME
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
