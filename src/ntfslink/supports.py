"""Filesystem/OS capability queries."""
from __future__ import annotations

from typing import Optional

from . import _consts as consts
from ._osversion import is_vista_or_later
from .backend import OptBackend, get_backend


def hardlinks(
    path: Optional[str] = None, use_cache: bool = False,
    backend: OptBackend = None, version: Optional[tuple[int, int]] = None,
) -> bool:
    """Hard links have been supported by NTFS since Windows 2000; the
    ``FILE_SUPPORTS_HARD_LINKS`` volume flag wasn't introduced until
    Windows 7, so treat any older system as supporting them."""
    if path is None or not is_vista_or_later(version):
        return True
    backend = backend or get_backend()
    flags = backend.query_volume_flags(path, use_cache)
    return bool(flags & consts.FILE_SUPPORTS_HARD_LINKS)


def reparse_points(path: Optional[str] = None, use_cache: bool = False, backend: OptBackend = None) -> bool:
    """Whether the volume containing ``path`` supports reparse points at
    all (the mechanism underlying both junctions and symbolic links).

    :param path: Path (any path on the volume of interest) to check.
        When omitted, asks for the platform-level default (``True``).
    :param use_cache: Reuse a previously queried volume-flags result for
        this volume instead of re-querying.
    :param backend: Backend override, primarily useful for testing.
    """
    if path is None:
        return True
    backend = backend or get_backend()
    flags = backend.query_volume_flags(path, use_cache)
    return bool(flags & consts.FILE_SUPPORTS_REPARSE_POINTS)


def junctions(path: Optional[str] = None, use_cache: bool = False, backend: OptBackend = None) -> bool:
    """Whether the volume containing ``path`` supports directory junctions.

    Junctions are reparse points, so this is currently equivalent to
    :func:`reparse_points` and unlike :func:`symlinks`, doesn't require
    Windows Vista or later.

    :param path: Path (any path on the volume of interest) to check.
        When omitted, asks for the platform-level default (``True``).
    :param use_cache: Reuse a previously queried volume-flags result for
        this volume instead of re-querying.
    :param backend: Backend override, primarily useful for testing.
    """
    return reparse_points(path, use_cache, backend)


def symlinks(
    path: Optional[str] = None, use_cache: bool = False,
    backend: OptBackend = None, version: Optional[tuple[int, int]] = None,
) -> bool:
    """Whether the volume containing ``path`` supports symbolic links.

    Symbolic links require Windows Vista or later in addition to
    reparse-point support on the volume itself.

    :param path: Path (any path on the volume of interest) to check.
        When omitted, asks for the platform-level default.
    :param use_cache: Reuse a previously queried volume-flags result for
        this volume instead of re-querying.
    :param backend: Backend override, primarily useful for testing.
    :param version: ``(major, minor)`` override for the OS version check,
        primarily useful for testing. Defaults to the running system's
        version.
    """
    if not is_vista_or_later(version):
        return False
    if path is None:
        return True
    return reparse_points(path, use_cache, backend)
