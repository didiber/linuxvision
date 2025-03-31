def parse_config(self, filepath):
    entries = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                # Ignoriere Kommentare und leere Zeilen
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
