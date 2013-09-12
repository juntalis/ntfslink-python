"""
_windows.py
Declarations and typedefs for some of the base Win32 platform APIs.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
import sys as _sys
_sys.getfilesystemencoding()

from ctypes import *
from ctypes.wintypes import *
from ctypes64 import POINTER



## Constants
# Windows definitions
ANYSIZE_ARRAY = 1
MAX_PATH = 260

FALSE = 0
TRUE = 1

NULL = c_void_p(0)
INVALID_HANDLE_VALUE = -1

# Access
FILE_ANY_ACCESS = 0
FILE_SPECIAL_ACCESS = FILE_ANY_ACCESS
FILE_READ_DATA = FILE_READ_ACCESS = 0x0001
FILE_WRITE_DATA = FILE_WRITE_ACCESS = 0x0002

# File open flags
FILE_FLAG_WRITE_THROUGH = 0x80000000
FILE_FLAG_OVERLAPPED = 0x40000000
FILE_FLAG_NO_BUFFERING = 0x20000000
FILE_FLAG_RANDOM_ACCESS = 0x10000000
FILE_FLAG_SEQUENTIAL_SCAN = 0x08000000
FILE_FLAG_DELETE_ON_CLOSE = 0x04000000
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
FILE_FLAG_POSIX_SEMANTICS = 0x01000000
FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
FILE_FLAG_OPEN_NO_RECALL = 0x00100000
FILE_FLAG_FIRST_PIPE_INSTANCE = 0x00080000
FILE_FLAG_REPARSE_BACKUP = FILE_FLAG_OPEN_REPARSE_POINT | FILE_FLAG_BACKUP_SEMANTICS

# The variables below deal with some of the more general stuff. (File
# IO, file access privileges, flags, basic typedefs, etc) There's a few
# flags dealing with reparse points that I left in this section for naming
# consistency.

# Generic access
GENERIC_READ = 0x80000000L
GENERIC_WRITE = 0x40000000L
GENERIC_EXECUTE = 0x20000000L
GENERIC_ALL = 0x10000000L

# File shared access
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
FILE_SHARE_DELETE = 0x00000004
FILE_SHARE_READ_WRITE = FILE_SHARE_READ | FILE_SHARE_WRITE
FILE_SHARE_ALL = FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE

# Creation flags
CREATE_NEW = 1
CREATE_ALWAYS = 2
OPEN_EXISTING = 3
OPEN_ALWAYS = 4
TRUNCATE_EXISTING = 5

## Type Definitions
# First, we'll do all of our stupid MS-specific typedecl's
CHAR = c_char
WCHAR = c_wchar
UCHAR = c_ubyte

TCHAR = c_wchar
LPCTSTR = LPTSTR = c_wchar_p

LPOVERLAPPED = c_void_p
LPSECURITY_ATTRIBUTES = c_void_p

PHANDLE = POINTER(HANDLE)
LPHANDLE = PHANDLE

PWORD = POINTER(WORD)
LPWORD = PWORD
PDWORD = POINTER(DWORD)
LPDWORD = PDWORD
DEVICE_TYPE = DWORD

ULONG_PTR = ULONG
PULONG_PTR = POINTER(ULONG_PTR)
LONG_PTR = c_long
PLONG_PTR = POINTER(LONG_PTR)

SIZE_T = ULONG_PTR
PSIZE_T = POINTER(SIZE_T)
SSIZE_T = LONG_PTR
PSSIZE_T = POINTER(SSIZE_T)

# Char-size constants
SZCHAR = sizeof(CHAR)
SZWCHAR = sizeof(WCHAR)
SZUCHAR = sizeof(UCHAR)
SZTCHAR = sizeof(TCHAR)

## Common Structures/Unions

class GUID(Structure):
	"""
	CTypes implementation of:

		typedef struct _GUID {
			DWORD Data1;
			WORD  Data2;
			WORD  Data3;
			BYTE  Data4[8];
		} GUID;
	"""
	_fields_ = [
		("Data1", DWORD),
		("Data2", WORD),
		("Data3", WORD),
		("Data4", (BYTE * 8)),
	]

