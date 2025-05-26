import json
from pathlib import Path
from typing import Any, Dict


class ConfigLoader:
    """Simple loader for JSON configuration files."""

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else None

    def load(self) -> Dict[str, Any]:
        """Load and return configuration data.

        Returns an empty dict if no path is provided or loading fails.
        """
        if not self.path:
            return {}

        try:
            with open(self.path, "r") as fh:
                return json.load(fh)
        except FileNotFoundError:
            raise
        except Exception:
            return {}
