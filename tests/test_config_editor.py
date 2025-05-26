import pytest
import os
import shutil
from pathlib import Path
import importlib.util
from src.config_editor import ConfigEditor, ValidationResult
from plugins import ConfigValidator

@pytest.fixture
def editor():
    return ConfigEditor()

@pytest.fixture
def sample_config(tmp_path):
    config_file = tmp_path / "app.conf"
    config_file.write_text("""
        # Kommentar
        key1 = value1
        key2 = value2
    """)
    return config_file

# Testet erfolgreiches Parsen einer Konfigurationsdatei
def test_parse_config_valid(editor, sample_config):
    entries = editor.parse_config(sample_config)
    assert len(entries) == 2
    assert ("key1", "value1") in entries

# Testet fehlende Datei
def test_parse_config_missing_file(editor):
    entries = editor.parse_config("nonexistent.conf")
    assert entries == []

# Testet Sandbox-Speicherung mit Validierung
def test_sandboxed_save_success(editor, sample_config, monkeypatch):
    monkeypatch.setattr(editor, 'validate_config', lambda path: True)
    assert editor.sandboxed_save(sample_config, "key3=value3") is True
    assert "key3" in open(sample_config).read()

# Testet fehlgeschlagene Validierung
def test_sandboxed_save_validation_fail(editor, sample_config, monkeypatch):
    monkeypatch.setattr(editor, 'validate_config', lambda path: False)
    assert editor.sandboxed_save(sample_config, "invalid_content") is False

# Testet JSON-Validierung
def test_validate_json(editor, tmp_path):
    json_file = tmp_path / "test.json"
    json_file.write_text('{"key": "value"}')
    assert editor.validate_config(str(json_file)) is True

# Testet Plugin-Integration mit Mock
def test_plugin_validation(editor, tmp_path):
    calls = {
        'detect': 0,
        'validate': 0,
    }

    class DummyValidator:
        def detect(self, path):
            calls['detect'] += 1
            return True

        def validate(self, path):
            calls['validate'] += 1
            return True

    editor.validators = [DummyValidator()]
    
    test_file = tmp_path / "nginx.conf"
    test_file.write_text("server { ... }")
    
    assert editor.validate_config(test_file) is True
    assert calls['validate'] == 1


def test_dynamic_loading(editor):
    assert any(type(v).__name__ == "NginxValidator" for v in editor.validators)


# Tests for save_or_backup
def test_save_or_backup_success(editor, sample_config, monkeypatch):
    monkeypatch.setattr(editor, "validate_config", lambda path: True)
    result = editor.save_or_backup(str(sample_config), "key3=value3")
    assert isinstance(result, ValidationResult)
    assert result.is_valid
    assert "gespeichert" in result.message
    assert "key3" in open(sample_config).read()
    assert not os.path.exists(str(sample_config) + ".bak")


def test_save_or_backup_failure(editor, sample_config, monkeypatch):
    monkeypatch.setattr(editor, "validate_config", lambda path: False)
    result = editor.save_or_backup(str(sample_config), "invalid")
    assert not result.is_valid
    backup_path = str(sample_config) + ".bak"
    assert os.path.exists(backup_path)
    with open(backup_path) as f:
        assert "invalid" in f.read()
    with open(sample_config) as f:
        assert "invalid" not in f.read()


def test_validator_loading_with_real_plugin(tmp_path, monkeypatch):
    """ConfigEditor should load NginxValidator when plugin file exists."""
    # Prepare temporary plugin directory with the nginx validator
    plugin_dir = tmp_path / "plugins" / "validators"
    plugin_dir.mkdir(parents=True)
    src_validator = (
        Path(__file__).resolve().parents[1]
        / "plugins"
        / "validators"
        / "nginx_validator.py"
    )
    shutil.copy(src_validator, plugin_dir / "nginx_validator.py")

    def _tmp_loader(self):
        validators = []
        for file in plugin_dir.glob("*.py"):
            if file.name == "__init__.py":
                continue
            module_name = f"plugins.validators.{file.stem}"
            spec = importlib.util.spec_from_file_location(module_name, file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for attr in dir(module):
                cls = getattr(module, attr)
                if (
                    isinstance(cls, type)
                    and issubclass(cls, ConfigValidator)
                    and cls is not ConfigValidator
                ):
                    validators.append(cls())
        return validators

    monkeypatch.setattr(ConfigEditor, "_load_validators", _tmp_loader)
    editor = ConfigEditor()
    assert any(type(v).__name__ == "NginxValidator" for v in editor.validators)
