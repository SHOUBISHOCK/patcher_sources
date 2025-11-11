# models/games.py
# -*- coding: utf-8 -*-

# Map: game key -> steam folder name
GAME_FOLDERS = {
    "dayofinfamy": "dayofinfamy",
    "insurgency2": "insurgency2",
}

# Mapping game-key -> Human Readable/Original Titel (für Scan/Prefill)
GKEY_TO_TITLE = {
    "dayofinfamy": "Day of Infamy",
    "insurgency2": "Insurgency 2",
}

# (Optional) Detail-Metadaten für UI/Scan
GAMES_META = {
    "Day of Infamy": {"AppID": "447820", "exe": "dayofinfamy_x64.exe", "Folder": "dayofinfamy"},
    "Insurgency 2": {"AppID": "222880", "exe": "insurgency_x64.exe", "Folder": "insurgency2"},
}
