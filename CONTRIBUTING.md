# Beitrag leisten

## Umgebung einrichten
1. Python >=3.11 installieren.
2. Repository klonen und ins Verzeichnis wechseln:
   ```bash
   git clone https://github.com/didiber/linuxvision.git
   cd linuxvision
   ```
3. Virtuelle Umgebung anlegen und Abhängigkeiten installieren:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Tests ausführen:
   ```bash
   pytest
   ```

## Pull Requests
* Einen Branch von `main` oder `dev` erstellen.
* Vor dem Pushen stets `pytest` ausführen.
* Beschreibende Commits schreiben und einen PR über GitHub stellen.
