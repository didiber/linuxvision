import subprocess
from .. import ConfigValidator

class NginxValidator(ConfigValidator):
    def detect(self, filepath):
        return "nginx" in filepath  # oder komplexere Logik

    def validate(self, filepath):
        result = subprocess.run(
            ["nginx", "-t", "-c", filepath],
            capture_output=True,
            text=True
        )
        return "syntax is okay" in result.stderr
