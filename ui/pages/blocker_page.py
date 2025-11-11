import os
import urllib.request
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QProgressBar
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QTextCursor
from resources.texts import BLOCKER_TEXT
from services.firewall import _run_powershell  # ✅ use your silent runner


class BlockerWorker(QThread):
    progress = Signal(str)
    finished = Signal(bool)

    def run(self):
        try:
            self.progress.emit("[blocker] Starting operation...")
            url = "https://content.hl2dm.org/spamfilter/RogueIPs.txt"

            with urllib.request.urlopen(url) as response:
                ips = [line.strip().decode("utf-8") for line in response if line.strip()]

            if not ips:
                self.progress.emit("[blocker] No IPs found in remote list.")
                self.finished.emit(False)
                return

            ip_list = ",".join(ips)
            self.progress.emit(f"[blocker] Loaded {len(ips)} IPs.")

            inbound_name = "INS2DOI_Block_All_IN"
            outbound_name = "INS2DOI_Block_All_OUT"

            # ✅ Remove old rules silently
            _run_powershell(f"Remove-NetFirewallRule -DisplayName '{inbound_name}' -ErrorAction SilentlyContinue")
            _run_powershell(f"Remove-NetFirewallRule -DisplayName '{outbound_name}' -ErrorAction SilentlyContinue")

            # ✅ Add single inbound rule
            _run_powershell(f"""
                New-NetFirewallRule -DisplayName '{inbound_name}' -Direction Inbound -Action Block `
                -RemoteAddress {ip_list} -Profile Any -Protocol Any
            """)

            # ✅ Add single outbound rule
            _run_powershell(f"""
                New-NetFirewallRule -DisplayName '{outbound_name}' -Direction Outbound -Action Block `
                -RemoteAddress {ip_list} -Profile Any -Protocol Any
            """)

            self.progress.emit("[blocker] Operation completed successfully with unified rules.")
            self.finished.emit(True)

        except Exception as e:
            self.progress.emit(f"[blocker] Error: {str(e)}")
            self.finished.emit(False)


class BlockerPage(QWidget):
    def __init__(self, back_cb=None):
        super().__init__()
        self.back_cb = back_cb
        self.worker = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # --- Description frame (from resources/texts.py) ---
        desc_box = QTextEdit()
        desc_box.setReadOnly(True)
        desc_box.setText(BLOCKER_TEXT)
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
        desc_box.setFixedHeight(300)
        layout.addWidget(desc_box)

        layout.setContentsMargins(10, 10, 10, 10)

        self.textbox = QTextEdit()
        self.textbox.setReadOnly(True)
        self.textbox.setStyleSheet(
            "background-color: black; color: #00FFAA; font-family: Consolas; font-size: 11pt;"
        )
        layout.addWidget(self.textbox)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.enable_btn = QPushButton("Enable Blocker")
        self.enable_btn.clicked.connect(self.handle_enable)
        self.enable_btn.setStyleSheet("background-color: #2c2c2c; color: #ffcc00; height: 26px;")
        layout.addWidget(self.enable_btn)

        self.back_btn = QPushButton("Back")
        self.back_btn.clicked.connect(self.back_cb)
        self.back_btn.setStyleSheet("background-color: #2c2c2c; color: white; height: 26px;")
        layout.addWidget(self.back_btn)

        self.setLayout(layout)

    def handle_enable(self):
        self.textbox.clear()
        self.append("[blocker] Starting...")
        self.progress.setValue(10)

        self.worker = BlockerWorker()
        self.worker.progress.connect(self.append)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def append(self, text):
        self.textbox.append(text)
        cursor = self.textbox.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.textbox.setTextCursor(cursor)
        self.textbox.ensureCursorVisible()

    def on_finished(self, success):
        self.progress.setValue(100 if success else 0)
        msg = "[blocker] Done." if success else "[blocker] Failed."
        self.append(msg)
