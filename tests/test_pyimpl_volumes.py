import ctypes

from ntfslink._pyimpl import volumes


def _patch_volume_root(monkeypatch, root='C:\\'):
    def fake_get_volume_path_name(path, buf, size):
        buf.value = root
        return True

    monkeypatch.setattr(volumes.winapi, 'GetVolumePathNameW', fake_get_volume_path_name)


def _patch_volume_info(monkeypatch, flags):
    def fake_get_volume_information(root, name_buf, name_size, serial, max_comp, fs_flags_ref, fsname_buf, fsname_size):
        fs_flags_ref._obj.value = flags
        return True

    monkeypatch.setattr(volumes.winapi, 'GetVolumeInformationW', fake_get_volume_information)


def test_volume_root_returns_root(monkeypatch):
    _patch_volume_root(monkeypatch, 'D:\\')
    assert volumes.volume_root('D:\\some\\path') == 'D:\\'


def test_volume_flags_without_cache(monkeypatch):
    _patch_volume_root(monkeypatch, 'C:\\')
    _patch_volume_info(monkeypatch, 0x1234)
    volumes.clear_cache()
    assert volumes.volume_flags('C:\\foo', use_cache=False) == 0x1234


def test_volume_flags_cache_hit_avoids_second_call(monkeypatch):
    volumes.clear_cache()
    _patch_volume_root(monkeypatch, 'C:\\')
    calls = {'n': 0}

    def fake_get_volume_information(root, name_buf, name_size, serial, max_comp, fs_flags_ref, fsname_buf, fsname_size):
        calls['n'] += 1
        fs_flags_ref._obj.value = 0xABCD
        return True

    monkeypatch.setattr(volumes.winapi, 'GetVolumeInformationW', fake_get_volume_information)

    first = volumes.volume_flags('C:\\foo', use_cache=True)
    second = volumes.volume_flags('C:\\bar', use_cache=True)  # same volume root

    assert first == second == 0xABCD
    assert calls['n'] == 1
    volumes.clear_cache()


def test_clear_cache_forces_refetch(monkeypatch):
    volumes.clear_cache()
    _patch_volume_root(monkeypatch, 'C:\\')
    _patch_volume_info(monkeypatch, 0x1)
    volumes.volume_flags('C:\\foo', use_cache=True)

    _patch_volume_info(monkeypatch, 0x2)
    cached = volumes.volume_flags('C:\\foo', use_cache=True)
    assert cached == 0x1  # still cached

    volumes.clear_cache()
    refreshed = volumes.volume_flags('C:\\foo', use_cache=True)
    assert refreshed == 0x2
    volumes.clear_cache()
