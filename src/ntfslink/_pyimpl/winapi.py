"""Shared ctypes Win32 bindings used by both pure-Python buffer codecs."""
from __future__ import annotations

import ctypes
from ctypes import wintypes
from typing import Any, Callable, Tuple

from .. import exceptions

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
advapi32 = ctypes.WinDLL('advapi32', use_last_error=True)
ntdll = ctypes.WinDLL('ntdll', use_last_error=False)

INVALID_HANDLE_VALUE = wintypes.HANDLE(-1).value
LPOVERLAPPED = wintypes.LPVOID


def check_bool(result: Any, func: Callable[..., Any], args: Tuple[Any, ...]) -> Any:
    if not result:
        raise ctypes.WinError(ctypes.get_last_error())
    return args


def check_handle(result: Any, func: Callable[..., Any], args: Tuple[Any, ...]) -> Any:
    if not result or result == INVALID_HANDLE_VALUE:
        raise exceptions.InvalidHandleError(
            f'{func.__name__} returned an invalid handle '
            f'[LastError={ctypes.get_last_error()}]'
        )
    return result


# --- CreateFile / CloseHandle / DeviceIoControl -----------------------------

CreateFileW = kernel32.CreateFileW
CreateFileW.restype = wintypes.HANDLE
CreateFileW.argtypes = (
    wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
    wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
)
CreateFileW.errcheck = check_handle

CloseHandle = kernel32.CloseHandle
CloseHandle.restype = wintypes.BOOL
CloseHandle.argtypes = (wintypes.HANDLE,)
CloseHandle.errcheck = check_bool

DeviceIoControl = kernel32.DeviceIoControl
DeviceIoControl.restype = wintypes.BOOL
DeviceIoControl.argtypes = (
    wintypes.HANDLE, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD,
    wintypes.LPVOID, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), LPOVERLAPPED,
)
DeviceIoControl.errcheck = check_bool

GetFileAttributesW = kernel32.GetFileAttributesW
GetFileAttributesW.restype = wintypes.DWORD
GetFileAttributesW.argtypes = (wintypes.LPCWSTR,)

CreateHardLinkW = kernel32.CreateHardLinkW
CreateHardLinkW.restype = wintypes.BOOL
CreateHardLinkW.argtypes = (wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.LPVOID)
CreateHardLinkW.errcheck = check_bool


class FILETIME(ctypes.Structure):
    _fields_ = [('dwLowDateTime', wintypes.DWORD), ('dwHighDateTime', wintypes.DWORD)]


class BY_HANDLE_FILE_INFORMATION(ctypes.Structure):
    _fields_ = [
        ('dwFileAttributes', wintypes.DWORD),
        ('ftCreationTime', FILETIME),
        ('ftLastAccessTime', FILETIME),
        ('ftLastWriteTime', FILETIME),
        ('dwVolumeSerialNumber', wintypes.DWORD),
        ('nFileSizeHigh', wintypes.DWORD),
        ('nFileSizeLow', wintypes.DWORD),
        ('nNumberOfLinks', wintypes.DWORD),
        ('nFileIndexHigh', wintypes.DWORD),
        ('nFileIndexLow', wintypes.DWORD),
    ]


GetFileInformationByHandle = kernel32.GetFileInformationByHandle
GetFileInformationByHandle.restype = wintypes.BOOL
GetFileInformationByHandle.argtypes = (wintypes.HANDLE, ctypes.POINTER(BY_HANDLE_FILE_INFORMATION))
GetFileInformationByHandle.errcheck = check_bool

# --- Volume info -------------------------------------------------------------

GetVolumePathNameW = kernel32.GetVolumePathNameW
GetVolumePathNameW.restype = wintypes.BOOL
GetVolumePathNameW.argtypes = (wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD)
GetVolumePathNameW.errcheck = check_bool

GetVolumeInformationW = kernel32.GetVolumeInformationW
GetVolumeInformationW.restype = wintypes.BOOL
GetVolumeInformationW.argtypes = (
    wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(wintypes.DWORD),
    ctypes.POINTER(wintypes.DWORD), wintypes.LPWSTR, wintypes.DWORD,
)
GetVolumeInformationW.errcheck = check_bool

# --- Privileges ---------------------------------------------------------------


class LUID(ctypes.Structure):
    _fields_ = [('LowPart', wintypes.DWORD), ('HighPart', wintypes.LONG)]


class LUID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [('Luid', LUID), ('Attributes', wintypes.DWORD)]


class TOKEN_PRIVILEGES(ctypes.Structure):
    _fields_ = [('PrivilegeCount', wintypes.DWORD), ('Privileges', LUID_AND_ATTRIBUTES * 8)]


GetCurrentProcess = kernel32.GetCurrentProcess
GetCurrentProcess.restype = wintypes.HANDLE
GetCurrentProcess.argtypes = ()

OpenProcessToken = advapi32.OpenProcessToken
OpenProcessToken.restype = wintypes.BOOL
OpenProcessToken.argtypes = (wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE))
OpenProcessToken.errcheck = check_bool

LookupPrivilegeValueW = advapi32.LookupPrivilegeValueW
LookupPrivilegeValueW.restype = wintypes.BOOL
LookupPrivilegeValueW.argtypes = (wintypes.LPCWSTR, wintypes.LPCWSTR, ctypes.POINTER(LUID))
LookupPrivilegeValueW.errcheck = check_bool

AdjustTokenPrivileges = advapi32.AdjustTokenPrivileges
AdjustTokenPrivileges.restype = wintypes.BOOL
AdjustTokenPrivileges.argtypes = (
    wintypes.HANDLE, wintypes.BOOL, ctypes.POINTER(TOKEN_PRIVILEGES),
    wintypes.DWORD, ctypes.POINTER(TOKEN_PRIVILEGES), ctypes.POINTER(wintypes.DWORD),
)
AdjustTokenPrivileges.errcheck = check_bool
