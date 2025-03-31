import tempfile
import shutil
import os

class ConfigEditor:
    def __init__(self):
        self.sandbox_dir = tempfile.mkdtemp(prefix="linuxvision_")

    def parse_config(self, filepath):
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
            print(f"Kritischer Fehler: {str(e)}")
            return []
        return entries

    def sandboxed_save(self, filepath, new_content):
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

    def validate_config(self, sandbox_path):
        try:
            with open(sandbox_path, 'r') as f:
                content = f.read()
                # Platzhalter: Hier später echte Validierung einbauen
                return "Syntax OK" in content
        except Exception as e:
            print(f"Validierungsfehler: {str(e)}")
            return False
