"""Pure-Python parsing of raw NTFS MFT file-record bytes.

Shared by every backend: whichever backend fetches the raw
``NTFS_FILE_RECORD_OUTPUT_BUFFER`` bytes (see ``get_ntfs_file_record`` in
``_pyimpl/backend.py`` or the C extension), parsing them into hard-link
``(name, parent_frn, name_type)`` triples is plain byte-crunching with no
Win32 call involved, so it lives here once. Field layout matches the
on-disk NTFS FILE record format (unchanged since NTFS 3.1 / Windows 2000),
not any particular C struct someone hand-typed from a header.
"""
from __future__ import annotations

import struct
from typing import Iterator

from . import _consts as consts

# NTFS_FILE_RECORD_OUTPUT_BUFFER: LARGE_INTEGER FileReferenceNumber; DWORD FileRecordLength;
_OUTPUT_BUFFER_HEADER = struct.Struct('<qI')

# FILE record header, up to and including NextAttributeNumber (42 bytes, no
# compiler padding — every field falls on a naturally-aligned offset):
#   4s magic("FILE") | H usaOffset | H usaCount | q lsn
#   H sequenceNumber | H linkCount | H attributesOffset | H flags
#   I bytesInUse | I bytesAllocated | Q baseFileRecord | H nextAttributeNumber
_FILE_RECORD_HEADER = struct.Struct('<4sHHqHHHHIIQH')

# Common ATTRIBUTE header (16 bytes): type | length | nonresident | nameLength
# | nameOffset | flags | attributeNumber
_ATTRIBUTE_HEADER = struct.Struct('<IIBBHHH')

# Resident-attribute extension (8 bytes, right after the common header):
# ULONG valueLength | USHORT valueOffset | USHORT residentFlags
_RESIDENT_HEADER = struct.Struct('<IHH')

# $FILE_NAME attribute value, fixed portion (66 bytes) before the WCHAR name:
_FILENAME_ATTRIBUTE_HEAD = struct.Struct('<QQQQQQQIIBB')

_FRN_MASK = 0x0000FFFFFFFFFFFF


def _file_record_buffer(raw_output_buffer: bytes) -> bytes:
    return raw_output_buffer[_OUTPUT_BUFFER_HEADER.size:]


def parse_filename_attributes(raw_output_buffer: bytes) -> Iterator[tuple[str, int, int]]:
    """Yield ``(name, parent_frn, name_type)`` for every $FILE_NAME
    attribute in one MFT record (one entry per hard link, plus a
    duplicate short/8.3-name entry for names that aren't already
    8.3-compatible)."""
    record = _file_record_buffer(raw_output_buffer)

    magic, _usa_offset, _usa_count, _lsn, _sequence_number, _link_count, \
        attrs_offset, _flags, bytes_in_use, _bytes_allocated, \
        _base_record, _next_attr_num = _FILE_RECORD_HEADER.unpack_from(record, 0)

    if magic != b'FILE':
        raise ValueError('Not an NTFS MFT file record (bad magic)')

    offset = attrs_offset
    while offset < bytes_in_use:
        attr_type, attr_length, nonresident, _name_length, _name_offset, \
            _attr_flags, _attr_number = _ATTRIBUTE_HEADER.unpack_from(record, offset)
        if attr_type == consts.ATTRIBUTE_TYPE_END or attr_length == 0:
            break

        if attr_type == consts.ATTRIBUTE_TYPE_FILE_NAME and not nonresident:
            _value_length, value_offset, _resident_flags = \
                _RESIDENT_HEADER.unpack_from(record, offset + _ATTRIBUTE_HEADER.size)
            value_offset += offset

            parent_frn, _creation_time, _change_time, _last_write_time, \
                _last_access_time, _allocated_size, _data_size, _file_attrs, \
                _reserved, name_length, name_type = \
                _FILENAME_ATTRIBUTE_HEAD.unpack_from(record, value_offset)

            parent_frn &= _FRN_MASK
            name_start = value_offset + _FILENAME_ATTRIBUTE_HEAD.size
            name = record[name_start:name_start + name_length * 2].decode('utf-16-le')
            yield name, parent_frn, name_type

        offset += attr_length
