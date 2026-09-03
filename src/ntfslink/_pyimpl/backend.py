"""Assembles the pure-Python (``ctypes``-Win32-call) backend.

The two selectable buffer codecs (``ctypes`` vs ``struct``, see
buffer_ctypes.py / buffer_struct.py) share every other primitive here,
since the choice between them only ever affects reparse-buffer packing.
"""
import contextlib
import ctypes
import struct
import types
from ctypes import wintypes

from .. import _consts as consts
from . import privileges, volumes, winapi

_HEADER_ONLY = struct.Struct('<IHH')


@contextlib.contextmanager
def _open_handle(path, access, disposition=consts.OPEN_EXISTING,
                  flags=consts.FILE_FLAG_REPARSE_BACKUP):
    privileges.ensure_privileges()
    handle = winapi.CreateFileW(
        path, access, consts.FILE_SHARE_ALL, None,
        disposition, flags, None,
    )
    try:
        yield handle
    finally:
        winapi.CloseHandle(handle)


def set_reparse_point(path, buffer):
    with _open_handle(path, consts.GENERIC_WRITE) as handle:
        bytes_returned = wintypes.DWORD(0)
        winapi.DeviceIoControl(
            handle, consts.FSCTL_SET_REPARSE_POINT,
            ctypes.c_char_p(buffer), len(buffer),
            None, 0, ctypes.byref(bytes_returned), None,
        )


def get_reparse_buffer(path):
    out_buf = ctypes.create_string_buffer(consts.MAX_REPARSE_BUFFER_SIZE)
    with _open_handle(path, consts.GENERIC_READ) as handle:
        bytes_returned = wintypes.DWORD(0)
        winapi.DeviceIoControl(
            handle, consts.FSCTL_GET_REPARSE_POINT, None, 0,
            out_buf, len(out_buf), ctypes.byref(bytes_returned), None,
        )
        return out_buf.raw[:bytes_returned.value]


def delete_reparse_point_ioctl(path, tag):
    header = _HEADER_ONLY.pack(tag, 0, 0)
    with _open_handle(path, consts.GENERIC_WRITE) as handle:
        bytes_returned = wintypes.DWORD(0)
        winapi.DeviceIoControl(
            handle, consts.FSCTL_DELETE_REPARSE_POINT,
            ctypes.c_char_p(header), len(header),
            None, 0, ctypes.byref(bytes_returned), None,
        )


def create_hard_link(src, dst):
    winapi.CreateHardLinkW(dst, src, None)


def _file_info(path):
    info = winapi.BY_HANDLE_FILE_INFORMATION()
    with _open_handle(path, 0x80000000, flags=consts.FILE_FLAG_BACKUP_SEMANTICS) as handle:
        winapi.GetFileInformationByHandle(handle, ctypes.byref(info))
    return info


def get_link_count(path):
    return _file_info(path).nNumberOfLinks


def get_file_reference_number(path):
    info = _file_info(path)
    return (info.nFileIndexHigh << 32) | info.nFileIndexLow


def _volume_device_path(volume_root_path):
    drive = volume_root_path.rstrip('\\')
    return f'\\\\.\\{drive}'


def get_ntfs_file_record(volume_root_path, file_reference_number):
    device_path = _volume_device_path(volume_root_path)
    input_buf = struct.pack('<q', file_reference_number)
    out_size = consts.MAX_REPARSE_BUFFER_SIZE
    out_buf = ctypes.create_string_buffer(out_size)
    with _open_handle(device_path, 0x80000000, flags=0) as handle:
        bytes_returned = wintypes.DWORD(0)
        winapi.DeviceIoControl(
            handle, consts.FSCTL_GET_NTFS_FILE_RECORD,
            ctypes.c_char_p(input_buf), len(input_buf),
            out_buf, out_size, ctypes.byref(bytes_returned), None,
        )
        return out_buf.raw[:bytes_returned.value]


def query_volume_flags(path, use_cache=False):
    return volumes.volume_flags(path, use_cache)


def ensure_privileges():
    privileges.ensure_privileges()


def make_backend(codec):
    if codec == 'ctypes':
        from . import buffer_ctypes as codec_module
    elif codec == 'struct':
        from . import buffer_struct as codec_module
    else:
        raise ValueError(f'Unknown pure-Python codec: {codec!r}')

    return types.SimpleNamespace(
        kind=codec,
        build_reparse_buffer=codec_module.build_reparse_buffer,
        parse_reparse_buffer=codec_module.parse_reparse_buffer,
        set_reparse_point=set_reparse_point,
        get_reparse_buffer=get_reparse_buffer,
        delete_reparse_point_ioctl=delete_reparse_point_ioctl,
        create_hard_link=create_hard_link,
        get_link_count=get_link_count,
        get_file_reference_number=get_file_reference_number,
        get_ntfs_file_record=get_ntfs_file_record,
        query_volume_flags=query_volume_flags,
        ensure_privileges=ensure_privileges,
        volume_root=volumes.volume_root,
    )
