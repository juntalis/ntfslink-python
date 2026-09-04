"""Volume path/capability-flag queries, with an opt-in cache."""
from __future__ import annotations

import ctypes
from ctypes import wintypes
from typing import Dict

from . import winapi

_cache: Dict[str, int] = {}


def clear_cache() -> None:
    _cache.clear()


def volume_root(path: str) -> str:
    buf = ctypes.create_unicode_buffer(len(path) + 2)
    winapi.GetVolumePathNameW(path, buf, len(buf))
    return buf.value


def volume_flags(path: str, use_cache: bool = False) -> int:
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
