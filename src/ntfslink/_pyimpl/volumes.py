"""Volume path/capability-flag queries, with an opt-in cache."""
import ctypes
from ctypes import wintypes

from . import winapi

_cache = {}


def clear_cache():
    _cache.clear()


def volume_root(path):
    buf = ctypes.create_unicode_buffer(len(path) + 2)
    winapi.GetVolumePathNameW(path, buf, len(buf))
    return buf.value


def volume_flags(path, use_cache=False):
    root = volume_root(path)
    key = root.upper()
    if use_cache and key in _cache:
        return _cache[key]

    fs_flags = wintypes.DWORD(0)
    name_buf = ctypes.create_unicode_buffer(261)
    winapi.GetVolumeInformationW(
        root, None, 0, None, None, ctypes.byref(fs_flags), name_buf, len(name_buf)
    )
    flags = fs_flags.value
    if use_cache:
        _cache[key] = flags
    return flags
