import os
import pytest

from src.config_editor import ConfigEditor


@pytest.fixture
def editor_no_plugins(monkeypatch):
    """ConfigEditor instance without any validators loaded."""
    ed = ConfigEditor()
    ed.validators = []
    return ed


def test_parse_config_invalid_lines(editor_no_plugins, tmp_path):
    cfg = tmp_path / "test.conf"
    cfg.write_text("""
key1=value1
invalid_line
key2=value2
    """)
    entries = editor_no_plugins.parse_config(cfg)
    assert ("key1", "value1") in entries
    assert ("key2", "value2") in entries
    # Invalid line should be ignored
    assert len(entries) == 2


def test_validate_invalid_json(editor_no_plugins, tmp_path):
    bad_json = tmp_path / "bad.json"
    bad_json.write_text('{"key": "value"')  # missing closing brace
    assert editor_no_plugins.validate_config(str(bad_json)) is False


def test_validate_invalid_yaml(editor_no_plugins, tmp_path):
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text("key1: value1:\n  - broken")
    assert editor_no_plugins.validate_config(str(bad_yaml)) is False


class DummyPlugin:
    def __init__(self, detect_return=True, validate_return=True):
        self.detect_called = 0
        self.validate_called = 0
        self._detect_return = detect_return
        self._validate_return = validate_return

    def detect(self, path):
        self.detect_called += 1
        return self._detect_return

    def validate(self, path):
        self.validate_called += 1
        return self._validate_return


def test_plugin_skip_when_not_detected(editor_no_plugins, tmp_path):
    plugin = DummyPlugin(detect_return=False)
    editor_no_plugins.validators = [plugin]
    target = tmp_path / "file.txt"
    target.write_text("data")
    assert editor_no_plugins.validate_config(str(target)) is True
    assert plugin.detect_called == 1
    # validate should not be called because detect returned False
    assert plugin.validate_called == 0


def test_plugin_validation_failure(editor_no_plugins, tmp_path):
    plugin = DummyPlugin(detect_return=True, validate_return=False)
    editor_no_plugins.validators = [plugin]
    target = tmp_path / "file.conf"
    target.write_text("data")
    assert editor_no_plugins.validate_config(str(target)) is False
    assert plugin.detect_called == 1
    assert plugin.validate_called == 1
