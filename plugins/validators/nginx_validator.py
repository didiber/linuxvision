import subprocess
import shutil
import os
from pathlib import Path
from .. import ConfigValidator

class NginxValidator(ConfigValidator):
    def detect(self, filepath):
        """Bestimmt, ob ``filepath`` eine Nginx-Konfigurationsdatei sein
        könnte.

        Neben der Dateiendung werden einige Schlüsselwörter im Inhalt
        geprüft.
        """
        path = Path(filepath)

        if path.suffix != ".conf":
            return False

        if path.name in {"nginx.conf", "default.conf"}:
            return True

        try:
            with open(path, "r", errors="ignore") as handle:
                snippet = handle.read(1024)
        except Exception:
            return False

        keywords = ["server", "location", "http", "upstream"]
        return any(kw in snippet for kw in keywords)

    def validate(self, filepath):
        """
        Validiert die Nginx-Konfiguration mit dem nginx-Kommandozeilentool.
        Gibt True zurück, wenn die Konfiguration gültig ist.
        """
        try:
            # Prüfe, ob nginx installiert ist
            if shutil.which("nginx") is None:
                print("Warnung: nginx nicht installiert, überspringe Validierung")
                return True

            # Führe nginx -t aus
            result = subprocess.run(
                ["nginx", "-t", "-c", filepath],
                capture_output=True,
                text=True
            )

            # Prüfe das Ergebnis
            stderr = result.stderr.lower()
            stdout = result.stdout.lower()
            success = (
                result.returncode == 0
                or "syntax is ok" in stderr
                or "syntax is ok" in stdout
                or "syntax is okay" in stderr
                or "syntax is okay" in stdout
            )

            if not success:
                error_message = result.stderr or result.stdout
                print(f"Nginx-Validierungsfehler: {error_message}")

            return success

        except Exception as e:
            print(f"Fehler bei der Nginx-Validierung: {str(e)}")
            return False
