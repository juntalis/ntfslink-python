import struct

import pytest

from ntfslink import _mft

_ATTRIBUTE_HEADER = struct.Struct('<IIBBHHH')
_RESIDENT_HEADER = struct.Struct('<IHH')
_FILENAME_ATTRIBUTE_HEAD = struct.Struct('<QQQQQQQIIBB')
_FILE_RECORD_HEADER = struct.Struct('<4sHHqHHHHIIQH')
_OUTPUT_BUFFER_HEADER = struct.Struct('<qI')

ATTRIBUTE_TYPE_FILE_NAME = 0x30
ATTRS_OFFSET = 56


def _build_filename_attribute(name, parent_frn, name_type, attr_number):
    name_bytes = name.encode('utf-16-le')
    value = _FILENAME_ATTRIBUTE_HEAD.pack(
        parent_frn, 0, 0, 0, 0, 0, 0, 0, 0, len(name), name_type
    ) + name_bytes
    resident = _RESIDENT_HEADER.pack(len(value), _ATTRIBUTE_HEADER.size + _RESIDENT_HEADER.size, 0)
    attr_length = _ATTRIBUTE_HEADER.size + len(resident) + len(value)
    header = _ATTRIBUTE_HEADER.pack(
        ATTRIBUTE_TYPE_FILE_NAME, attr_length, 0, 0, 0, 0, attr_number
    )
    return header + resident + value


def _build_file_record(filename_entries):
    attrs = b''.join(
        _build_filename_attribute(name, parent_frn, name_type, i)
        for i, (name, parent_frn, name_type) in enumerate(filename_entries)
    )
    bytes_in_use = ATTRS_OFFSET + len(attrs)
    record = _FILE_RECORD_HEADER.pack(
        b'FILE', 0, 0, 0, 1, len(filename_entries),
        ATTRS_OFFSET, 0, bytes_in_use, 1024, 0, len(filename_entries),
    )
    record += b'\x00' * (ATTRS_OFFSET - len(record))
    record += attrs
    return _OUTPUT_BUFFER_HEADER.pack(0, len(record)) + record


def test_single_hardlink():
    raw = _build_file_record([('file.txt', 100, 1)])
    result = list(_mft.parse_filename_attributes(raw))
    assert result == [('file.txt', 100, 1)]


def test_multiple_hardlinks_different_parents():
    raw = _build_file_record([
        ('link_one.txt', 100, 1),
        ('link_two.txt', 200, 1),
    ])
    result = list(_mft.parse_filename_attributes(raw))
    assert result == [('link_one.txt', 100, 1), ('link_two.txt', 200, 1)]


def test_short_and_long_name_pair_both_present():
    # NTFS stores a DOS(2) short-name alias alongside the WIN32(1) long
    # name for the same link/parent when the name isn't 8.3-compatible —
    # parse_filename_attributes must yield both raw entries; deduplication
    # is the caller's (hardlinks.py's) job, filtering out NameType == DOS.
    raw = _build_file_record([
        ('LONGFI~1.TXT', 100, 2),
        ('a rather long file name.txt', 100, 1),
    ])
    result = list(_mft.parse_filename_attributes(raw))
    assert result == [
        ('LONGFI~1.TXT', 100, 2),
        ('a rather long file name.txt', 100, 1),
    ]
    non_dos = [r for r in result if r[2] != 2]
    assert len(non_dos) == 1


def test_win32_and_dos_combined_name_type():
    raw = _build_file_record([('short.txt', 100, 3)])
    result = list(_mft.parse_filename_attributes(raw))
    assert result == [('short.txt', 100, 3)]


def test_parent_frn_masks_sequence_number_bits():
    high_seq_frn = 0x1234000000000005  # sequence number in top 16 bits, FRN 5 in low 48
    raw = _build_file_record([('root_child.txt', high_seq_frn, 1)])
    result = list(_mft.parse_filename_attributes(raw))
    assert result[0][1] == 5


def test_bad_magic_raises():
    record = _FILE_RECORD_HEADER.pack(b'BAD!', 0, 0, 0, 0, 0, 56, 0, 56, 1024, 0, 0)
    raw = _OUTPUT_BUFFER_HEADER.pack(0, len(record)) + record
    with pytest.raises(ValueError):
        list(_mft.parse_filename_attributes(raw))


def test_no_filename_attributes_yields_empty():
    raw = _build_file_record([])
    assert list(_mft.parse_filename_attributes(raw)) == []
