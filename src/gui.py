"""Basic GUI definitions for LinuxVision."""

from PyQt5.QtWidgets import QMainWindow

from modules.manpage_explorer import ManpageExplorer
from modules.config_loader import ConfigLoader


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LinuxVision Config Suite")
        self.resize(1024, 768)
        self.manpage_explorer = ManpageExplorer()
        self.setCentralWidget(self.manpage_explorer)
        self._load_config()

    def _load_config(self):
        loader = ConfigLoader()
        try:
            data = loader.load()
            self.manpage_explorer.populate(data)
        except FileNotFoundError:
            # Config file missing; ignore for now
            pass
