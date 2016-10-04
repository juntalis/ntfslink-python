# encoding: utf-8
"""
Common definitions/declarations for dealing with reparse points. Used by
both :mod:`reparse_struct` and :mod:`reparse_ctypes`.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
from .winapi import *
from .._util import chain

#############
# Constants #
#############

## Reparse Point Tag Values
IO_REPARSE_TAG_RESERVED_ZERO    = 0x00000000
IO_REPARSE_TAG_RESERVED_ONE     = 0x00000001
IO_REPARSE_TAG_MOUNT_POINT      = 0xA0000003
IO_REPARSE_TAG_HSM              = 0xC0000004
IO_REPARSE_TAG_HSM2             = 0x80000006
IO_REPARSE_TAG_SIS              = 0x80000007
IO_REPARSE_TAG_WIM              = 0x80000008
IO_REPARSE_TAG_CSV              = 0x80000009
IO_REPARSE_TAG_DFS              = 0x8000000A
IO_REPARSE_TAG_SYMLINK          = 0xA000000C
IO_REPARSE_TAG_DFSR             = 0x80000012
IO_REPARSE_TAG_DEDUP            = 0x80000013
IO_REPARSE_TAG_NFS              = 0x80000014
IO_REPARSE_TAG_FILE_PLACEHOLDER = 0x80000015
IO_REPARSE_TAG_WOF              = 0x80000017

## Misc Size Constants
MAX_NAME_LENGTH = 1024
MAX_REPARSE_BUFFER = 16 * MAX_NAME_LENGTH

## Control Codes
FSCTL_SET_REPARSE_POINT    = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 41, METHOD_BUFFERED, FILE_SPECIAL_ACCESS)
FSCTL_GET_REPARSE_POINT    = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 42, METHOD_BUFFERED, FILE_ANY_ACCESS)
FSCTL_DELETE_REPARSE_POINT = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 43, METHOD_BUFFERED, FILE_SPECIAL_ACCESS)

## Header Size Constants
#REPARSE_POINT_HEADER_SIZE = SIZEOF(DWORD) + (2 * SIZEOF(WORD))
#REPARSE_GUID_DATA_BUFFER_HEADER_SIZE = REPARSE_POINT_HEADER_SIZE + (SIZEOF(DWORD) * 4)

## Buffer Size Constants
#MAX_GENERIC_REPARSE_BUFFER = MAX_REPARSE_BUFFER - REPARSE_GUID_DATA_BUFFER_HEADER_SIZE
#MAX_MOUNTPOINT_REPARSE_BUFFER = MAX_GENERIC_REPARSE_BUFFER - SIZEOF(WORD) * 4
#MAX_SYMLINK_REPARSE_BUFFER = MAX_MOUNTPOINT_REPARSE_BUFFER - SIZEOF(DWORD)

## FILE_INFORMATION_CLASS Values
FileReparsePointInformation = 0x00000021

#####################
# Utility Functions #
#####################

def is_ms_tag(tag):
	"""
	Determine whether a reparse point tag corresponds to a tag owned by
	Microsoft.
	:param tag: Reparse point tag
	:type tag: int
	:return: ``True`` or ``False`` depending on ``tag``'s value.
	:rtype: bool
	"""
	return bool(tag & 0x80000000)

def is_name_surrogate_tag(tag):
	"""
	Determine whether a reparse point tag is a name surrogate.
	:param tag: Reparse point tag
	:type tag: int
	:return: ``True`` or ``False`` depending on ``tag``'s value.
	:rtype: bool
	"""
	return bool(tag & 0x20000000)

###########
# C Types #
###########

FILE_INFORMATION_CLASS = DWORD

class _IO_STATUS_BLOCK(Structure):
	"""
	:class:`ctypes.Structure` implementation of the following C structure:
	
	```
	typedef struct _IO_STATUS_BLOCK {
	    union {
	        NTSTATUS Status;
	        PVOID Pointer;
	    } DUMMYUNIONNAME;
	
	    ULONG_PTR Information;
	} IO_STATUS_BLOCK, *PIO_STATUS_BLOCK;
	```
	"""
	_fields_ = [
		('Status', LONG_PTR),
		('Information', ULONG_PTR),
	]

# Pointer to IO_STATUS_BLOCK
_PIO_STATUS_BLOCK = POINTER(_IO_STATUS_BLOCK)

class _FILE_REPARSE_POINT_INFORMATION(Structure):
	"""
	:class:`ctypes.Structure` implementation of the following C structure:
	
	```
	typedef struct _FILE_REPARSE_POINT_INFORMATION {
	  LONGLONG FileReference;
	  ULONG    Tag;
	} FILE_REPARSE_POINT_INFORMATION, *PFILE_REPARSE_POINT_INFORMATION;
	```
	"""
	_fields_ = [
		('FileReference', LONGLONG),
		('Tag', ULONG),
	]

_FILE_REPARSE_POINT_INFORMATION.size = SIZEOF(_FILE_REPARSE_POINT_INFORMATION)

# Callback declaration. Not currently used.
# _PIO_APC_ROUTINE = WINFUNCTYPE(None, LPVOID, _PIO_STATUS_BLOCK, ULONG)

###############################
# API Declarations & Wrappers #
###############################

# Not currently used.
# _NtQueryInformationFile = NTFUNCDECL(
# 	'NtQueryInformationFile',
# 	HANDLE, _PIO_STATUS_BLOCK, LPVOID, ULONG, FILE_INFORMATION_CLASS
# )

_NtQueryDirectoryFile = NTFUNCDECL(
	'NtQueryDirectoryFile',
	HANDLE, HANDLE, LPVOID, LPVOID, _PIO_STATUS_BLOCK, LPVOID, ULONG,
	FILE_INFORMATION_CLASS, BOOLEAN, PUNICODE_STRING, BOOLEAN
)

_DeviceIoControl = WINFUNCDECL(
	'DeviceIoControl',
	HANDLE, DWORD, LPVOID, DWORD, LPVOID, DWORD, LPDWORD, LPVOID,
	restype=BOOL, errcheck=errcheck_bool_result_checked
)

def nt_query_directory(hfile):
	"""
	Queries a directory's file reference id and reparse tag.
	:param hfile: The open handle of the target directory.
	:type hfile: HANDLE
	:return: A tuple of the directory's file reference id, and its reparse tag.
	:rtype: (int, int,)
	"""
	statusblock = _IO_STATUS_BLOCK()
	infobuf = _FILE_REPARSE_POINT_INFORMATION()
	query = _NtQueryDirectoryFile(hfile, None, None, None, BYREF(statusblock), BYREF(infobuf), infobuf.size, FileReparsePointInformation, TRUE, None, TRUE)
	return infobuf.FileReference, infobuf.Tag, query, statusblock

def deviceioctl(hfile, code, inbuf, insize, outbuf, outsize):
	"""
	Wrapper around the real DeviceIoControl to return a tuple containing a bool
	indicating success, and a number containing the size of the bytes returned.
	:param hfile: File handle
	:type hfile: HANDLE | int
	:param code: Decide control code
	:type code: int
	:param inbuf: Input buffer
	:type inbuf: ctypes.c_void_p | ctypes.c_char_p | None
	:param insize: sizeof(inbuf)
	:type insize: int
	:param outbuf: ctypes
	:type outbuf: ctypes.c_void_p | ctypes.c_char_p | None
	:param outsize: sizeof(outsize)
	:type outsize: int
	:return: Tuple of success, bytes written
	:rtype: (bool, int,)
	"""
	dwret = DWORD(0)
	return _DeviceIoControl(
		hfile, code, inbuf, insize,
		outbuf, outsize, BYREF(dwret), None
	), dwret.value
