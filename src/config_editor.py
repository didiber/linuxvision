# config_editor.py

import tempfile
import shutil
import os
import json
import importlib
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class ValidationResult:
    """Represents the result of a validation with an optional message."""

    is_valid: bool
    message: str = ""

    def __bool__(self) -> bool:  # pragma: no cover - simple truthiness helper
        return self.is_valid


class ConfigValidator:
    def detect(self, filepath: str) -> bool:
        """Erkennt, ob das Plugin für die Datei zuständig ist."""
        return False

    def validate(self, filepath: str) -> bool:
        """Führt die Validierung durch."""
        return False


class ConfigEditor:
    def __init__(self):
        self.sandbox_dir = tempfile.mkdtemp(prefix="linuxvision_")
        self.validators = self._load_validators()

    def _load_validators(self):
        """Lädt alle Validierungs-Plugins dynamisch."""
        validators = []
        try:
            plugin_dir = Path(__file__).parent / "plugins/validators"
            for file in plugin_dir.glob("*.py"):
                if file.name == "__init__.py":
                    continue
                module_name = f"plugins.validators.{file.stem}"
                spec = importlib.util.spec_from_file_location(
                    module_name, file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for attr in dir(module):
                    cls = getattr(module, attr)
                    if (isinstance(cls, type)
                            and issubclass(cls, ConfigValidator)
                            and cls != ConfigValidator):
                        validators.append(cls())
        except Exception as e:
            print(f"Plugin-Loader-Fehler: {str(e)}")
        return validators

    def parse_config(self, filepath):
        """Liest und parst Konfigurationsdateien (Key-Value-Format)."""
        entries = []
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)
                        entries.append((key.strip(), value.strip()))
        except FileNotFoundError:
            print(f"Fehler: Datei {filepath} nicht gefunden!")
            return []
        except Exception as e:
            print(f"Parser-Fehler: {str(e)}")
            return []
        return entries

    def sandboxed_save(self, filepath, new_content):
        """Sichert Änderungen über eine Sandbox."""
        try:
            sandbox_path = f"{self.sandbox_dir}/{os.path.basename(filepath)}"
            shutil.copy2(filepath, sandbox_path)

            with open(sandbox_path, 'w') as f:
                f.write(new_content)

            if self.validate_config(sandbox_path):
                shutil.move(sandbox_path, filepath)
                return True
            return False

        except Exception as e:
            print(f"Sandbox-Fehler: {str(e)}")
            return False

    def save_or_backup(self, filepath: str, new_content: str) -> ValidationResult:
        """Save content if valid, otherwise create a .bak backup.

        Parameters
        ----------
        filepath: str
            Path to the target configuration file.
        new_content: str
            Content to be validated and written.
        Returns
        -------
        ValidationResult
            Result of the validation with information about created backup.
        """

        tmp_path = os.path.join(self.sandbox_dir, os.path.basename(filepath))
        try:
            with open(tmp_path, "w") as tmp_file:
                tmp_file.write(new_content)

            validation = self.validate_config(tmp_path)
            if validation:
                os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
                with open(filepath, "w") as dest:
                    dest.write(new_content)
                return ValidationResult(True, "Konfiguration gespeichert.")

            backup_path = f"{filepath}.bak"
            with open(backup_path, "w") as backup:
                backup.write(new_content)
            return ValidationResult(False, f"Validierung fehlgeschlagen. Backup unter {backup_path} erstellt.")
        except Exception as exc:
            return ValidationResult(False, f"Fehler beim Speichern: {exc}")
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

    def validate_config(self, sandbox_path):
        """Hybride Validierung: Allgemeine Syntax + Plugin-Checks."""
        return (self._validate_syntax(sandbox_path)
                and self._validate_with_plugins(sandbox_path))

    def _validate_syntax(self, sandbox_path):
        """Allgemeine Syntaxprüfung für JSON/YAML/INI."""
        filepath = str(sandbox_path)
        try:
            if filepath.endswith(".json"):
                with open(filepath, "r") as f:
                    json.load(f)
            elif filepath.endswith((".yaml", ".yml")):
                import yaml
                with open(filepath, "r") as f:
                    yaml.safe_load(f)
            else:
                self.parse_config(filepath)
            return True
        except Exception as e:
            print(f"Syntaxfehler: {str(e)}")
            return False

    def _validate_with_plugins(self, sandbox_path):
        """Führt dienstspezifische Plugin-Validierungen durch."""
        for validator in self.validators:
            if validator.detect(sandbox_path):
                return validator.validate(sandbox_path)
        return True
