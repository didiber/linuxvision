#!/usr/bin/env python3
"""
linuxvision-GUI.py
------------------
Hauptschnittstelle für die LinuxVision Config Suite.
Dieses Modul startet die GUI und initialisiert alle Kernkomponenten.
"""

import sys
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow
from modules.manpage_explorer import ManpageExplorer
from modules.config_loader import ConfigLoader

# Logging-Konfiguration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LinuxVision Config Suite")
        self.setGeometry(100, 100, 1024, 768)
        self.initUI()

    def initUI(self):
        try:
            self.manpage_explorer = ManpageExplorer()
            self.setCentralWidget(self.manpage_explorer)
            logging.info("GUI erfolgreich initialisiert.")
        except Exception as e:
            logging.error(f"Fehler bei der GUI-Initialisierung: {e}")

    def loadConfig(self):
        try:
            config_loader = ConfigLoader()
            config_data = config_loader.load()
            self.manpage_explorer.populate(config_data)
            logging.info("Konfigurationsdaten erfolgreich geladen.")
        except FileNotFoundError:
            logging.error("Konfigurationsdatei nicht gefunden.")
        except Exception as e:
            logging.error(f"Fehler beim Laden der Konfiguration: {e}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
