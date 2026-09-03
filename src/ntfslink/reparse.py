"""Junction/symlink creation, reading, and deletion.

This orchestration (path validation, placeholder creation + rollback,
exception translation) is written once here and works identically no
matter which backend (cext / ctypes / struct) supplies the low-level
build_reparse_buffer/parse_reparse_buffer/set_reparse_point/
get_reparse_buffer/delete_reparse_point_ioctl primitives.
"""
import os

from . import _consts as consts
from ._attrs import is_directory_entry, is_reparse_point_safe
from .backend import get_backend
from .exceptions import InvalidLinkError, InvalidTargetError


def _substitute_and_print_names(tag, target):
    if tag == consts.IO_REPARSE_TAG_SYMLINK and not os.path.isabs(target):
        return target, target, consts.SYMBOLIC_LINK_FLAG_RELATIVE
    abs_target = os.path.abspath(target)
    return consts.PATHNAME_PREFIX + abs_target, abs_target, 0


def create_junction(src, dst, backend=None):
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


def create_symlink(src, dst, target_is_directory=None, backend=None):
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


def read_link(path, backend=None):
    backend = backend or get_backend()
    if not is_reparse_point_safe(path):
        raise InvalidLinkError(path, 'Path is not a reparse point!')

    raw = backend.get_reparse_buffer(path)
    tag, _flags, subst_name, _print_name = backend.parse_reparse_buffer(raw)
    if tag not in (consts.IO_REPARSE_TAG_MOUNT_POINT, consts.IO_REPARSE_TAG_SYMLINK):
        raise NotImplementedError(f'Unsupported reparse tag: 0x{tag:08X}')
    return consts.strip_pathname_prefix(subst_name)


def delete_reparse_point(path, backend=None):
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


def is_junction(path, backend=None):
    return _tag_is(path, backend or get_backend(), consts.IO_REPARSE_TAG_MOUNT_POINT)


def is_symlink(path, backend=None):
    return _tag_is(path, backend or get_backend(), consts.IO_REPARSE_TAG_SYMLINK)


def _tag_is(path, backend, expected_tag):
    if not is_reparse_point_safe(path):
        return False
    raw = backend.get_reparse_buffer(path)
    tag = raw[0] | (raw[1] << 8) | (raw[2] << 16) | (raw[3] << 24)
    return tag == expected_tag
