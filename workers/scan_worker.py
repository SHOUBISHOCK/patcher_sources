# -*- coding: utf-8 -*-
from __future__ import annotations
import os
import time
import logging
from pathlib import Path
from typing import Dict, List
from PySide6.QtCore import QObject, Signal
from services.steam import find_steam_common_dirs

logger = logging.getLogger("workers.scan")

class ScanWorker(QObject):
    progress = Signal(int)
    log = Signal(str)
    finished = Signal(object)

    def __init__(self, games: Dict[str, Dict[str, str]]):
        super().__init__()
        self.games = games

    # -----------------------------------------------------
    # Helper: Look for folders on drives
    # -----------------------------------------------------
    def _find_game_dirs_on_drive(self, drive: Path, game_folder_name: str) -> List[Path]:
        found: List[Path] = []
        candidates = [
            drive / "Program Files (x86)" / "Steam" / "steamapps" / "common" / game_folder_name,
            drive / "Program Files" / "Steam" / "steamapps" / "common" / game_folder_name,
            drive / "SteamLibrary" / "steamapps" / "common" / game_folder_name,
        ]
        for c in candidates:
            if c.exists() and c.is_dir():
                found.append(c)
        return found

    # -----------------------------------------------------
    # Main scanning routine
    # -----------------------------------------------------
    def run(self):
        print("[debug] ScanWorker.run() entered")
        result = {"found_games": {}, "missing": [], "libraries": []}

        self.log.emit("🔵 Starting scan...\n")
        time.sleep(0.1)

        # STEP 1: Locate Steam libraries
        self.log.emit("🧩 Detecting Steam libraries...\n")
        try:
            steam_libs = find_steam_common_dirs()
        except Exception as e:
            self.log.emit(f"❌ Steam library detection failed: {e}\n")
            steam_libs = []

        if not steam_libs:
            self.log.emit("⚠️ No Steam libraries found.\n")
            self.finished.emit(result)
            return

        self.log.emit("✅ Detected Steam libraries:\n")
        for lib in steam_libs:
            self.log.emit(f"  - {lib}\n")
        result["libraries"] = [str(l) for l in steam_libs]

        total = len(self.games)
        step = 100 // (total if total else 1)
        progress = 0

        # STEP 2: Search for each game
        for game_name, info in self.games.items():
            folder = info.get("Folder", "")
            exe_name = info.get("exe", "")
            self.log.emit(f"\n🔵 Checking '{game_name}'...\n")

            found = False
            for lib in steam_libs:
                possible_dir = lib / folder
                exe_path = possible_dir / exe_name

                self.log.emit(f"• Searching in: {exe_path}\n")
                print(f"[debug] checking {exe_path}")

                # Case-insensitive search for .exe
                if exe_path.exists() or any(
                    f.name.lower() == exe_name.lower() for f in possible_dir.glob("*.exe")
                ):
                    self.log.emit(f"✅ Found in {possible_dir}\n")
                    result["found_games"][game_name] = str(possible_dir)
                    found = True
                    break

            if not found:
                self.log.emit(f"❌ {game_name} not found in Steam libraries.\n")
                result["missing"].append(game_name)

            progress += step
            self.progress.emit(min(progress, 100))
            time.sleep(0.1)

        # STEP 3: Fallback deep scan if missing
        if result["missing"]:
            self.log.emit("🪄 Running fallback drive scan for missing games...\n")
            drives = [Path(f"{chr(i)}:\\") for i in range(67, 91) if Path(f"{chr(i)}:\\").exists()]
            for drive in drives:
                self.log.emit(f"→ Scanning drive {drive}\n")
                for game_name in list(result["missing"]):
                    folder = self.games[game_name]["Folder"]
                    exe_name = self.games[game_name]["exe"]
                    for found_dir in self._find_game_dirs_on_drive(drive, folder):
                        exe_path = found_dir / exe_name
                        if exe_path.exists() or any(
                            f.name.lower() == exe_name.lower() for f in found_dir.glob("*.exe")
                        ):
                            self.log.emit(f"✅ Found '{game_name}' in {found_dir}\n")
                            result["found_games"][game_name] = str(found_dir)
                            result["missing"].remove(game_name)
            time.sleep(0.2)

        # STEP 4: Wrap up
        self.progress.emit(100)
        if result["found_games"]:
            self.log.emit("✅ Scan complete.\n")
        else:
            self.log.emit("⚠️ No supported games detected.\n")

        self.log.emit(f"[debug] Final result: {result}\n")
        self.finished.emit(result)
        print("[debug] ScanWorker finished cleanly")
