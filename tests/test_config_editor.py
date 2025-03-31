import pytest
import os
import shutil
from config_editor import ConfigEditor

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
def test_sandboxed_save_success(editor, sample_config, mocker):
    mocker.patch.object(editor, 'validate_config', return_value=True)
    assert editor.sandboxed_save(sample_config, "key3=value3") is True
    assert "key3" in open(sample_config).read()

# Testet fehlgeschlagene Validierung
def test_sandboxed_save_validation_fail(editor, sample_config, mocker):
    mocker.patch.object(editor, 'validate_config', return_value=False)
    assert editor.sandboxed_save(sample_config, "invalid_content") is False

# Testet JSON-Validierung
def test_validate_json(editor, tmp_path):
    json_file = tmp_path / "test.json"
    json_file.write_text('{"key": "value"}')
    assert editor.validate_config(json_file) is True

# Testet Plugin-Integration mit Mock
def test_plugin_validation(editor, mocker, tmp_path):
    mock_validator = mocker.Mock()
    mock_validator.detect.return_value = True
    mock_validator.validate.return_value = True
    editor.validators = [mock_validator]
    
    test_file = tmp_path / "nginx.conf"
    test_file.write_text("server { ... }")
    
    assert editor.validate_config(test_file) is True
    mock_validator.validate.assert_called_once()
