"""REPARSE_DATA_BUFFER (de)serialization using the stdlib ``struct`` module.

One of two interchangeable buffer codecs (see buffer_ctypes.py for the
ctypes.Structure-based alternative) benchmarked against each other in
benchmarks/bench_backends.py to decide which becomes the maintained
pure-Python fallback.
"""
from __future__ import annotations

import struct

from .. import _consts as consts

WCHAR_SIZE = 2

_HEADER = struct.Struct('<IHH')
_MOUNT_POINT_HEADER = struct.Struct('<HHHH')
_SYMLINK_HEADER = struct.Struct('<HHHHI')


def build_reparse_buffer(tag: int, subst_name: str, print_name: str, flags: int = 0) -> bytes:
    subst_bytes = subst_name.encode('utf-16-le')
    print_bytes = print_name.encode('utf-16-le')

    if tag == consts.IO_REPARSE_TAG_MOUNT_POINT:
        buf_header = _MOUNT_POINT_HEADER.pack(
            0, len(subst_bytes), len(subst_bytes) + WCHAR_SIZE, len(print_bytes)
        )
        # Windows' own junctions put a null wchar between the substitute
        # and print names *and* a trailing one after the print name (not
        # counted in PrintNameLength) — match that exactly for
        # interop with junctions created/read by other tools.
        path_buffer = subst_bytes + b'\x00\x00' + print_bytes + b'\x00\x00'
    elif tag == consts.IO_REPARSE_TAG_SYMLINK:
        buf_header = _SYMLINK_HEADER.pack(
            0, len(subst_bytes), len(subst_bytes), len(print_bytes), flags
        )
        path_buffer = subst_bytes + print_bytes
    else:
        raise NotImplementedError(f'Unsupported reparse tag: 0x{tag:08X}')

    data_length = len(buf_header) + len(path_buffer)
    header = _HEADER.pack(tag, data_length, 0)
    return header + buf_header + path_buffer


def parse_reparse_buffer(data: bytes) -> tuple[int, int, str, str]:
    data = bytes(data)
    tag, _length, _reserved = _HEADER.unpack_from(data, 0)
    offset = _HEADER.size

    if tag == consts.IO_REPARSE_TAG_MOUNT_POINT:
        so, sl, po, pl = _MOUNT_POINT_HEADER.unpack_from(data, offset)
        flags = 0
        path_offset = offset + _MOUNT_POINT_HEADER.size
    elif tag == consts.IO_REPARSE_TAG_SYMLINK:
        so, sl, po, pl, flags = _SYMLINK_HEADER.unpack_from(data, offset)
        path_offset = offset + _SYMLINK_HEADER.size
    else:
        raise NotImplementedError(f'Unsupported reparse tag: 0x{tag:08X}')

    path_data = data[path_offset:]
    subst_name = path_data[so:so + sl].decode('utf-16-le')
    print_name = path_data[po:po + pl].decode('utf-16-le')
    return tag, flags, subst_name, print_name
