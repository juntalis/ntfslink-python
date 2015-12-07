"""
helpers.py
Internal package for native Win32 API. I've been ping ponging back
and forth with the naming scheme for this file, as well as for the
rest of the ntfslink.internals package. I'd prefer to use the
lowercase underscore names for the entire project, but having that
inconsistency between the native Win32 function names and the pythonic
helpers has been bugging the shit out of me.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""

import os
from .consts import *
from .prototypes import *
from ._winioctl import *

# See: ObtainTokenPrivileges
_ObtainedPrivileges = []

class InvalidHandleException(Exception):
	""" Raised when a necessary handle contains INVALID_HANDLE_VALUE (-1). """

class InvalidSourceException(Exception):
	""" Raised when an invalid path is specified for srcpath in a create function. """

class InvalidLinkException(Exception):
	""" Raised when an invalid path is given for linkpath in a read function. """

def IsDir(filepath):
	"""
	Checks whether a given path is a folder by using the GetFileAttributes call and testing the result against the
	FILE_ATTRIBUTE_DIRECTORY flag.
	"""
	return (GetFileAttributes(filepath) & FILE_ATTRIBUTE_DIRECTORY) == FILE_ATTRIBUTE_DIRECTORY

def IsReparsePoint(filepath):
	"""
	Checks whether a given path is a reparse point by using the GetFileAttributes call and testing the result against
	the FILE_ATTRIBUTE_REPARSE_POINT flag.
	"""
	return (GetFileAttributes(filepath) & FILE_ATTRIBUTE_REPARSE_POINT) == FILE_ATTRIBUTE_REPARSE_POINT

def IsReparseDir(filepath):
	"""
	Checks whether a given path is a reparse point and a folder by using the GetFileAttributes call and testing the
	result against the FILE_ATTRIBUTE_REPARSE_DIRECTORY flag. (which is just:
		FILE_ATTRIBUTE_DIRECTORY | FILE_ATTRIBUTE_REPARSE_POINT
	)
	"""
	return (GetFileAttributes(filepath) & FILE_ATTRIBUTE_REPARSE_DIRECTORY) == FILE_ATTRIBUTE_REPARSE_DIRECTORY

def ExtendedAbspath(filepath):
	"""
	Builds a filepath for use in absolute symbolic links and junctions. Used for the "SubstituteName" field.

		>>> ExtendedAbspath('test.txt')
		\??\C:\Temp\test.txt
	"""
	filepath = os.path.abspath(filepath)
	if filepath[-1] == '\\' and filepath[-2] == ':':
		filepath = filepath[:-1]
	return '\\?\\{0}'.format(filepath)

def ObtainTokenPrivileges(privileges):
	"""
	Acquires the privileges necessary to open a file with some additional access. For instance, when creating a
	junction, we'll use this so that we can call CreateFile with the FILE_FLAG_REPARSE_BACKUP flag set.
	"""
	global _ObtainedPrivileges
	hToken = HANDLE()
	tp = TOKEN_PRIVILEGES()
	hProcess = GetCurrentProcess()
	if not OpenProcessToken(hProcess, TOKEN_ADJUST_PRIVILEGES, byref(hToken)):
		raise WinError()
	tp.PrivilegeCount = 1
	tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED
	for privilege in privileges:
		if privilege in _ObtainedPrivileges: continue
		if not LookupPrivilegeValue(None, privilege, byref(tp.Privileges[0].Luid)):
			CloseHandle(hToken)
			raise Exception('LookupPrivilegeValue failed for privilege: {0}'.format(privilege))
		if not AdjustTokenPrivileges(hToken, False, byref(tp), sizeof(TOKEN_PRIVILEGES), None, None):
			CloseHandle(hToken)
			raise WinError()
		_ObtainedPrivileges.append(privilege)
	CloseHandle(hToken)

def OpenFileIO(filepath, generic, share, privileges, flag = FILE_FLAG_OPEN_REPARSE_POINT, template = HANDLE.NULL):
	if privileges is not None:
		ObtainTokenPrivileges(privileges)
		flag |= FILE_FLAG_BACKUP_SEMANTICS
	hFile = CreateFile(
		lpFileName=filepath,
		dwDesiredAccess=generic,
		dwShareMode=share,
		dwCreationDisposition=OPEN_EXISTING,
		dwFlagsAndAttributes=flag,
		hTemplateFile=template
	)
	if not hFile:
		raise InvalidHandleException('Failed to open path: %s' % filepath)
	return hFile

def OpenFileR(filepath, backup = False):
	""" Opens a file for reading. """
	return OpenFileIO(filepath, GENERIC_READ, FILE_SHARE_READ, [ SE_BACKUP_NAME ] if backup else None)

def OpenFileRW(filepath, backup = False):
	""" Opens a file for writing/deleting. """
	return OpenFileIO(filepath, GENERIC_WRITE, FILE_SHARE_ALL, [ SE_RESTORE_NAME ] if backup else None)

def calcsize_pathbuffer(buftype, pathbuf):
	"""
	Used internally to find the ReparseDataLength and the size of the PathBuffer to allocate.

	It returns a tuple containing (PathBufferLength, ReparseDataLength).
	"""
	offset = pathbuf.SubstituteNameLength \
			 if pathbuf.PrintNameOffset == 0 else \
			 pathbuf.PrintNameOffset + sizeof(WCHAR)
	buflen = pathbuf.PrintNameLength + offset # Ending \0
	return buflen, buftype.PathBuffer.offset + buflen

