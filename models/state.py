# models/state.py
# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class ScanResult:
    found_games: Dict[str, Dict[str, str]] = field(default_factory=dict)
    missing: List[str] = field(default_factory=list)
    libraries: List[str] = field(default_factory=list)
    scan_log_text: str = ""
