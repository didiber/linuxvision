from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit

class ManpageExplorer(QWidget):
    """Simple widget to display configuration or manpage text."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)
        self.setLayout(layout)

    def populate(self, data):
        """Populate the explorer with the provided data."""
        self.text_area.setPlainText(str(data))
