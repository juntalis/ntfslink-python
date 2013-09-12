"""
_advapi32.py
Declarations and wrapper for some of the advapi32.dll exports.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
from _winioctl import *

# Our DLL object
advapi32 = WinDLL('advapi32')

## Constants used specifically by our advapi32 functions.
# Access Types
# The following are masks for the predefined standard access types
DELETE = 0x00010000L
READ_CONTROL = 0x00020000L
WRITE_DAC = 0x00040000L
WRITE_OWNER = 0x00080000L
SYNCHRONIZE = 0x00100000L

STANDARD_RIGHTS_REQUIRED = 0x000F0000L
STANDARD_RIGHTS_READ = READ_CONTROL
STANDARD_RIGHTS_WRITE = READ_CONTROL
STANDARD_RIGHTS_EXECUTE = READ_CONTROL

STANDARD_RIGHTS_ALL = 0x001F0000L
SPECIFIC_RIGHTS_ALL = 0x0000FFFFL

# AccessSystemAcl access type
ACCESS_SYSTEM_SECURITY = 0x01000000L

# MaximumAllowed access type
MAXIMUM_ALLOWED = 0x02000000L

# Security Tokens
TOKEN_ASSIGN_PRIMARY = 0x0001
TOKEN_DUPLICATE = 0x0002
TOKEN_IMPERSONATE = 0x0004
TOKEN_QUERY = 0x0008
TOKEN_QUERY_SOURCE = 0x0010
TOKEN_ADJUST_PRIVILEGES = 0x0020
TOKEN_ADJUST_GROUPS = 0x0040
TOKEN_ADJUST_DEFAULT = 0x0080
TOKEN_ADJUST_SESSIONID = 0x0100

TOKEN_ALL_ACCESS_P = STANDARD_RIGHTS_REQUIRED | TOKEN_ASSIGN_PRIMARY | TOKEN_DUPLICATE | TOKEN_IMPERSONATE | TOKEN_QUERY | TOKEN_QUERY_SOURCE | TOKEN_ADJUST_PRIVILEGES | TOKEN_ADJUST_GROUPS | TOKEN_ADJUST_DEFAULT
TOKEN_ALL_ACCESS = TOKEN_ALL_ACCESS_P | TOKEN_ADJUST_SESSIONID

# SE Privileges
SE_PRIVILEGE_ENABLED_BY_DEFAULT = 0x00000001L
SE_PRIVILEGE_ENABLED = 0x00000002L
SE_PRIVILEGE_REMOVED = 0X00000004L
SE_PRIVILEGE_USED_FOR_ACCESS = 0x80000000L

SE_PRIVILEGE_VALID_ATTRIBUTES = SE_PRIVILEGE_ENABLED_BY_DEFAULT | SE_PRIVILEGE_ENABLED | SE_PRIVILEGE_REMOVED | SE_PRIVILEGE_USED_FOR_ACCESS

# Privilege Set Control flags
PRIVILEGE_SET_ALL_NECESSARY = 1

# Privilege names.
SE_CREATE_TOKEN_NAME = 'SeCreateTokenPrivilege'
SE_ASSIGNPRIMARYTOKEN_NAME = 'SeAssignPrimaryTokenPrivilege'
SE_RESTORE_NAME = 'SeRestorePrivilege'
SE_BACKUP_NAME = 'SeBackupPrivilege'
SE_CREATE_SYMBOLIC_LINK_NAME = 'SeCreateSymbolicLinkPrivilege'
SE_MANAGE_VOLUME_NAME = 'SeManageVolumePrivilege'
SE_LOAD_DRIVER_NAME = 'SeLoadDriverPrivilege'
SE_UNSOLICITED_INPUT_NAME = 'SeUnsolicitedInputPrivilege'

## Types that will only be used with advapi32 declarations.
class LUID(Structure):
	"""
	CTypes implementation of:

	typedef struct _LUID {
	  DWORD LowPart;
	  LONG  HighPart;
	} LUID, *PLUID;
	"""

	_fields_ = [
		("LowPart", DWORD),
		("HighPart", LONG),
	]

PLUID = POINTER(LUID)

class LuidAndAttributes(Structure):
	"""
	CTypes implementation of:

	typedef struct _LUID_AND_ATTRIBUTES {
	  LUID  Luid;
	  DWORD Attributes;
	} LUID_AND_ATTRIBUTES, *PLUID_AND_ATTRIBUTES;
	"""

	_fields_ = [
		("Luid", LUID),
		("Attributes", DWORD),
	]

class TokenPrivileges(Structure):
	"""
	CTypes implementation of:

	typedef struct _TOKEN_PRIVILEGES {
	  DWORD               PrivilegeCount;
	  LUID_AND_ATTRIBUTES Privileges[ANYSIZE_ARRAY];
	} TOKEN_PRIVILEGES, *PTOKEN_PRIVILEGES;
	"""

	#noinspection PyTypeChecker
	_fields_ = [
		("PrivilegeCount", DWORD),
		("Privileges", LuidAndAttributes * ANYSIZE_ARRAY),
	]

PTokenPrivileges = POINTER(TokenPrivileges)

## Functions exported from AdvApi32.dll

OpenProcessToken = advapi32.OpenProcessToken
OpenProcessToken.restype = BOOL
OpenProcessToken.argtypes = [HANDLE, DWORD, PHANDLE]
OpenProcessToken.__doc__ = \
"""
The OpenProcessToken function opens the access token associated with a process.

	BOOL WINAPI OpenProcessToken(
		_In_   HANDLE ProcessHandle,
		_In_   DWORD DesiredAccess,
		_Out_  PHANDLE TokenHandle
	);

`MSDN Documentation <http://msdn.microsoft.com/en-us/library/windows/desktop/aa379295(v=vs.85).aspx>`_
"""

LookupPrivilegeValue = advapi32.LookupPrivilegeValueW
LookupPrivilegeValue.restype = BOOL
LookupPrivilegeValue.argtypes = [ LPCWSTR, LPCWSTR, PLUID ]
LookupPrivilegeValue.__doc__ = \
"""
The LookupPrivilegeValue function retrieves the locally unique identifier (LUID) used on a specified system to locally
represent the specified privilege name.

	BOOL WINAPI LookupPrivilegeValue(
		_In_opt_  LPCTSTR lpSystemName,
		_In_      LPCTSTR lpName,
		_Out_     PLUID lpLuid
	);

`MSDN Documentation <http://msdn.microsoft.com/en-us/library/windows/desktop/aa379180(v=vs.85).aspx>`_
"""

AdjustTokenPrivileges = advapi32.AdjustTokenPrivileges
AdjustTokenPrivileges.restype = BOOL
AdjustTokenPrivileges.argtypes = [ HANDLE, BOOL, PTokenPrivileges, DWORD, PTokenPrivileges, PDWORD ]
AdjustTokenPrivileges.__doc__ = \
"""
The AdjustTokenPrivileges function enables or disables privileges in the specified access token. Enabling or disabling
privileges in an access token requires TOKEN_ADJUST_PRIVILEGES access.

	BOOL WINAPI AdjustTokenPrivileges(
		_In_       HANDLE TokenHandle,
		_In_       BOOL DisableAllPrivileges,
		_In_opt_   PTOKEN_PRIVILEGES NewState,
		_In_       DWORD BufferLength,
		_Out_opt_  PTOKEN_PRIVILEGES PreviousState,
		_Out_opt_  PDWORD ReturnLength
	);

`MSDN Documentation <http://msdn.microsoft.com/en-us/library/windows/desktop/aa375202(v=vs.85).aspx>`_
"""

