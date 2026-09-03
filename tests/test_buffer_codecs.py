import pytest

from ntfslink import _consts as consts
from ntfslink._pyimpl import buffer_ctypes, buffer_struct

CODECS = [buffer_ctypes, buffer_struct]


@pytest.fixture(params=CODECS, ids=['ctypes', 'struct'])
def codec(request):
    return request.param


def test_mount_point_roundtrip(codec):
    subst = '\\??\\C:\\real\\target\\'
    print_name = 'C:\\real\\target\\'
    buf = codec.build_reparse_buffer(consts.IO_REPARSE_TAG_MOUNT_POINT, subst, print_name)
    tag, flags, out_subst, out_print = codec.parse_reparse_buffer(buf)
    assert tag == consts.IO_REPARSE_TAG_MOUNT_POINT
    assert flags == 0
    assert out_subst == subst
    assert out_print == print_name


def test_symlink_absolute_roundtrip(codec):
    subst = '\\??\\C:\\real\\target.txt'
    print_name = 'C:\\real\\target.txt'
    buf = codec.build_reparse_buffer(
        consts.IO_REPARSE_TAG_SYMLINK, subst, print_name, flags=0
    )
    tag, flags, out_subst, out_print = codec.parse_reparse_buffer(buf)
    assert tag == consts.IO_REPARSE_TAG_SYMLINK
    assert flags == 0
    assert out_subst == subst
    assert out_print == print_name


def test_symlink_relative_roundtrip(codec):
    subst = print_name = 'relative\\target.txt'
    buf = codec.build_reparse_buffer(
        consts.IO_REPARSE_TAG_SYMLINK, subst, print_name,
        flags=consts.SYMBOLIC_LINK_FLAG_RELATIVE,
    )
    tag, flags, out_subst, out_print = codec.parse_reparse_buffer(buf)
    assert tag == consts.IO_REPARSE_TAG_SYMLINK
    assert flags == consts.SYMBOLIC_LINK_FLAG_RELATIVE
    assert out_subst == subst
    assert out_print == print_name


def test_unsupported_tag_build_raises(codec):
    with pytest.raises(NotImplementedError):
        codec.build_reparse_buffer(0xDEADBEEF, 'a', 'b')


def test_unsupported_tag_parse_raises(codec):
    import struct
    bogus = struct.pack('<IHH', 0xDEADBEEF, 0, 0)
    with pytest.raises(NotImplementedError):
        codec.parse_reparse_buffer(bogus)


def test_empty_names_roundtrip(codec):
    buf = codec.build_reparse_buffer(consts.IO_REPARSE_TAG_SYMLINK, '', '')
    tag, flags, subst, print_name = codec.parse_reparse_buffer(buf)
    assert subst == ''
    assert print_name == ''


def test_both_codecs_produce_identical_bytes_for_symlink():
    subst = '\\??\\C:\\a\\b.txt'
    print_name = 'C:\\a\\b.txt'
    a = buffer_ctypes.build_reparse_buffer(consts.IO_REPARSE_TAG_SYMLINK, subst, print_name)
    b = buffer_struct.build_reparse_buffer(consts.IO_REPARSE_TAG_SYMLINK, subst, print_name)
    assert a == b


def test_both_codecs_produce_identical_bytes_for_mount_point():
    subst = '\\??\\C:\\a\\b\\'
    print_name = 'C:\\a\\b\\'
    a = buffer_ctypes.build_reparse_buffer(consts.IO_REPARSE_TAG_MOUNT_POINT, subst, print_name)
    b = buffer_struct.build_reparse_buffer(consts.IO_REPARSE_TAG_MOUNT_POINT, subst, print_name)
    assert a == b
