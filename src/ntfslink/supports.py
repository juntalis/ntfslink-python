"""Filesystem/OS capability queries."""
from . import _consts as consts
from ._osversion import is_vista_or_later
from .backend import get_backend


def hardlinks(path=None, use_cache=False, backend=None, version=None):
    """Hard links have been supported by NTFS since Windows 2000; the
    ``FILE_SUPPORTS_HARD_LINKS`` volume flag wasn't introduced until
    Windows 7, so treat any older system as supporting them."""
    if path is None or not is_vista_or_later(version):
        return True
    backend = backend or get_backend()
    flags = backend.query_volume_flags(path, use_cache)
    return bool(flags & consts.FILE_SUPPORTS_HARD_LINKS)


def reparse_points(path=None, use_cache=False, backend=None):
    if path is None:
        return True
    backend = backend or get_backend()
    flags = backend.query_volume_flags(path, use_cache)
    return bool(flags & consts.FILE_SUPPORTS_REPARSE_POINTS)


def junctions(path=None, use_cache=False, backend=None):
    return reparse_points(path, use_cache, backend)


def symlinks(path=None, use_cache=False, backend=None, version=None):
    if not is_vista_or_later(version):
        return False
    if path is None:
        return True
    return reparse_points(path, use_cache, backend)
