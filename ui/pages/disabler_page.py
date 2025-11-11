# ui/pages/disabler_page.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Callable, Optional, Dict
from pathlib import Path
import shutil
from resources.texts import DISABLER_TEXT
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QProgressBar,
    QHBoxLayout, QPushButton, QSizePolicy, QMessageBox
)

class DisablerPage(QWidget):
    """
    Merged: modern UI + legacy rename logic.
    Automatically loads scan results from Main Page and applies BattleEye disable step.
    """
    def __init__(self, back_cb: Optional[Callable[[], None]] = None, get_scan_results: Optional[Callable[[], dict]] = None):
        super().__init__()
        self.go_home = back_cb
        self.get_scan_results = get_scan_results or (lambda: {})
        self.found_games: Dict[str, Dict[str, Path]] = {}

        # --- UI Setup ---
        layout = QVBoxLayout(self)
        # Description frame (from resources/texts.py)
        desc_box = QTextEdit()
        desc_box.setReadOnly(True)
        desc_box.setText(DISABLER_TEXT)
        desc_box.setStyleSheet("""
            QTextEdit {
                background-color: #111;
                border: 1px solid #444;
                color: #ccc;
                font-family: Consolas;
                font-size: 12px;
                padding: 6px;
            }
        """)
        desc_box.setFixedHeight(200)
        layout.addWidget(desc_box)
        title = QLabel("Disabler")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")
        layout.addWidget(title)

        subtitle = QLabel("Scan from Home first — detected games are auto-loaded here.")
        subtitle.setStyleSheet("color: gray;")
        layout.addWidget(subtitle)

        self.textbox = QTextEdit(self)
        self.textbox.setReadOnly(True)
        self.textbox.setAcceptRichText(False)
        self.textbox.setLineWrapMode(QTextEdit.NoWrap)
        self.textbox.setStyleSheet("background-color: #111; color: cyan; font-family: Consolas;")
        layout.addWidget(self.textbox)

        self.progress = QProgressBar(self)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        # Buttons
        btn_layout = QHBoxLayout()
        self.disable_button = QPushButton("Disable BattleEye", self)
        self.disable_button.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold;")
        self.disable_button.clicked.connect(self.on_disable_clicked)
        btn_layout.addWidget(self.disable_button)

        self.back_button = QPushButton("Back", self)
        self.back_button.clicked.connect(self.go_home)
        btn_layout.addWidget(self.back_button)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self._refresh_from_scan()

    # ---------- Utility ----------
    def append(self, text: str):
        self.textbox.append(text)
        cursor = self.textbox.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.textbox.setTextCursor(cursor)

    # ---------- Load scan results ----------
    def _refresh_from_scan(self):
        self.textbox.clear()
        self.progress.setValue(0)
        self.found_games.clear()

        results = self.get_scan_results()
        fg = results.get("found_games", {}) if results else {}

        if not fg:
            self.append("⚠️ No scan data found — please scan first.")
            return

        self.append("[disabler] Loading scan results...")
        for game, path in fg.items():
            path = Path(path)
            if not path.exists():
                continue

            # Detect expected exe names
            if "dayofinfamy" in str(path).lower():
                source_exe = path / "dayofinfamy_x64.exe"
            elif "insurgency" in str(path).lower():
                source_exe = path / "insurgency_x64.exe"
            else:
                continue

            self.found_games[game] = {"path": path, "source_exe": source_exe}
            self.append(f"• {game} detected at {path}")

        if not self.found_games:
            self.append("⚠️ No valid games with source_exe found.")
        else:
            self.append("Paths loaded. Click 'Disable BattleEye' to apply.")

    # ---------- Disable BattleEye ----------
    def on_disable_clicked(self):
        if not self.found_games:
            QMessageBox.information(self, "Info", "No valid game executables found. Run scan first.")
            return

        total = len(self.found_games)
        self.append("Starting disable process...")
        self.progress.setValue(0)

        for i, (game_key, info) in enumerate(self.found_games.items(), start=1):
            source_exe = info["source_exe"]
            if not source_exe.exists():
                self.append(f"⚠️ Missing executable for {game_key}: {source_exe}")
                continue

            dest_exe = Path(str(source_exe).replace("_x64", "_BE"))
            disabled_exe = Path(str(source_exe).replace("_x64", "_BE_disabled"))

            try:
                # If BE version exists, back it up
                if dest_exe.exists():
                    if not disabled_exe.exists():
                        dest_exe.rename(disabled_exe)
                        self.append(f"Backed up {dest_exe.name} → {disabled_exe.name}")
                    else:
                        if dest_exe.is_file():
                            dest_exe.unlink()
                        self.append(f"Removed old {dest_exe.name}")

                shutil.copy2(source_exe, dest_exe)
                self.append(f"✅ {game_key}: created {dest_exe.name}")

            except Exception as e:
                self.append(f"❌ Error while disabling {game_key}: {e}")

            self.progress.setValue(int(100 * i / total))

        self.append("Disable process completed.")
        QMessageBox.information(self, "Completed", "BattleEye disable completed.")
