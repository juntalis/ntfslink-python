import pytest

import ntfslink.backend as backend_module


@pytest.fixture(autouse=True)
def _reset():
    backend_module.reset_for_tests()
    yield
    backend_module.reset_for_tests()


def test_auto_prefers_cext_when_available(monkeypatch):
    monkeypatch.delenv('NTFSLINK_BACKEND', raising=False)
    assert backend_module.active_backend() == 'cext'


def test_forcing_ctypes(monkeypatch):
    monkeypatch.setenv('NTFSLINK_BACKEND', 'ctypes')
    b = backend_module.get_backend()
    assert backend_module.active_backend() == 'ctypes'
    assert b.kind == 'ctypes'


def test_forcing_struct(monkeypatch):
    monkeypatch.setenv('NTFSLINK_BACKEND', 'struct')
    b = backend_module.get_backend()
    assert backend_module.active_backend() == 'struct'
    assert b.kind == 'struct'


def test_forcing_cext_explicitly(monkeypatch):
    monkeypatch.setenv('NTFSLINK_BACKEND', 'cext')
    assert backend_module.active_backend() == 'cext'


def test_unknown_override_raises(monkeypatch):
    monkeypatch.setenv('NTFSLINK_BACKEND', 'not-a-real-backend')
    with pytest.raises(ValueError):
        backend_module.get_backend()


def test_backend_choice_is_cached_until_reset(monkeypatch):
    monkeypatch.setenv('NTFSLINK_BACKEND', 'ctypes')
    backend_module.get_backend()
    monkeypatch.setenv('NTFSLINK_BACKEND', 'struct')
    # still cached as ctypes: env var changes don't take effect until reset
    assert backend_module.active_backend() == 'ctypes'
    backend_module.reset_for_tests()
    assert backend_module.active_backend() == 'struct'


def test_auto_falls_back_when_cext_import_fails(monkeypatch):
    monkeypatch.delenv('NTFSLINK_BACKEND', raising=False)

    def fail_load_cext():
        raise ImportError('simulated missing compiled extension')

    monkeypatch.setattr(backend_module, '_load_cext', fail_load_cext)
    assert backend_module.active_backend() == 'struct'


def test_forcing_cext_propagates_import_error_instead_of_falling_back(monkeypatch):
    monkeypatch.setenv('NTFSLINK_BACKEND', 'cext')

    def fail_load_cext():
        raise ImportError('simulated missing compiled extension')

    monkeypatch.setattr(backend_module, '_load_cext', fail_load_cext)
    with pytest.raises(ImportError):
        backend_module.get_backend()


def test_available_backends_always_includes_pure_python():
    available = backend_module.available_backends()
    assert 'ctypes' in available
    assert 'struct' in available


def test_available_backends_reflects_cext_import_failure(monkeypatch):
    def fail_load_cext():
        raise ImportError('simulated missing compiled extension')

    monkeypatch.setattr(backend_module, '_load_cext', fail_load_cext)
    assert 'cext' not in backend_module.available_backends()


def test_non_import_error_from_cext_is_not_swallowed(monkeypatch):
    monkeypatch.delenv('NTFSLINK_BACKEND', raising=False)

    def broken_load_cext():
        raise RuntimeError('extension imported but is broken')

    monkeypatch.setattr(backend_module, '_load_cext', broken_load_cext)
    with pytest.raises(RuntimeError):
        backend_module.get_backend()
