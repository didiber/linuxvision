import subprocess
import os
from pathlib import Path
from .. import ConfigValidator

class NginxValidator(ConfigValidator):
    def detect(self, filepath):
        """
        Erkennt, ob eine Datei eine Nginx-Konfigurationsdatei ist.
        Prüft sowohl den Dateinamen als auch den Inhalt.
        """
        filepath = Path(filepath)

        # Prüfe Dateinamen-Muster
        filename_patterns = [
            'nginx.conf',
            'default.conf',
            '.conf'
        ]

        if any(pattern in filepath.name for pattern in filename_patterns):
            # Zusätzliche Inhaltsüberprüfung
            try:
                with open(filepath, 'r') as f:
                    content = f.read(1024)  # Nur die ersten 1024 Bytes lesen
                    nginx_keywords = ['server', 'location', 'http', 'upstream']
                    if any(keyword in content for keyword in nginx_keywords):
                        return True
            except Exception:
                # Bei Leseproblemen verlassen wir uns nur auf den Dateinamen
                pass

        return False

    def validate(self, filepath):
        """
        Validiert die Nginx-Konfiguration mit dem nginx-Kommandozeilentool.
        Gibt True zurück, wenn die Konfiguration gültig ist.
        """
        try:
            # Prüfe, ob nginx installiert ist
            which_result = subprocess.run(
                ["which", "nginx"],
                capture_output=True,
                text=True
            )

            if which_result.returncode != 0:
                print("Warnung: nginx nicht installiert, überspringe Validierung")
                return True

            # Führe nginx -t aus
            result = subprocess.run(
                ["nginx", "-t", "-c", filepath],
                capture_output=True,
                text=True
            )

            # Prüfe das Ergebnis
            success = result.returncode == 0 or "syntax is okay" in result.stderr

            if not success:
                error_message = result.stderr or result.stdout
                print(f"Nginx-Validierungsfehler: {error_message}")

            return success

        except Exception as e:
            print(f"Fehler bei der Nginx-Validierung: {str(e)}")
            return False
