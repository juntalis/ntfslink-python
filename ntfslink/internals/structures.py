# encoding: utf-8
"""
TODO: Description

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
from ctypes.wintypes import FILETIME
from .consts import ANYSIZE_ARRAY
from .cutil import Out as _out, deref as deref
from .compat import POINTER, binary
from .types import *

#import sys
#mymod = sys.modules[__name__]
#_notmine_ = []
#_notmine_ += dir(mymod)

## Kernel32 Structures
class FILE_NOTIFY_INFORMATION(Structure):
	_fields_ = [
		('NextEntryOffset', DWORD),
		('Action', DWORD),
		('FileNameLength', DWORD),
		('FileName', PTSTR),
	]

class BY_HANDLE_FILE_INFORMATION(Structure):
	_fields_ = [
		('dwFileAttributes', DWORD),
		('ftCreationTime', FILETIME),
		('ftLastAccessTime', FILETIME),
		('ftLastWriteTime', FILETIME),
		('dwVolumeSerialNumber', DWORD),
		('nFileSizeHigh', DWORD),
		('nFileSizeLow', DWORD),
		('nNumberOfLinks', DWORD),
		('nFileIndexHigh', DWORD),
		('nFileIndexLow', DWORD)
	]

PBY_HANDLE_FILE_INFORMATION = POINTER(BY_HANDLE_FILE_INFORMATION)
LPBY_HANDLE_FILE_INFORMATION = _out(PBY_HANDLE_FILE_INFORMATION)

## Win32 Structs
class GUID(Structure):
	""" Borrowed small parts of this from the comtypes module. """
	NULL = None
	_fields_ = [
		('Data1', DWORD),
		('Data2', WORD),
		('Data3', WORD),
		('Data4', (BYTE * 8)),
	]

	def __nonzero__(self):
		return self != GUID.NULL

	def __eq__(self, other):
		return isinstance(other, GUID) and \
			   binary(self) == binary(other)

	def __hash__(self):
		return hash(binary(self))

	def __cmp__(self, other):
		if isinstance(other, GUID):
			return cmp(binary(self), binary(other))
		return -1

# Make LARGE_INTEGER/ULARGE_INTEGER a bit easier to deal with.
class _LARGE_INTEGER_STRUCT(Structure):
	_fields_ = [
		('LowPart', DWORD),
		('HighPart', LONG),
	]
class _ULARGE_INTEGER_STRUCT(Structure):
	_fields_ = [
		('LowPart', DWORD),
		('HighPart', DWORD),
	]

_LARGE_INTEGER_BYTES = _ULARGE_INTEGER_BYTES = (BYTE * 8)

class LARGE_INTEGER(LONGLONG):
	
	@property
	def Parts(self):
		return deref(addressof(self), _LARGE_INTEGER_STRUCT)
	
	@property
	def bytes(self):
		return deref(addressof(self), _LARGE_INTEGER_BYTES)

class LARGE_INTEGER(ULONGLONG):
	
	@property
	def Parts(self):
		return deref(addressof(self), _ULARGE_INTEGER_STRUCT)
	
	@property
	def bytes(self):
		return deref(addressof(self), _ULARGE_INTEGER_BYTES)

LUID = _LARGE_INTEGER_STRUCT

class LUID_AND_ATTRIBUTES(Structure):
	_fields_ = [
		('Luid', LUID),
		('Attributes', DWORD),
	]

class TOKEN_PRIVILEGES(Structure):
	#noinspection PyTypeChecker
	_fields_ = [
		('PrivilegeCount', DWORD),
		('Privileges', LUID_AND_ATTRIBUTES * ANYSIZE_ARRAY),
	]

PLUID              = POINTER(LUID)
PTOKEN_PRIVILEGES  = POINTER(TOKEN_PRIVILEGES)

LPLUID             = _out(PLUID)
LPTOKEN_PRIVILEGES = _out(PTOKEN_PRIVILEGES)

GUID.NULL = GUID()

#mine = dir(mymod)
#__all__ = []
#for k in mine:
#	if k in _notmine_ or k == '_mine_':
#		continue
#	__all__.append(k)
