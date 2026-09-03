"""Acquires the process privileges needed to manipulate reparse points."""
import ctypes
import ctypes.wintypes

from .. import _consts as consts
from . import winapi

_OBTAINABLE_PRIVILEGES = (
    consts.SE_BACKUP_NAME,
    consts.SE_RESTORE_NAME,
    consts.SE_CREATE_SYMBOLIC_LINK_NAME,
)

_done = False


def obtain_privileges(names):
    if not names:
        return
    hproc = winapi.GetCurrentProcess()
    htoken = ctypes.wintypes.HANDLE(0)
    winapi.OpenProcessToken(hproc, consts.TOKEN_ADJUST_PRIVILEGES, ctypes.byref(htoken))
    try:
        tp = winapi.TOKEN_PRIVILEGES()
        tp.PrivilegeCount = len(names)
        for idx, name in enumerate(names):
            winapi.LookupPrivilegeValueW(None, name, ctypes.byref(tp.Privileges[idx].Luid))
            tp.Privileges[idx].Attributes = consts.SE_PRIVILEGE_ENABLED
        winapi.AdjustTokenPrivileges(htoken, False, ctypes.byref(tp), 0, None, None)
    finally:
        winapi.CloseHandle(htoken)


def ensure_privileges():
    global _done
    if not _done:
        obtain_privileges(_OBTAINABLE_PRIVILEGES)
        _done = True


def reset_for_tests():
    """Test-only hook: forget that privileges were already acquired."""
    global _done
    _done = False
