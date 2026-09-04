"""Cheap file-attribute checks that don't need a backend (no perf-sensitive
or codec-dependent work involved, just one GetFileAttributesW call)."""
from __future__ import annotations

import ctypes

from . import _consts as consts
from ._pyimpl.winapi import GetFileAttributesW


def get_file_attributes(path: str) -> int:
    return int(GetFileAttributesW(path))


def is_reparse_point(path: str) -> bool:
    attrs = get_file_attributes(path)
    if attrs == consts.INVALID_FILE_ATTRIBUTES:
        raise ctypes.WinError(ctypes.get_last_error())
    return bool(attrs & consts.FILE_ATTRIBUTE_REPARSE_POINT)


def is_directory_entry(path: str) -> bool:
    """Whether ``path``'s own on-disk entry is directory-typed, without
    following a reparse point to check its target (unlike
    ``os.path.isdir``, which would misreport a dangling directory
    junction/symlink as not-a-directory)."""
    attrs = get_file_attributes(path)
    if attrs == consts.INVALID_FILE_ATTRIBUTES:
        raise ctypes.WinError(ctypes.get_last_error())
    return bool(attrs & consts.FILE_ATTRIBUTE_DIRECTORY)


def is_reparse_point_safe(path: str) -> bool:
    """Like ``is_reparse_point``, but ``False`` instead of raising when
    ``path`` doesn't exist. Uses GetFileAttributesW directly (not
    ``os.path.exists``/``os.stat``, which follow the reparse point and
    would misreport a dangling link's own presence as "doesn't exist")."""
    attrs = get_file_attributes(path)
    if attrs == consts.INVALID_FILE_ATTRIBUTES:
        return False
    return bool(attrs & consts.FILE_ATTRIBUTE_REPARSE_POINT)
