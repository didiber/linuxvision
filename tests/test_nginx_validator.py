import shutil
from plugins.validators.nginx_validator import NginxValidator


def test_detect_by_extension_and_content(tmp_path):
    file = tmp_path / "site.conf"
    file.write_text("server { listen 80; }")
    validator = NginxValidator()
    assert validator.detect(str(file))


def test_detect_wrong_extension(tmp_path):
    file = tmp_path / "site.txt"
    file.write_text("server { listen 80; }")
    validator = NginxValidator()
    assert not validator.detect(str(file))


def test_validate_skips_when_nginx_missing(tmp_path, monkeypatch):
    file = tmp_path / "test.conf"
    file.write_text("server { listen 80; }")
    validator = NginxValidator()

    monkeypatch.setattr(shutil, "which", lambda x: None)
    assert validator.validate(str(file))
