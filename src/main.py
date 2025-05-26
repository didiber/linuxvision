"""Command line entry point for LinuxVision."""

import sys
from PyQt5.QtWidgets import QApplication

from .gui import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
