# workers/blocker_worker.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import os
import tempfile
from pathlib import Path
from PySide6.QtCore import QObject, Signal
from services.firewall import remove_rules, add_block_rules_from_ip_file, verify_rules_exist
from services.admin import is_admin
import urllib.request


class BlockerWorker(QObject):
    progress = Signal(int)        # emits progress percentage (0–100)
    log = Signal(str)             # emits log text for GUI
    done = Signal(bool, str)      # emits (success, message) when finished

    def __init__(self, url: str = "https://content.hl2dm.org/spamfilter/RogueIPs.txt"):
        super().__init__()
        self.url = url

    def run(self):
        """Main installation/update process for Fast Path Blocker."""
        if os.name != "nt":
            self.done.emit(False, "Windows only.")
            return

        try:
            # --------------------------
            # 1. Check for admin rights
            # --------------------------
            if not is_admin():
                raise PermissionError("Administrator privileges required.")

            # --------------------------
            # 2. Download IP list
            # --------------------------
            self.progress.emit(5)
            self.log.emit("🌐 Downloading Rogue IP list …")

            with urllib.request.urlopen(self.url, timeout=30) as r:
                content = r.read().decode("utf-8", errors="ignore")

            ips = [
                ln.strip()
                for ln in content.splitlines()
                if ln.strip() and not ln.strip().startswith("#")
            ]
            if not ips:
                raise Exception("Empty IP list from server.")

            self.progress.emit(25)
            self.log.emit(f"✅ Loaded {len(ips)} IPs.")

            # --------------------------
            # 3. Save to temporary file
            # --------------------------
            tmp_list = Path(tempfile.gettempdir()) / "rogue_ips.txt"
            tmp_list.write_text("\n".join(ips), encoding="utf-8")

            # --------------------------
            # 4. Remove old rules
            # --------------------------
            self.log.emit("🧹 Removing old firewall rules …")
            remove_rules("GameSpamFilter")

            # --------------------------
            # 5. Add new rules with progress callback
            # --------------------------
            self.progress.emit(45)
            self.log.emit("⚙️ Adding new firewall rules …")

            def on_progress(percent: int, message: str):
                # forward from firewall.py callback to GUI
                self.progress.emit(percent)
                if message:
                    self.log.emit(message)

            success = add_block_rules_from_ip_file(
                tmp_list,
                rule_prefix="GameSpamFilter",
                progress_callback=on_progress
            )

            # --------------------------
            # 6. Verify created rules
            # --------------------------
            self.progress.emit(90)
            self.log.emit("🔍 Verifying rules …")

            if not success or not verify_rules_exist("GameSpamFilter"):
                raise Exception("Rules not found after creation.")

            # --------------------------
            # 7. Done
            # --------------------------
            self.progress.emit(100)
            self.done.emit(True, "✅ Fast Path Blocker installed/updated successfully.")

        except PermissionError as pe:
            self.done.emit(False, str(pe))
        except Exception as e:
            self.done.emit(False, f"❌ Error: {e}")
