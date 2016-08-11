# encoding: utf-8
"""
privileges.py
TODO: Description

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
from ..supports import is_gt_winxp
from ._winapi import errcheck_bool_result_checked, CloseHandle, WinError, DWORD, \
	SIZEOF, LPDWORD, advapi32, BOOL, _T, POINTER, BYREF, LARGE_INTEGER, \
	WINFUNCDECL, Structure, HANDLE, LPTSTR

## Shorten up references
LUID = LARGE_INTEGER
PHANDLE, PLUID = POINTER(HANDLE), POINTER(LUID)

#############
# Constants #
#############

## SE Privilege names
SE_BACKUP_NAME = _T('SeBackupPrivilege')
SE_RESTORE_NAME = _T('SeRestorePrivilege')

## From what I read, this privilege is only necessary on Windows Vista, but we
## might as well acquire for Vista+ just to be safe.
SE_CREATE_SYMBOLIC_LINK_NAME = _T('SeCreateSymbolicLinkPrivilege')

## Privileges to obtain
_OBTAINABLE_PRIVILEGES = [
	SE_BACKUP_NAME,
	SE_RESTORE_NAME
]

if is_gt_winxp:
	_OBTAINABLE_PRIVILEGES.append(SE_CREATE_SYMBOLIC_LINK_NAME)

_OBTAINABLE_PRIVILEGES_COUNT = len(_OBTAINABLE_PRIVILEGES)

## SE Privilege Attributes
SE_PRIVILEGE_ENABLED_BY_DEFAULT = 0x00000001
SE_PRIVILEGE_ENABLED = 0x00000002
SE_PRIVILEGE_REMOVED = 0X00000004
SE_PRIVILEGE_USED_FOR_ACCESS = 0x80000000

## Process token access mask
TOKEN_ASSIGN_PRIMARY = 0x0001
TOKEN_DUPLICATE = 0x0002
TOKEN_IMPERSONATE = 0x0004
TOKEN_QUERY = 0x0008
TOKEN_QUERY_SOURCE = 0x0010
TOKEN_ADJUST_PRIVILEGES = 0x0020
TOKEN_ADJUST_GROUPS = 0x0040
TOKEN_ADJUST_DEFAULT = 0x0080
TOKEN_ADJUST_SESSIONID = 0x0100

###########################
# Structures Declarations #
###########################

class LUID_AND_ATTRIBUTES(Structure):
	_fields_ = [
		('Luid', LUID),
		('Attributes', DWORD),
	]

class TOKEN_PRIVILEGES(Structure):
	#noinspection PyTypeChecker
	_fields_ = [
		('PrivilegeCount', DWORD),
		('Privileges', LUID_AND_ATTRIBUTES * _OBTAINABLE_PRIVILEGES_COUNT),
	]

PTOKEN_PRIVILEGES = POINTER(TOKEN_PRIVILEGES)

################################
# Native Function Declarations #
################################

_GetCurrentProcess = WINFUNCDECL(
	'GetCurrentProcess', [],
	restype=HANDLE, use_last_error=False
)

_OpenProcessToken = WINFUNCDECL(
	'OpenProcessToken',
	[ HANDLE, DWORD, PHANDLE ], dll=advapi32,
	restype=BOOL, errcheck=errcheck_bool_result_checked,
)

_LookupPrivilegeValue = WINFUNCDECL(
	'LookupPrivilegeValue',
	[ LPTSTR, LPTSTR, PLUID ], dll=advapi32, use_tchar=True,
	restype=BOOL, errcheck=errcheck_bool_result_checked
)

_AdjustTokenPrivileges = WINFUNCDECL(
	'AdjustTokenPrivileges',
	[ HANDLE, BOOL, PTOKEN_PRIVILEGES, DWORD, PTOKEN_PRIVILEGES, LPDWORD ],
	dll=advapi32, restype=BOOL, errcheck=errcheck_bool_result_checked
)

def obtain_privileges():
	"""
	Obtain all privileges necessary for this module to function correctly.
	"""
	global _OBTAINABLE_PRIVILEGES, _OBTAINABLE_PRIVILEGES_COUNT
	hToken = HANDLE(0)
	tp = TOKEN_PRIVILEGES()
	hProcess = _GetCurrentProcess()
	_OpenProcessToken(hProcess, TOKEN_ADJUST_PRIVILEGES, BYREF(hToken))
	tp.PrivilegeCount = _OBTAINABLE_PRIVILEGES_COUNT
	try:
		for idx, privname in enumerate(_OBTAINABLE_PRIVILEGES):
			_LookupPrivilegeValue(None, privname, BYREF(tp.Privileges[idx]))
			tp.Privileges[idx].Attributes = SE_PRIVILEGE_ENABLED
		_AdjustTokenPrivileges(hToken, 0, BYREF(tp), SIZEOF(TOKEN_PRIVILEGES), None, None)
	finally:
		CloseHandle(hToken)

__all__ = [ 'obtain_privileges' ]
