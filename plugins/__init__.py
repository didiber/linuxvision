# plugins/__init__.py
from abc import ABC, abstractmethod

class ConfigValidator(ABC):
    @abstractmethod
    def detect(self, filepath: str) -> bool:
        """Erkennt, ob das Plugin für die Datei zuständig ist."""
        pass

    @abstractmethod
    def validate(self, filepath: str) -> bool:
        """Führt die dienstspezifische Validierung durch."""
        pass
