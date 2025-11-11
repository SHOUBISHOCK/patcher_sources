# ui/styles.py
# -*- coding: utf-8 -*-

DARK_BG = "#1e1e1e"
PANEL_BG = "#141414"
TEXT_FG = "#ffffff"
TITLE_GREEN = "#00ff00"
BTN_GREEN = "#32cd32"
BTN_RED = "#dc143c"
LOG_BG = "#141414"
LOG_FG = "#00ff00"
BORDER = "#3a3a3a"

APP_TITLE = "INS2DOI Community Patcher"

BASE_STYLESHEET = f"""
QMainWindow {{
    background-color: {DARK_BG};
    color: {TEXT_FG};
}}
QWidget {{
    background-color: {DARK_BG};
    color: {TEXT_FG};
    font-family: "Segoe UI";
    font-size: 11pt;
}}
QLabel#TitleLabel {{
    color: {TITLE_GREEN};
    font-size: 18pt;
    font-weight: 700;
}}
QTextBrowser#MainText {{
    background-color: {PANEL_BG};
    color: {TEXT_FG};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px;
}}
QPlainTextEdit#LogBox {{
    background-color: {LOG_BG};
    color: {LOG_FG};
    border: 1px solid {BORDER};
    border-radius: 6px;
    font-family: Consolas, monospace;
    font-size: 10pt;
}}
QScrollBar:vertical {{
    background: #202020;
    width: 8px;
    margin: 0;
    border: 1px solid #2a2a2a;
}}
QScrollBar::handle:vertical {{
    background: #444444;
    min-height: 20px;
    border-radius: 4px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar:horizontal {{
    height: 0px;
}}
QLineEdit, QComboBox {{
    background-color: {PANEL_BG};
    color: {TEXT_FG};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px;
}}
QProgressBar {{
    background: {PANEL_BG};
    border: 1px solid {BORDER};
    border-radius: 4px;
    text-align: center;
    color: {TEXT_FG};
}}
QProgressBar::chunk {{
    background-color: {BTN_GREEN};
    border-radius: 3px;
}}
QPushButton#InstallBtn {{
    background-color: {BTN_GREEN};
    color: black;
    font-weight: 700;
    border: 1px solid #0b7c0b;
    border-radius: 6px;
    padding: 6px 14px;
}}
QPushButton#ExitBtn {{
    background-color: {BTN_RED};
    color: white;
    font-weight: 700;
    border: 1px solid #7a0f1f;
    border-radius: 6px;
    padding: 6px 14px;
}}
QPushButton {{
    background-color: #2a2a2a;
    color: {TEXT_FG};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 12px;
}}
QPushButton:hover {{
    background-color: #333333;
}}
"""

# --- Extra appended styles (GUI enhancements) ---

APPENDED_STYLES = """
#mainPage {
    background-color: #1a1a1a;
    color: #e6e6e6;
}
QPushButton {
    background-color: #222;
    color: #00ff99;
    border: 1px solid #00ff99;
    border-radius: 6px;
    padding: 6px 10px;
}
QPushButton:hover {
    background-color: #00ff99;
    color: #111;
}
#scanLogBox {
    background-color: #111;
    color: #00ff66;
    border: 1px solid #00ff99;
    border-radius: 5px;
}
"""

# Merge new styles with the base stylesheet
BASE_STYLESHEET += APPENDED_STYLES

