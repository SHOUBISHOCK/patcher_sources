from PySide6.QtWidgets import QMainWindow, QStackedWidget
from ui.pages.main_page import MainPage
from ui.pages.patcher_page import PatcherPage
from ui.pages.disabler_page import DisablerPage
from ui.pages.blocker_page import BlockerPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("INS2DOI Community Patcher")
        self.resize(900, 680)

        # Store scan results
        self.scan_results = {}

        # Initialize all pages
        self.main_page = MainPage(
            go_patcher=self.open_patcher,
            go_disabler=self.open_disabler,
            go_blocker=self.open_blocker,
            go_home=self.go_home,
            set_scan_results=self.set_scan_results
        )
        
        self.patcher_page = PatcherPage(back_cb=self.go_home)
        self.disabler_page = DisablerPage(back_cb=self.go_home, get_scan_results=self.get_scan_results)
        self.blocker_page = BlockerPage(back_cb=self.go_home)

        # Central stack
        self.stack = QStackedWidget()
        self.stack.addWidget(self.main_page)
        self.stack.addWidget(self.patcher_page)
        self.stack.addWidget(self.disabler_page)
        self.stack.addWidget(self.blocker_page)
        self.setCentralWidget(self.stack)

        self.stack.setCurrentWidget(self.main_page)

    # Navigation
    def go_home(self):
        self.stack.setCurrentWidget(self.main_page)

    def open_patcher(self):
        self.stack.setCurrentWidget(self.patcher_page)

    def open_disabler(self):
        self.stack.setCurrentWidget(self.disabler_page)
        self.disabler_page._refresh_from_scan()  # ensure latest data is displayed

    def open_blocker(self):
        self.stack.setCurrentWidget(self.blocker_page)

    # Scan data handling
    def set_scan_results(self, results: dict):
        self.scan_results = results or {}
        print(f"[debug] Stored scan results in MainWindow: {self.scan_results}")

    def get_scan_results(self):
        print(f"[debug] Returning scan results: {self.scan_results}")
        return self.scan_results
