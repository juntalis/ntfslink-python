"""REPARSE_DATA_BUFFER (de)serialization using ctypes.Structure/Union.

One of two interchangeable buffer codecs (see buffer_struct.py for the
stdlib-``struct``-based alternative) benchmarked against each other in
benchmarks/bench_backends.py to decide which becomes the maintained
pure-Python fallback.
"""
from __future__ import annotations

import ctypes
from typing import Union

from .. import _consts as consts

WCHAR_SIZE = ctypes.sizeof(ctypes.c_wchar)

_HEADER_FMT = ('ReparseTag', 'ReparseDataLength', 'Reserved')


class _Header(ctypes.Structure):
    _fields_ = [
        ('ReparseTag', ctypes.c_uint32),
        ('ReparseDataLength', ctypes.c_uint16),
        ('Reserved', ctypes.c_uint16),
    ]


class _MountPointHeader(ctypes.Structure):
    _fields_ = [
        ('SubstituteNameOffset', ctypes.c_uint16),
        ('SubstituteNameLength', ctypes.c_uint16),
        ('PrintNameOffset', ctypes.c_uint16),
        ('PrintNameLength', ctypes.c_uint16),
    ]


class _SymlinkHeader(ctypes.Structure):
    _fields_ = [
        ('SubstituteNameOffset', ctypes.c_uint16),
        ('SubstituteNameLength', ctypes.c_uint16),
        ('PrintNameOffset', ctypes.c_uint16),
        ('PrintNameLength', ctypes.c_uint16),
        ('Flags', ctypes.c_uint32),
    ]


def build_reparse_buffer(tag: int, subst_name: str, print_name: str, flags: int = 0) -> bytes:
    subst_bytes = subst_name.encode('utf-16-le')
    print_bytes = print_name.encode('utf-16-le')

    buf_header: Union[_MountPointHeader, _SymlinkHeader]
    if tag == consts.IO_REPARSE_TAG_MOUNT_POINT:
        buf_header = _MountPointHeader(
            SubstituteNameOffset=0,
            SubstituteNameLength=len(subst_bytes),
            PrintNameOffset=len(subst_bytes) + WCHAR_SIZE,
            PrintNameLength=len(print_bytes),
        )
        # Windows' own junctions put a null wchar between the substitute
        # and print names *and* a trailing one after the print name (not
        # counted in PrintNameLength) — match that exactly for
        # interop with junctions created/read by other tools.
        path_buffer = subst_bytes + b'\x00\x00' + print_bytes + b'\x00\x00'
    elif tag == consts.IO_REPARSE_TAG_SYMLINK:
        buf_header = _SymlinkHeader(
            SubstituteNameOffset=0,
            SubstituteNameLength=len(subst_bytes),
            PrintNameOffset=len(subst_bytes),
            PrintNameLength=len(print_bytes),
            Flags=flags,
        )
        path_buffer = subst_bytes + print_bytes
    else:
        raise NotImplementedError(f'Unsupported reparse tag: 0x{tag:08X}')

    data_length = ctypes.sizeof(buf_header) + len(path_buffer)
    header = _Header(ReparseTag=tag, ReparseDataLength=data_length, Reserved=0)
    return bytes(header) + bytes(buf_header) + path_buffer


def parse_reparse_buffer(data: bytes) -> tuple[int, int, str, str]:
    header = _Header.from_buffer_copy(data, 0)
    offset = ctypes.sizeof(_Header)
    tag = header.ReparseTag

    buf_header: Union[_MountPointHeader, _SymlinkHeader]
    if tag == consts.IO_REPARSE_TAG_MOUNT_POINT:
        buf_header = _MountPointHeader.from_buffer_copy(data, offset)
        flags = 0
    elif tag == consts.IO_REPARSE_TAG_SYMLINK:
        buf_header = _SymlinkHeader.from_buffer_copy(data, offset)
        flags = buf_header.Flags
    else:
        raise NotImplementedError(f'Unsupported reparse tag: 0x{tag:08X}')

    path_offset = offset + ctypes.sizeof(buf_header)
    path_data = bytes(data)[path_offset:]

    so, sl = buf_header.SubstituteNameOffset, buf_header.SubstituteNameLength
    po, pl = buf_header.PrintNameOffset, buf_header.PrintNameLength
    subst_name = path_data[so:so + sl].decode('utf-16-le')
    print_name = path_data[po:po + pl].decode('utf-16-le')
    return tag, flags, subst_name, print_name
