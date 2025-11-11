# ui/pages/patcher_page.py
# -*- coding: utf-8 -*-
from typing import Optional, Callable, Dict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QTextEdit, QHBoxLayout
)
from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QTextCursor
from pathlib import Path
from resources.texts import PATCHER_TEXT
from PySide6.QtWidgets import QProgressBar
from PySide6.QtCore import Slot



# Try importing legacy patcher worker
try:
    from workers.patcher_worker import PatcherWorker
    HAS_REAL_PATCHER = True
except Exception:
    PatcherWorker = None
    HAS_REAL_PATCHER = False


class PatcherPage(QWidget):
    """
    Modern patcher page with integrated log and auto-refresh of scan results.
    """
    def __init__(
        self,
        go_home: Optional[Callable[[], None]] = None,
        back_cb: Optional[Callable[[], None]] = None,
        get_scan_results: Optional[Callable[[], dict]] = None,
    ):
        super().__init__()
        self.go_home = go_home or back_cb
        self.get_scan_results_cb = get_scan_results
        self.scan_results: Dict = {}
        self.thread: Optional[QThread] = None
        self.worker = None

        # ----- UI -----
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # Description frame (from resources/texts.py)
        desc_box = QTextEdit()
        desc_box.setReadOnly(True)
        desc_box.setText(PATCHER_TEXT)
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

        # --- Progress bar (Patcher page) -------------------------------------------
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)                # show percentage text
        self.progress.setFixedHeight(12)                  # thin height like other pages
        # Styling: thin grey track, light-blue chunk
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #2b2b2b;
                background-color: #111;
                text-align: center;
                color: #a7e1ff;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8fe4ff, stop:1 #3bbcf0);
                border-radius: 4px;
            }
        """)
        # ---------------------------------------------------------------------------
        title = QLabel("🧩 Patcher")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setFixedHeight(300)
        self.log.setStyleSheet("background:#0c0c0c; color:#00ff99; font-family: Consolas; font-size: 12px;")
        layout.addWidget(self.log)

        layout.addWidget(self.progress)

        row = QHBoxLayout()
        self.btn_apply = QPushButton("Apply Patch (auto for detected)")
        self.btn_apply.clicked.connect(self.apply_patch)
        row.addWidget(self.btn_apply)

        self.btn_back = QPushButton("⬅ Back")
        self.btn_back.clicked.connect(self.handle_back)
        row.addWidget(self.btn_back)

        layout.addLayout(row)

        self.setLayout(layout)

    # ===== UTILITIES =====
    def append_log(self, text: str):
        """Append log text and scroll automatically."""
        if not text:
            return
        self.log.moveCursor(QTextCursor.End)
        self.log.insertPlainText(text.strip() + "\n")
        self.log.moveCursor(QTextCursor.End)
        self.log.ensureCursorVisible()

    # ===== SCAN RESULTS =====
    def set_scan_results(self, results: Dict = None):
        """Receive updated scan results from MainWindow."""
        self.scan_results = results or {}
        self.append_log("[patcher] Scan results loaded.")
        self.show_detected_games()

    def _get_scan_results(self) -> Dict:
        if self.scan_results:
            return self.scan_results
        if callable(self.get_scan_results_cb):
            try:
                return self.get_scan_results_cb() or {}
            except Exception:
                pass
        win = self.window()
        if hasattr(win, "get_scan_results"):
            try:
                return win.get_scan_results() or {}
            except Exception:
                pass
        return {}

    # ===== LOG DISPLAY =====
    def show_detected_games(self):
        """Show all found games in the log, preserving previous output."""
        results = self._get_scan_results()
        found = results.get("found_games", {}) if isinstance(results, dict) else {}
        self.append_log("\n[patcher] Detected games:")
        if not found:
            self.append_log("⚠️ No detected games. Please run a scan first.")
            return
        for name, info in found.items():
            path = info.get("path") if isinstance(info, dict) else info
            exe = info.get("source_exe") if isinstance(info, dict) else info.get("exe") if isinstance(info, dict) else None
            exe_name = exe.name if exe else ""
            self.append_log(f"• {name}: {path} (exe: {exe_name})")

    # ===== PATCH ACTION =====
    def apply_patch(self):
        """Instantly start patching all detected games using PatcherWorker."""
        results = self._get_scan_results()
        found = results.get("found_games", {}) if isinstance(results, dict) else {}

        if not found:
            QMessageBox.information(self, "Info", "No supported games detected. Please run the scan first.")
            return

        if not HAS_REAL_PATCHER or not PatcherWorker:
            QMessageBox.warning(
                self,
                "Missing Backend",
                "PatcherWorker not found. Please ensure workers/patcher_worker.py exists."
            )
            return

        # Prevent multiple runs
        self.btn_apply.setEnabled(False)
        self.append_log("⚙️ Starting patcher worker...")

        try:
            self.thread = QThread()
            self.worker = PatcherWorker(found)
            self.worker.moveToThread(self.thread)

            # Connect worker signals
            if hasattr(self.worker, "log"):
                self.worker.log.connect(self.append_log)
            if hasattr(self.worker, "progress"):
                self.worker.progress.connect(self._on_patch_progress)
            if hasattr(self.worker, "finished"):
                self.worker.finished.connect(self._on_patcher_finished)
                self.worker.finished.connect(self.thread.quit)
                self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.started.connect(self.worker.run)
            self.thread.start()

        except Exception as e:
            self.append_log(f"❌ Could not start patcher worker: {e}")
            self.btn_apply.setEnabled(True)

    def _on_patcher_finished(self, summary=None):
        """Handle worker completion."""
        if summary:
            self.append_log(f"[patcher] Finished: {summary}")
        else:
            self.append_log("[patcher] Finished.")
        try:
            if self.thread:
                self.thread.quit()
                self.thread.wait()
        except Exception:
            pass
        self.thread = None
        self.worker = None
        self.btn_apply.setEnabled(True)
        self.append_log("✅ All patching operations completed.")

        # Instead of clearing, append updated list to show new detection results
        self.append_log("\n[patcher] Auto-refreshing detected games...")
        self.show_detected_games()

    # ===== NAVIGATION =====
    def handle_back(self):
        if callable(self.go_home):
            self.go_home()
        else:
            win = self.window()
            if hasattr(win, "stack") and hasattr(win, "main_page"):
                win.stack.setCurrentWidget(win.main_page)

    # ===== AUTO-REFRESH HOOK =====
    def showEvent(self, event):
        """Automatically refresh detected games whenever the page is shown."""
        self.show_detected_games()
        super().showEvent(event)

    @Slot(int)
    def _on_patch_progress(self, value: int):
        try:
            v = max(0, min(100, int(value)))
            self.progress.setValue(v)
        except Exception:
            pass

