import os
import traceback
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLabel, QProgressBar, QMessageBox
)
from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QTextCursor
from workers.scan_worker import ScanWorker
from resources.texts import MAIN_TEXT
import webbrowser  # Add at the very top of the file (if missing)


class MainPage(QWidget):
    def __init__(self, go_patcher, go_disabler, go_blocker, go_home, set_scan_results=None):
        super().__init__()
        self.go_patcher = go_patcher
        self.go_disabler = go_disabler
        self.go_blocker = go_blocker
        self.go_home = go_home
        self.set_scan_results = set_scan_results

        self.scan_results = {}
        self.thread = None
        self.worker = None
        self._scanning = False

        self.init_ui()

    # ---------------------------------------------------------
    # UI Setup
    # ---------------------------------------------------------
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        title = QLabel("INS2DOI Community Patcher")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFD700;")
        layout.addWidget(title)

        subtitle = QLabel("⚠️ Please run as Administrator")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: orange;")
        layout.addWidget(subtitle)

        # Intro text from resources
        self.desc_box = QTextEdit()
        self.desc_box.setReadOnly(True)
        self.desc_box.setPlainText(MAIN_TEXT)
        self.desc_box.setFixedHeight(140)
        self.desc_box.setStyleSheet(
            "background-color:#111; color:#ccc; font-family:Consolas; "
            "font-size:12px; border:1px solid #555; padding:4px;"
        )
        layout.addWidget(self.desc_box)

        # Log area
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("background-color: #000; color: #00FFAA; font-family: Consolas; font-size: 12px;")
        layout.addWidget(self.log)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        # Button row
        btn_layout = QHBoxLayout()
        self.btn_scan = QPushButton("Start Scan")
        self.btn_scan.clicked.connect(self.handle_scan)
        btn_layout.addWidget(self.btn_scan)

        self.btn_patcher = QPushButton("Open Patcher")
        self.btn_patcher.clicked.connect(self.go_patcher)
        btn_layout.addWidget(self.btn_patcher)

        self.btn_disabler = QPushButton("Open Disabler")
        self.btn_disabler.clicked.connect(self.go_disabler)
        btn_layout.addWidget(self.btn_disabler)

        self.btn_blocker = QPushButton("Open Server Spam Blocker")
        self.btn_blocker.clicked.connect(self.go_blocker)
        btn_layout.addWidget(self.btn_blocker)

        self.btn_exit = QPushButton("Exit")
        self.btn_exit.clicked.connect(self.close_app)
        btn_layout.addWidget(self.btn_exit)
        layout.addLayout(btn_layout)

        # Bottom
        bottom_layout = QHBoxLayout()
        self.btn_credits = QPushButton("Credits")
        self.btn_credits.clicked.connect(self.show_credits)
        bottom_layout.addWidget(self.btn_credits)

        self.btn_support = QPushButton("💖 Support Us")
        self.btn_support.clicked.connect(self.show_support)
        bottom_layout.addWidget(self.btn_support)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

    # ---------------------------------------------------------
    # Utility
    # ---------------------------------------------------------
    def append_log(self, text: str):
        cursor = self.log.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log.setTextCursor(cursor)
        self.log.insertPlainText(text + "\n")
        self.log.ensureCursorVisible()

    def close_app(self):
        os._exit(0)

    def show_credits(self):
        QMessageBox.information(
            self,
            "CREDITS",
            (
                "CREDITS:\n"
                "DeltaMike (contributor)\n"
                "ChrisTX (coder tips)\n"
                "SHOUBI (publishing)\n"
                "OnSync (.bat installers clarification)\n"
                "Rafai (original workaround idea)\n"
                "Bouncy-Henky‼ (spam filter web server)\n"
                "E.G.Cage (all in one patcher coding)\n"
            ),
        )

    def show_support(self):
        # Open website directly when button is pressed
        webbrowser.open("https://mygamingedge.online/")
        self.append_log("\n💖 Redirecting to support page: https://mygamingedge.online/\n")



    # ---------------------------------------------------------
    # Scan logic
    # ---------------------------------------------------------
    def handle_scan(self):
        """Run the scan safely without reusing deleted threads."""
        if self._scanning:
            self.append_log("[warn] Scan already running. Please wait...")
            return

        try:
            self.log.clear()
            self.progress.setValue(0)
            self.append_log("🟢 Starting scan...")

            # Build game definitions
            games = {
                "Insurgency 2": {"Folder": "insurgency2", "exe": "insurgency.exe"},
                "Day of Infamy": {"Folder": "dayofinfamy", "exe": "dayofinfamy.exe"},
            }

            # Thread setup
            self.thread = QThread()
            self.worker = ScanWorker(games)
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.run)
            self.worker.log.connect(self.append_log)
            self.worker.progress.connect(self.progress.setValue)
            self.worker.finished.connect(self._on_scan_finished)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self._on_thread_cleanup)
            self.thread.finished.connect(self.thread.deleteLater)

            self._scanning = True
            self.thread.start()

        except Exception as e:
            traceback.print_exc()
            self.append_log(f"❌ Scan failed to start: {e}")

    def _on_thread_cleanup(self):
        self._scanning = False
        self.thread = None
        self.worker = None
        self.append_log("[info] Scan thread cleaned up.\n")

    def _on_scan_finished(self, results):
        """Handle scan completion."""
        self.scan_results = results
        self.progress.setValue(100)

        if callable(self.set_scan_results):
            self.set_scan_results(results)

        if results.get("found_games"):
            found = ", ".join(results["found_games"].keys())
            self.append_log(f"✅ Found games: {found}")
        else:
            self.append_log("⚠️ No supported games detected.")
        self.append_log("Scan complete.")

    def get_scan_results(self):
        return self.scan_results
