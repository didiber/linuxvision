"""Entry point for the LinuxVision GUI."""

from linuxvision_gui import main as gui_main



import sys
from PyQt5.QtWidgets import QApplication

from .gui import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    gui_main()
