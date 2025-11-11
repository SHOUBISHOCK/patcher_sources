# core/logging_setup.py
# -*- coding: utf-8 -*-
import tempfile
from pathlib import Path
from datetime import datetime
import logging
from typing import Optional
from PySide6.QtWidgets import QPlainTextEdit

LOG_FILE = Path(tempfile.gettempdir()) / "game_tools_suite.log"

def setup_logging(name: str = "game_tools") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        )
        logger.setLevel(logging.DEBUG)
    return logger

def write_log_line(msg: str, log_widget: Optional[QPlainTextEdit] = None) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass
    if log_widget is not None:
        try:
            log_widget.appendPlainText(line)
        except Exception:
            pass
