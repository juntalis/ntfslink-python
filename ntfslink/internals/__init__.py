"""
__init__.py
Internal package for native Win32 API.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
from os import path
from _kernel32 import *
from _advapi32 import *

class InvalidHandleException(Exception):
	""" Exception class for when a call to CreateFile returns INVALID_HANDLE (-1). """

def IsFolder(fpath):
	"""
	Checks whether a given path is a folder by using the GetFileAttributes call and testing the result against the
	FILE_ATTRIBUTE_DIRECTORY flag.
	"""
	return bool(GetFileAttributesW(fpath) & FILE_ATTRIBUTE_DIRECTORY)

def IsReparsePoint(fpath):
	"""
	Checks whether a given path is a reparse point by using the GetFileAttributes call and testing the result against
	the FILE_ATTRIBUTE_REPARSE_POINT flag.
	"""
	return bool(GetFileAttributesW(fpath) & FILE_ATTRIBUTE_REPARSE_POINT)

def IsReparseDir(fpath):
	"""
	Checks whether a given path is a reparse point and a folder by using the GetFileAttributes call and testing the
	result against the FILE_ATTRIBUTE_REPARSE_DIRECTORY flag. (which is just:
		FILE_ATTRIBUTE_DIRECTORY | FILE_ATTRIBUTE_REPARSE_POINT
	)
	"""
	return bool((GetFileAttributesW(fpath) & FILE_ATTRIBUTE_REPARSE_DIRECTORY) == FILE_ATTRIBUTE_REPARSE_DIRECTORY)

def TranslatePath(fpath):
	"""
	Builds a filepath for use in absolute symbolic links and junctions. Used for the "SubstituteName" field.

		>>> TranslatePath('test.txt')
		\??\C:\Temp\test.txt
	"""
	fpath = path.abspath(fpath)
	if fpath[len(fpath)-1] == '\\' and fpath[len(fpath)-2] == ':':
		fpath = fpath[:len(fpath)-1]
	return '\\??\\%s' % fpath

def ObtainRestorePrivilege(readwrite = False):
	"""
	Acquires the privileges necessary to open a file with some additional access. For instance, when creating a
	junction, we'll use this so that we can call CreateFile with the FILE_FLAG_REPARSE_BACKUP flag set.
	"""
	hToken = HANDLE()
	tp = TokenPrivileges()
	hProcess = GetCurrentProcess()
	lpName = SE_RESTORE_NAME if readwrite else SE_BACKUP_NAME
	if OpenProcessToken(hProcess, TOKEN_ADJUST_PRIVILEGES, byref(hToken)) == FALSE:
		raise Exception('Could not open current process security token.')
	if LookupPrivilegeValue(None, lpName, byref(tp.Privileges[0].Luid)) == FALSE:
		CloseHandle(hToken)
		raise Exception('Could not look up %s privilege.' % lpName)
	tp.PrivilegeCount = 1
	tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED
	if AdjustTokenPrivileges(hToken, FALSE, byref(tp), sizeof(TokenPrivileges), None, None) == FALSE:
		CloseHandle(hToken)
		raise Exception('Could not adjust current process\'s security privileges.')
	CloseHandle(hToken)

def _OpenFileForIO(filepath, generic, share, backup, flag = FILE_FLAG_OPEN_REPARSE_POINT):
	if backup:
		ObtainRestorePrivilege()
		flag |= FILE_FLAG_BACKUP_SEMANTICS
	hFile = CreateFile(filepath, generic, share, OPEN_EXISTING, flag)
	if hFile == HANDLE(INVALID_HANDLE_VALUE):
		raise InvalidHandleException('Failed to open path: %s' % filepath)
	return hFile

def OpenFileForRead(filepath, backup = False):
	""" Opens a file for reading. """
	return _OpenFileForIO(filepath, GENERIC_READ, FILE_SHARE_READ, backup)

def OpenFileForAll(filepath, backup = False):
	""" Opens a file for writing/deleting. """
	return _OpenFileForIO(filepath, GENERIC_WRITE, FILE_SHARE_ALL, backup)

def CalculateLength(bufferType, pathBuffer):
	"""
	Used internally to find the ReparseDataLength and the size of the PathBuffer to allocate.

	It returns a tuple containing (PathBufferLength, ReparseDataLength).
	"""
	offset = pathBuffer.SubstituteNameLength \
			 if pathBuffer.PrintNameOffset == 0 else \
			 pathBuffer.PrintNameOffset + SZWCHAR
	pathBufLen = pathBuffer.PrintNameLength + offset # Ending \0
	return pathBufLen, bufferType.PathBuffer.offset + pathBufLen
