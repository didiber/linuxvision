import yaml
from pathlib import Path

def load_roles(file_path: Path) -> dict:
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def is_change_allowed(user_role: str, param: str, roles_data: dict) -> bool:
    """
    Prüft, ob der Benutzer mit der angegebenen Rolle den Parameter bearbeiten darf.
    """
    role = roles_data.get('roles', {}).get(user_role)
    if not role:
        return False
    allowed = role.get('allowed_params', [])
    return 'all' in allowed or param in allowed

# Beispielnutzung:
if __name__ == "__main__":
    config_path = Path(__file__).parent.parent / "config" / "config_roles.yaml"
    roles_data = load_roles(config_path)
    if is_change_allowed('junior_admin', 'nginx.worker_processes', roles_data):
        print("Änderung erlaubt!")
    else:
        print("Zugriff verweigert!")
