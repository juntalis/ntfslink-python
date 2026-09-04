"""Hard link creation and enumeration.

Enumeration works back to Windows XP SP2: it walks raw NTFS MFT records
via FSCTL_GET_NTFS_FILE_RECORD instead of relying on the Vista-only
FindFirstFileNameW/FindNextFileNameW APIs. See Prompt.md ("Hardlink
creation and enumeration, and the Windows XP SP2 baseline") for the full
rationale.
"""
from __future__ import annotations

import os
from typing import Dict, List

from . import _consts as consts
from . import _mft
from .backend import Backend, OptBackend, get_backend
from .exceptions import InvalidLinkError, InvalidTargetError


def create_hardlink(src: str, dst: str, backend: OptBackend = None) -> None:
    backend = backend or get_backend()
    if not os.path.exists(src):
        raise InvalidTargetError(src, 'Hard link source does not exist!')
    if os.path.isdir(src):
        raise InvalidTargetError(src, 'Hard links to directories are not supported by NTFS!')
    if os.path.exists(dst):
        raise InvalidLinkError(dst, 'A file already exists at the hard link path!')

    backend.create_hard_link(src, dst)


def hardlink_count(path: str, backend: OptBackend = None) -> int:
    backend = backend or get_backend()
    return backend.get_link_count(path)


def _resolve_directory_path(
    frn: int, volume_root: str, backend: Backend, cache: Dict[int, str],
) -> str:
    if frn == consts.NTFS_ROOT_DIRECTORY_FRN:
        return volume_root
    if frn in cache:
        return cache[frn]

    raw = backend.get_ntfs_file_record(volume_root, frn)
    name, parent_frn, _name_type = next(
        attr for attr in _mft.parse_filename_attributes(raw)
        if attr[2] != consts.NTFS_FILENAME_TYPE_DOS
    )
    parent_path = _resolve_directory_path(parent_frn, volume_root, backend, cache)
    full_path = os.path.join(parent_path, name)
    cache[frn] = full_path
    return full_path


def enumerate_hardlinks(path: str, backend: OptBackend = None) -> List[str]:
    backend = backend or get_backend()
    volume_root = backend.volume_root(path)
    frn = backend.get_file_reference_number(path)
    raw = backend.get_ntfs_file_record(volume_root, frn)

    cache: Dict[int, str] = {}
    paths = []
    for name, parent_frn, name_type in _mft.parse_filename_attributes(raw):
        if name_type == consts.NTFS_FILENAME_TYPE_DOS:
            continue
        parent_path = _resolve_directory_path(parent_frn, volume_root, backend, cache)
        paths.append(os.path.join(parent_path, name))
    return paths
