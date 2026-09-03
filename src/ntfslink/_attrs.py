"""Cheap file-attribute checks that don't need a backend (no perf-sensitive
or codec-dependent work involved, just one GetFileAttributesW call)."""
import ctypes
from ctypes import wintypes

from . import _consts as consts

_GetFileAttributesW = ctypes.WinDLL('kernel32', use_last_error=True).GetFileAttributesW
_GetFileAttributesW.restype = wintypes.DWORD
_GetFileAttributesW.argtypes = (wintypes.LPCWSTR,)


def get_file_attributes(path):
    return _GetFileAttributesW(path)


def is_reparse_point(path):
    attrs = get_file_attributes(path)
    if attrs == consts.INVALID_FILE_ATTRIBUTES:
        raise ctypes.WinError(ctypes.get_last_error())
    return bool(attrs & consts.FILE_ATTRIBUTE_REPARSE_POINT)


def is_directory_entry(path):
    """Whether ``path``'s own on-disk entry is directory-typed, without
    following a reparse point to check its target (unlike
    ``os.path.isdir``, which would misreport a dangling directory
    junction/symlink as not-a-directory)."""
    attrs = get_file_attributes(path)
    if attrs == consts.INVALID_FILE_ATTRIBUTES:
        raise ctypes.WinError(ctypes.get_last_error())
    return bool(attrs & consts.FILE_ATTRIBUTE_DIRECTORY)


def is_reparse_point_safe(path):
    """Like ``is_reparse_point``, but ``False`` instead of raising when
    ``path`` doesn't exist. Uses GetFileAttributesW directly (not
    ``os.path.exists``/``os.stat``, which follow the reparse point and
    would misreport a dangling link's own presence as "doesn't exist")."""
    attrs = get_file_attributes(path)
    if attrs == consts.INVALID_FILE_ATTRIBUTES:
        return False
    return bool(attrs & consts.FILE_ATTRIBUTE_REPARSE_POINT)
