import os
import types

import pytest

import ntfslink
import ntfslink.backend as backend_module


@pytest.fixture(params=sorted(ntfslink.available_backends()))
def backend_name(request, monkeypatch):
    """Parametrizes a test over every backend actually available on this
    machine (cext only if it was built)."""
    monkeypatch.setenv('NTFSLINK_BACKEND', request.param)
    backend_module.reset_for_tests()
    yield request.param
    backend_module.reset_for_tests()


@pytest.fixture
def backend(backend_name):
    return backend_module.get_backend()


class FakeBackend(types.SimpleNamespace):
    """A minimal fake satisfying the primitive-operation interface, for
    testing reparse.py/hardlinks.py orchestration without touching Win32
    at all."""


@pytest.fixture
def fake_backend():
    calls = []

    def build_reparse_buffer(tag, subst, print_name, flags=0):
        calls.append(('build_reparse_buffer', tag, subst, print_name, flags))
        return b'FAKE-BUFFER'

    def set_reparse_point(path, buffer):
        calls.append(('set_reparse_point', path, buffer))

    def get_reparse_buffer(path):
        calls.append(('get_reparse_buffer', path))
        import struct
        return struct.pack('<IHH', 0xA0000003, 0, 0) + b'\x00' * 8

    def parse_reparse_buffer(data):
        calls.append(('parse_reparse_buffer', data))
        return 0xA0000003, 0, '\\??\\C:\\target', 'C:\\target'

    def delete_reparse_point_ioctl(path, tag):
        calls.append(('delete_reparse_point_ioctl', path, tag))

    fb = FakeBackend(
        calls=calls,
        build_reparse_buffer=build_reparse_buffer,
        set_reparse_point=set_reparse_point,
        get_reparse_buffer=get_reparse_buffer,
        parse_reparse_buffer=parse_reparse_buffer,
        delete_reparse_point_ioctl=delete_reparse_point_ioctl,
    )
    return fb


@pytest.fixture
def unique_path(tmp_path):
    counter = {'n': 0}

    def make(name='item'):
        counter['n'] += 1
        return str(tmp_path / f'{name}_{counter["n"]}')

    return make
