import importlib
import sys
import types


def _load_rbac(monkeypatch):
    """Import rbac module with a temporary yaml stub."""
    stub = types.SimpleNamespace(safe_load=lambda f: {})
    monkeypatch.setitem(sys.modules, 'yaml', stub)
    if 'src.rbac' in sys.modules:
        return importlib.reload(sys.modules['src.rbac'])
    return importlib.import_module('src.rbac')


def test_is_change_allowed_positive(monkeypatch):
    rbac = _load_rbac(monkeypatch)
    data = {
        'roles': {
            'admin': {'allowed_params': ['all']},
            'junior': {'allowed_params': ['foo.bar']},
        }
    }
    assert rbac.is_change_allowed('admin', 'anything', data)
    assert rbac.is_change_allowed('junior', 'foo.bar', data)


def test_is_change_allowed_negative(monkeypatch):
    rbac = _load_rbac(monkeypatch)
    data = {
        'roles': {
            'junior': {'allowed_params': ['foo.bar']}
        }
    }
    assert not rbac.is_change_allowed('junior', 'other.param', data)
    assert not rbac.is_change_allowed('unknown', 'foo.bar', data)

