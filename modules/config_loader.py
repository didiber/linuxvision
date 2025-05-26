import json
import os
from pathlib import Path


class ConfigLoader:
    """Load configuration files with minimal parsing."""

    def __init__(self, path=Path("config/config_roles.yaml")):
        self.path = Path(path)

    def load(self):
        """Return parsed configuration data."""
        if not self.path.exists():
            raise FileNotFoundError(self.path)

        text = self.path.read_text()
        ext = self.path.suffix.lower()

        if ext == ".json":
            return json.loads(text)

        # Try YAML if available; otherwise return raw text
        if ext in {".yaml", ".yml"}:
            try:
                import yaml  # type: ignore
                return yaml.safe_load(text)
            except Exception:
                pass
        # Fallback: simple line-based parsing
        return {
            i: line.strip()
            for i, line in enumerate(text.splitlines(), start=1)
            if line.strip()
        }
