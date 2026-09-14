"""Junction/symlink creation, reading, and deletion.

This orchestration (path validation, placeholder creation + rollback,
exception translation) is written once here and works identically no
matter which backend (cext / ctypes / struct) supplies the low-level
build_reparse_buffer/parse_reparse_buffer/set_reparse_point/
get_reparse_buffer/delete_reparse_point_ioctl primitives.
"""
from __future__ import annotations

import os
from typing import Optional

from . import _consts as consts
from ._attrs import is_directory_entry, is_reparse_point_safe
from .backend import Backend, OptBackend, get_backend
from .exceptions import InvalidLinkError, InvalidTargetError


def _substitute_and_print_names(tag: int, target: str) -> tuple[str, str, int]:
    if tag == consts.IO_REPARSE_TAG_SYMLINK and not os.path.isabs(target):
        return target, target, consts.SYMBOLIC_LINK_FLAG_RELATIVE
    abs_target = os.path.abspath(target)
    return consts.PATHNAME_PREFIX + abs_target, abs_target, 0


def create_junction(src: str, dst: str, backend: OptBackend = None) -> None:
    """Create a directory junction (mount point) at ``dst`` targeting ``src``.

    ``src`` must be an existing directory; ``dst`` must not already exist as
    a file. If ``dst`` does not exist, it is created and populated with the
    reparse point; if the reparse point fails to install, the created
    directory is rolled back and the underlying exception re-raised.

    Junction targets are always stored as absolute paths, so relative
    ``src`` values are resolved with :func:`os.path.abspath` before being
    written to the reparse buffer.

    :param src: Existing directory the junction should point to.
    :param dst: Path at which to create the junction.
    :param backend: Backend override, primarily useful for testing.
    :raises InvalidTargetError: ``src`` is a file, or does not exist.
    :raises InvalidLinkError: A file already exists at ``dst``.
    """
    backend = backend or get_backend()
    if os.path.isfile(src):
        raise InvalidTargetError(src, 'Junctions can only target directories!')
    if not os.path.isdir(src):
        raise InvalidTargetError(src, 'Junction target does not exist!')
    if os.path.isfile(dst):
        raise InvalidLinkError(dst, 'A file already exists at the junction path!')

    created = False
    if not os.path.isdir(dst):
        os.mkdir(dst)
        created = True

    try:
        subst, print_name, flags = _substitute_and_print_names(
            consts.IO_REPARSE_TAG_MOUNT_POINT, src
        )
        buffer = backend.build_reparse_buffer(
            consts.IO_REPARSE_TAG_MOUNT_POINT, subst, print_name, flags
        )
        backend.set_reparse_point(dst, buffer)
    except BaseException:
        if created:
            os.rmdir(dst)
        raise


def create_symlink(
    src: str, dst: str, target_is_directory: Optional[bool] = None, backend: OptBackend = None,
) -> None:
    """Create a file or directory symbolic link at ``dst`` targeting ``src``.

    Unlike junctions, symlink targets may be relative; a relative ``src``
    is stored verbatim (interpreted relative to ``dst``'s directory at
    resolution time), while an absolute ``src`` is normalized with
    :func:`os.path.abspath`.

    ``target_is_directory`` controls whether ``dst`` is created as a
    directory or file placeholder before the reparse point is attached.
    When omitted, it is inferred from whether ``src`` currently exists and
    is a directory — pass it explicitly when ``src`` does not exist yet.

    :param src: Path the symlink should point to. Existing or not.
    :param dst: Path at which to create the symlink.
    :param target_is_directory: Force directory- or file-mode symlink
        creation. Required when ``src`` doesn't exist yet.
    :param backend: Backend override, primarily useful for testing.
    :raises InvalidLinkError: A file, directory, or reparse point already
        exists at ``dst``.
    """
    backend = backend or get_backend()
    if target_is_directory is None:
        target_is_directory = os.path.isdir(src)

    if is_reparse_point_safe(dst) or os.path.exists(dst):
        raise InvalidLinkError(dst, 'A file/directory already exists at the symlink path!')

    if target_is_directory:
        os.mkdir(dst)
    else:
        open(dst, 'xb').close()

    try:
        subst, print_name, flags = _substitute_and_print_names(
            consts.IO_REPARSE_TAG_SYMLINK, src
        )
        buffer = backend.build_reparse_buffer(
            consts.IO_REPARSE_TAG_SYMLINK, subst, print_name, flags
        )
        backend.set_reparse_point(dst, buffer)
    except BaseException:
        if target_is_directory:
            os.rmdir(dst)
        else:
            os.remove(dst)
        raise


def read_link(path: str, backend: OptBackend = None) -> str:
    """Return the target path stored in a junction or symbolic link.

    :param path: Path to a junction or symbolic link.
    :param backend: Backend override, primarily useful for testing.
    :returns: The link's target, with any internal ``\\\\??\\`` device
        prefix stripped.
    :raises InvalidLinkError: ``path`` is not a reparse point.
    :raises NotImplementedError: ``path`` is a reparse point of a type
        other than a junction or symbolic link.
    """
    backend = backend or get_backend()
    if not is_reparse_point_safe(path):
        raise InvalidLinkError(path, 'Path is not a reparse point!')

    raw = backend.get_reparse_buffer(path)
    tag, _flags, subst_name, _print_name = backend.parse_reparse_buffer(raw)
    if tag not in (consts.IO_REPARSE_TAG_MOUNT_POINT, consts.IO_REPARSE_TAG_SYMLINK):
        raise NotImplementedError(f'Unsupported reparse tag: 0x{tag:08X}')
    return consts.strip_pathname_prefix(subst_name)


def delete_reparse_point(path: str, backend: OptBackend = None) -> None:
    """Remove a junction or symbolic link and its on-disk placeholder.

    The reparse point is detached via the appropriate ``FSCTL`` before the
    now-plain placeholder (directory or file) is removed, so this cleans
    up both the link and the empty directory/file it was attached to.

    :param path: Path to a junction or symbolic link.
    :param backend: Backend override, primarily useful for testing.
    :raises InvalidLinkError: ``path`` is not a reparse point.
    """
    backend = backend or get_backend()
    if not is_reparse_point_safe(path):
        raise InvalidLinkError(path, 'Path is not a reparse point!')

    raw = backend.get_reparse_buffer(path)
    tag = raw[0] | (raw[1] << 8) | (raw[2] << 16) | (raw[3] << 24)
    was_dir = is_directory_entry(path)
    backend.delete_reparse_point_ioctl(path, tag)
    if was_dir:
        os.rmdir(path)
    else:
        os.remove(path)


def is_junction(path: str, backend: OptBackend = None) -> bool:
    """Return whether ``path`` is a directory junction (mount point).

    Returns ``False`` (rather than raising) for a non-existent path or a
    reparse point of a different type.

    :param path: Path to check.
    :param backend: Backend override, primarily useful for testing.
    """
    return _tag_is(path, backend or get_backend(), consts.IO_REPARSE_TAG_MOUNT_POINT)


def is_symlink(path: str, backend: OptBackend = None) -> bool:
    """Return whether ``path`` is a file or directory symbolic link.

    Returns ``False`` (rather than raising) for a non-existent path or a
    reparse point of a different type.

    :param path: Path to check.
    :param backend: Backend override, primarily useful for testing.
    """
    return _tag_is(path, backend or get_backend(), consts.IO_REPARSE_TAG_SYMLINK)


def _tag_is(path: str, backend: Backend, expected_tag: int) -> bool:
    if not is_reparse_point_safe(path):
        return False
    raw = backend.get_reparse_buffer(path)
    tag = raw[0] | (raw[1] << 8) | (raw[2] << 16) | (raw[3] << 24)
    return tag == expected_tag
