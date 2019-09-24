# encoding: utf-8
"""
Contains all of the members of :mod:`ntfslink.ctypes_impl._winapi`, plus a set
of commonly used Win32 API declarations and wrappers.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
from contextlib import contextmanager

from ._win_api import *
from .privileges import ensure_privileges

##########
# Macros #
##########

# noinspection PyMissingOrEmptyDocstring
def CTL_CODE(device, func, method, access):
	return (device << 16) | (access << 14) | (func << 2) | method

# noinspection PyMissingOrEmptyDocstring
def DEVICE_TYPE_FROM_CTL_CODE(code):
	return (code & 0xffff0000) >> 16

# noinspection PyMissingOrEmptyDocstring
def METHOD_FROM_CTL_CODE(code):
	return code & 3

#############
# Constants #
#############

## Creation Flags
CREATE_NEW = 1
OPEN_EXISTING = 3

## File Operation Constants
_FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
_FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
_FILE_FLAG_REPARSE_BACKUP = _FILE_FLAG_OPEN_REPARSE_POINT | _FILE_FLAG_BACKUP_SEMANTICS

## Generic Access Constants
_GENERIC_READ = 0x80000000
_GENERIC_WRITE = 0x40000000

## File Shared Access Constants
_FILE_SHARE_READ   = 0x00000001
_FILE_SHARE_WRITE  = 0x00000002
_FILE_SHARE_DELETE = 0x00000004
_FILE_SHARE_ALL    = _FILE_SHARE_READ | _FILE_SHARE_WRITE | _FILE_SHARE_DELETE

## Device Codes
FILE_DEVICE_FILE_SYSTEM = 0x00000009

## Method Codes
METHOD_BUFFERED = 0

## File Attributes
FILE_ATTRIBUTE_NORMAL        = 0x00000080
FILE_ATTRIBUTE_DIRECTORY     = 0x00000010
FILE_ATTRIBUTE_REPARSE_POINT = 0x00000400

## Ioctl File Access
FILE_ANY_ACCESS = 0
FILE_SPECIAL_ACCESS = FILE_ANY_ACCESS
FILE_READ_DATA = FILE_READ_ACCESS = 0x0001
FILE_WRITE_DATA = FILE_WRITE_ACCESS = 0x0002

#########
# Types #
#########

class UNICODE_STRING(Structure):
	""" Used to define Unicode strings. """
	_pack_ = 1
	_fields_ = [('Length', USHORT),
	            ('MaximumLength', USHORT),
	            ('Buffer', LPWSTR)]

#: Pointer to :class:`UNICODE_STRING`.
PUNICODE_STRING = POINTER(UNICODE_STRING)

###############################
# API Declarations & Wrappers #
###############################

_CreateFile = WINFUNCDECL(
	'CreateFile',
	LPTSTR, DWORD, DWORD, LPVOID, DWORD, DWORD, HANDLE,
	restype=HANDLE, use_tchar=True, errcheck=errcheck_handle_result
)

@contextmanager
def _open_file(filepath, access, share):
	""" Wrapper around ``CreateFile`` API. """
	ensure_privileges()
	flags = _FILE_FLAG_OPEN_REPARSE_POINT | _FILE_FLAG_BACKUP_SEMANTICS \
	        if os.path.isdir(filepath) else \
	        _FILE_FLAG_OPEN_REPARSE_POINT
	disposition = OPEN_EXISTING if os.path.exists(filepath) else CREATE_NEW
	handle = _CreateFile(filepath, access, share, None, disposition, flags, PNULL)
	try:
		yield handle
	finally:
		CloseHandle(handle)

def open_file_r(filepath):
	"""
	Opens a file for reading.
	:param filepath: filepath to open.
	:type filepath:
	:return: A valid handle
	:rtype: HANDLE
	"""
	return _open_file(filepath, _GENERIC_READ, _FILE_SHARE_ALL)

def open_file_w(filepath):
	""" Opens a file for writing/deleting. """
	return _open_file(filepath, _GENERIC_WRITE, _FILE_SHARE_ALL)
