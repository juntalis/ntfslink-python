import pytest

from ntfslink._pyimpl import backend as pyimpl_backend


def test_make_backend_unknown_codec_raises():
    with pytest.raises(ValueError):
        pyimpl_backend.make_backend('not-a-codec')


def test_make_backend_ctypes_wraps_expected_primitives():
    b = pyimpl_backend.make_backend('ctypes')
    assert b.kind == 'ctypes'
    for attr in (
        'build_reparse_buffer', 'parse_reparse_buffer', 'set_reparse_point',
        'get_reparse_buffer', 'delete_reparse_point_ioctl', 'create_hard_link',
        'get_link_count', 'get_file_reference_number', 'get_ntfs_file_record',
        'query_volume_flags', 'ensure_privileges', 'volume_root',
    ):
        assert hasattr(b, attr)


def test_query_volume_flags_wrapper_delegates(tmp_path, monkeypatch):
    called = {}

    def fake_volume_flags(path, use_cache):
        called['args'] = (path, use_cache)
        return 0x99

    monkeypatch.setattr(pyimpl_backend.volumes, 'volume_flags', fake_volume_flags)
    assert pyimpl_backend.query_volume_flags(str(tmp_path), use_cache=True) == 0x99
    assert called['args'] == (str(tmp_path), True)


def test_ensure_privileges_wrapper_delegates(monkeypatch):
    calls = []
    monkeypatch.setattr(pyimpl_backend.privileges, 'ensure_privileges', lambda: calls.append(1))
    pyimpl_backend.ensure_privileges()
    assert calls == [1]
