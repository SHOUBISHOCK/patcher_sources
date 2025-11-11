# workers/patcher_worker.py
# -*- coding: utf-8 -*-
from PySide6.QtCore import QObject, Signal
from installer.utils import decode_embedded_zip, extract_zip
from installer import embedded_ins_patch, embedded_doi_patch
import os


class PatcherWorker(QObject):
    """Wrapper for MultiPatcherWorker to integrate with modern GUI."""
    log = Signal(str)
    progress = Signal(int)
    finished = Signal(str)

    def __init__(self, found_games: dict):
        super().__init__()
        self.found_games = found_games or {}

    def run(self):
        """Build tasks and run patching immediately."""
        try:
            tasks = []
            for name, path in self.found_games.items():
                if "insurgency" in name.lower():
                    tasks.append({"game_key": "insurgency2", "target_dir": str(path)})
                elif "infamy" in name.lower():
                    tasks.append({"game_key": "dayofinfamy", "target_dir": str(path)})
                else:
                    self.log.emit(f"Skipping unknown game: {name}")

            if not tasks:
                self.log.emit("⚠️ No valid games detected for patching.")
                self.finished.emit("No valid tasks.")
                return

            total = len(tasks)
            for i, task in enumerate(tasks, 1):
                key = task["game_key"]
                target = task["target_dir"]

                if key == "insurgency2":
                    data = embedded_ins_patch.BASE64_DATA
                    sha = embedded_ins_patch.SHA256
                    label = "Insurgency 2 Patch"
                elif key == "dayofinfamy":
                    data = embedded_doi_patch.BASE64_DATA
                    sha = embedded_doi_patch.SHA256
                    label = "Day of Infamy Patch"
                else:
                    self.log.emit(f"Unknown task key: {key}")
                    continue

                self.log.emit(f"🔧 Applying {label} to {target} ...")
                zip_path = decode_embedded_zip(data, sha, label)
                extract_zip(zip_path, os.path.join(target, "BattlEye"))
                os.unlink(zip_path)

                # --- Emit progress update to UI ---
                percent = int((i / total) * 100)
                self.progress.emit(percent)  # <--- Added line
                self.log.emit(f"✅ {label} applied successfully. ({percent}%)")

            self.progress.emit(100)  # <--- Ensure bar reaches 100% at end
            self.log.emit("🎯 All patches applied successfully.")
            self.finished.emit("Done")

        except Exception as e:
            self.log.emit(f"❌ Patch process failed: {e}")
            self.finished.emit(f"Error: {e}")
