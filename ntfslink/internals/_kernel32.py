"""
_kernel32.py
Declarations and wrapper for some of the kernel32.dll exports.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
from _winioctl import *

# Our DLL object
kernel32 = WinDLL('kernel32.dll')

## Constants used specifically by our kernel32 functions.
FILE_ATTRIBUTE_READONLY = 0x00000001
FILE_ATTRIBUTE_HIDDEN = 0x00000002
FILE_ATTRIBUTE_SYSTEM = 0x00000004
FILE_ATTRIBUTE_DIRECTORY = 0x00000010
FILE_ATTRIBUTE_ARCHIVE = 0x00000020
FILE_ATTRIBUTE_DEVICE = 0x00000040
FILE_ATTRIBUTE_NORMAL = 0x00000080
FILE_ATTRIBUTE_TEMPORARY = 0x00000100
FILE_ATTRIBUTE_SPARSE_FILE = 0x00000200
FILE_ATTRIBUTE_REPARSE_POINT = 0x00000400
FILE_ATTRIBUTE_COMPRESSED = 0x00000800
FILE_ATTRIBUTE_OFFLINE = 0x00001000
FILE_ATTRIBUTE_NOT_CONTENT_INDEXED = 0x00002000
FILE_ATTRIBUTE_ENCRYPTED = 0x00004000
FILE_ATTRIBUTE_VIRTUAL = 0x00010000
FILE_ATTRIBUTE_REPARSE_DIRECTORY = (FILE_ATTRIBUTE_DIRECTORY | FILE_ATTRIBUTE_REPARSE_POINT)

FILE_NOTIFY_CHANGE_FILE_NAME = 0x00000001
FILE_NOTIFY_CHANGE_DIR_NAME = 0x00000002
FILE_NOTIFY_CHANGE_ATTRIBUTES = 0x00000004
FILE_NOTIFY_CHANGE_SIZE = 0x00000008
FILE_NOTIFY_CHANGE_LAST_WRITE = 0x00000010
FILE_NOTIFY_CHANGE_LAST_ACCESS = 0x00000020
FILE_NOTIFY_CHANGE_CREATION = 0x00000040
FILE_NOTIFY_CHANGE_SECURITY = 0x00000100

FILE_ACTION_ADDED = 0x00000001
FILE_ACTION_REMOVED = 0x00000002
FILE_ACTION_MODIFIED = 0x00000003
FILE_ACTION_RENAMED_OLD_NAME = 0x00000004
FILE_ACTION_RENAMED_NEW_NAME = 0x00000005

FILE_CASE_SENSITIVE_SEARCH = 0x00000001
FILE_CASE_PRESERVED_NAMES = 0x00000002
FILE_UNICODE_ON_DISK = 0x00000004
FILE_PERSISTENT_ACLS = 0x00000008
FILE_FILE_COMPRESSION = 0x00000010
FILE_VOLUME_QUOTAS = 0x00000020
FILE_VOLUME_IS_COMPRESSED = 0x00008000
FILE_READ_ONLY_VOLUME = 0x00080000
FILE_SEQUENTIAL_WRITE_ONCE = 0x00100000
FILE_NAMED_STREAMS = 0x00040000

FILE_SUPPORTS_SPARSE_FILES = 0x00000040
FILE_SUPPORTS_REPARSE_POINTS = 0x00000080
FILE_SUPPORTS_REMOTE_STORAGE = 0x00000100
FILE_SUPPORTS_OBJECT_IDS = 0x00010000
FILE_SUPPORTS_ENCRYPTION = 0x00020000
FILE_SUPPORTS_TRANSACTIONS = 0x00200000
FILE_SUPPORTS_HARD_LINKS = 0x00400000
FILE_SUPPORTS_EXTENDED_ATTRIBUTES = 0x00800000
FILE_SUPPORTS_OPEN_BY_FILE_ID = 0x01000000
FILE_SUPPORTS_USN_JOURNAL = 0x02000000

MAILSLOT_NO_MESSAGE = DWORD(-1)
MAILSLOT_WAIT_FOREVER = DWORD(-1)

# File command codes
FILE_READ_DATA = 0x0001
FILE_WRITE_DATA = 0x0002
FILE_LIST_DIRECTORY = 0x0001
FILE_ADD_FILE = 0x0002
FILE_APPEND_DATA = 0x0004
FILE_ADD_SUBDIRECTORY = 0x0004
FILE_CREATE_PIPE_INSTANCE = 0x0004
FILE_READ_EA = 0x0008
FILE_WRITE_EA = 0x0010
FILE_EXECUTE = 0x0020
FILE_TRAVERSE = 0x0020
FILE_DELETE_CHILD = 0x0040
FILE_READ_ATTRIBUTES = 0x0080
FILE_WRITE_ATTRIBUTES = 0x0100

class FILE_NOTIFY_INFORMATION(Structure):
	"""
	DWORD NextEntryOffset;
	DWORD Action;
	DWORD FileNameLength;
	WCHAR FileName[1];
	"""
	_fields_ = [
		('NextEntryOffset', DWORD),
		('Action', DWORD),
		('FileNameLength', DWORD),
		('FileName', LPTSTR),
	]

class BY_HANDLE_FILE_INFORMATION(Structure):
	"""
		typedef struct _BY_HANDLE_FILE_INFORMATION {
			DWORD dwFileAttributes;
			FILETIME ftCreationTime;
			FILETIME ftLastAccessTime;
			FILETIME ftLastWriteTime;
			DWORD dwVolumeSerialNumber;
			DWORD nFileSizeHigh;
			DWORD nFileSizeLow;
			DWORD nNumberOfLinks;
			DWORD nFileIndexHigh;
			DWORD nFileIndexLow;
		} BY_HANDLE_FILE_INFORMATION, *PBY_HANDLE_FILE_INFORMATION;
	"""
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

LPBY_HANDLE_FILE_INFORMATION = POINTER(BY_HANDLE_FILE_INFORMATION)

## Functions exported from kernel32.dll
CreateFileW = kernel32.CreateFileW
CreateFileW.restype = HANDLE
CreateFileW.argtypes = [ LPCWSTR, DWORD, DWORD, LPSECURITY_ATTRIBUTES, DWORD, DWORD, HANDLE ]

def CreateFile(filename, access, sharemode, creation, flags):
	"""
	Simple wrapper around the CreateFile API call to save me the trouble of constantly casting my variables to the
	needed ctypes type. CreateFile is exported from kernel32.dll and is called with the following arguments::

		HANDLE WINAPI CreateFile(
			__in      LPCTSTR lpFileName,
			__in      DWORD dwDesiredAccess,
			__in      DWORD dwShareMode,
			__in_opt  LPSECURITY_ATTRIBUTES lpSecurityAttributes,
			__in      DWORD dwCreationDisposition,
			__in      DWORD dwFlagsAndAttributes,
			__in_opt  HANDLE hTemplateFile
		);

	More information can be found at the function's
	`MSDN Documentation <http://msdn.microsoft.com/en-us/library/windows/desktop/aa363858(v=vs.85).aspx>`_.
	"""
	hresult = CreateFileW(filename, access, sharemode, None, creation, flags, None)
	return None if hresult == INVALID_HANDLE_VALUE else hresult

CreateDirectoryW = kernel32.CreateDirectoryW
CreateDirectoryW.restype = BOOL
CreateDirectoryW.argtypes = [LPCWSTR, LPSECURITY_ATTRIBUTES]

def CreateDirectory(fpath):
	"""
	Simple wrapper around the CreateDirectory API call. CreateFile is exported from kernel32.dll and is called with the
	following arguments::

		BOOL WINAPI CreateDirectory(
			__in      LPCTSTR lpPathName,
			__in_opt  LPSECURITY_ATTRIBUTES lpSecurityAttributes
		);

	As far as I know, most of what we're doing doesn't require us to deal with the lpSecurityAttributes so for now, I'm
	filling that in with NULL to allow calling the function with just the file path. The wrapper returns a python bool,
	rather than a C BOOL.

	More information can be found at the function's
	`MSDN Documentation <http://msdn.microsoft.com/en-us/library/windows/desktop/aa363855(v=vs.85).aspx>`_.
	"""
	return CreateDirectoryW(fpath, None) != FALSE

RemoveDirectory = kernel32.RemoveDirectoryW
RemoveDirectory.restype = BOOL
RemoveDirectory.argtypes = [LPCWSTR]

GetVolumePathNameW = kernel32.GetVolumePathNameW
GetVolumePathNameW.argtypes = [LPCWSTR, LPWSTR, DWORD]
GetVolumePathNameW.restype = BOOL

def GetVolumePathName(filename):
	""" Retrieves the volume mount point where the specified path is mounted. """
	szbuf = len(filename) + 2
	volbuf = create_unicode_buffer(szbuf)
	if GetVolumePathNameW(filename, volbuf, szbuf):
		raise WinError()
	return volbuf

GetVolumePathNamesForVolumeNameW = kernel32.GetVolumePathNamesForVolumeNameW
GetVolumePathNamesForVolumeNameW.argtypes = [LPCWSTR, LPVOID, DWORD, PDWORD]
GetVolumePathNamesForVolumeNameW.restype = BOOL

def GetVolumePathNamesForVolumeName(volumeguid):
	""" Retrieves a list of drive letters and mounted folder paths for the specified volume. """
	dwsize = DWORD(0)
	GetVolumePathNamesForVolumeNameW(volumeguid, NULL, 0, byref(dwsize))
	if dwsize.value == 0: raise WinError()
	namesbuf = cast(create_unicode_buffer('', dwsize + 1), c_void_p)
	if GetVolumePathNamesForVolumeNameW(volumeguid, namesbuf, dwsize, byref(dwsize)):
		raise WinError()
	bufend = namesbuf.value + dwsize.value
	currname = namesbuf.value
	lresults = []
	while (currname + 2) < bufend:
		name = wstring_at(currname)
		print name
		lresults.append(name)
	return lresults

GetFileAttributesW = kernel32.GetFileAttributesW
GetFileAttributesW.restype = DWORD
GetFileAttributesW.argtypes = [ LPCWSTR ]

GetFileAttributesA = kernel32.GetFileAttributesA
GetFileAttributesA.restype = DWORD
GetFileAttributesA.argtypes = [ LPCSTR ]

GetFileAttributesW.__doc__ = \
GetFileAttributesA.__doc__ = \
	"""
	Used pretty heavily for a number of different tests, but it should be self-explanatory to people who've done
	any Win32 API stuff.

	`MSDN Documentation <http://msdn.microsoft.com/en-us/library/windows/desktop/aa364944(v=vs.85).aspx>`_
	"""

SetFileAttributesW = kernel32.SetFileAttributesW
SetFileAttributesW.restype = BOOL
SetFileAttributesW.argtypes = [ LPCWSTR, DWORD ]

SetFileAttributesA = kernel32.SetFileAttributesA
SetFileAttributesA.restype = BOOL
SetFileAttributesA.argtypes = [ LPCSTR, DWORD ]

SetFileAttributesW.__doc__ = \
SetFileAttributesA.__doc__ = \
	"""
	Sets the attributes for a file or directory.

	`MSDN Documentation <http://msdn.microsoft.com/en-us/library/windows/desktop/aa365535%28v=vs.85%29.aspx>`_
	"""

GetCurrentProcess = kernel32.GetCurrentProcess
GetCurrentProcess.restype = HANDLE
GetCurrentProcess.argtypes = []
GetCurrentProcess.__doc__ = \
	""" Gets a handle to the current process. """

CloseHandle = kernel32.CloseHandle
CloseHandle.restype = BOOL
CloseHandle.argtypes = [HANDLE]
CloseHandle.__doc__ = \
	""" Closes a previously opened handle.. """

DeviceIoControl = kernel32.DeviceIoControl
DeviceIoControl.restype = BOOL
DeviceIoControl.argtypes = [HANDLE, DWORD, LPVOID, DWORD, LPVOID, DWORD, LPDWORD, LPOVERLAPPED]
DeviceIoControl.__doc__ = \
	"""
	Sends a control code directly to a specified device driver, causing the corresponding device to perform the corresponding operation.

		BOOL WINAPI DeviceIoControl(
			_In_         HANDLE hDevice,
			_In_         DWORD dwIoControlCode,
			_In_opt_     LPVOID lpInBuffer,
			_In_         DWORD nInBufferSize,
			_Out_opt_    LPVOID lpOutBuffer,
			_In_         DWORD nOutBufferSize,
			_Out_opt_    LPDWORD lpBytesReturned,
			_Inout_opt_  LPOVERLAPPED lpOverlapped
		);

	`MSDN Documentation <http://msdn.microsoft.com/en-us/library/windows/desktop/aa363216(v=vs.85).aspx>`_
	"""

GetSystemDirectoryW = kernel32.GetSystemDirectoryW
GetSystemDirectoryW.restype = UINT
GetSystemDirectoryW.argtypes = [LPWSTR, UINT]
GetSystemDirectoryW.__doc__ = \
	"""
	Retrieves the path of the system directory. The system directory contains system files such as dynamic-link libraries and drivers.

		UINT WINAPI GetSystemDirectory(
			_Out_  LPTSTR lpBuffer,
			_In_   UINT uSize
		);

	`MSDN Documentation <http://msdn.microsoft.com/en-us/library/windows/desktop/ms724373(v=vs.85).aspx>`_
	"""

def GetSystemDirectory():
	""" Just a wrapper around the C API to provide a parameter-less function."""
	usysbuf = create_unicode_buffer(MAX_PATH + 1)
	if GetSystemDirectoryW(usysbuf, MAX_PATH) == 0: raise WindowsError()
	return usysbuf.value

GetVolumeInformationW = kernel32.GetVolumeInformationW
GetVolumeInformationW.restype = BOOL
GetVolumeInformationW.argtypes = [LPCWSTR, LPWSTR, DWORD, LPDWORD, LPDWORD, LPDWORD, LPWSTR, DWORD]
GetVolumeInformationW.__doc__ = \
	"""
	Retrieves information about the file system and volume associated with the specified root directory.

		BOOL WINAPI GetVolumeInformation(
			_In_opt_   LPCTSTR lpRootPathName,
			_Out_opt_  LPTSTR lpVolumeNameBuffer,
			_In_       DWORD nVolumeNameSize,
			_Out_opt_  LPDWORD lpVolumeSerialNumber,
			_Out_opt_  LPDWORD lpMaximumComponentLength,
			_Out_opt_  LPDWORD lpFileSystemFlags,
			_Out_opt_  LPTSTR lpFileSystemNameBuffer,
			_In_       DWORD nFileSystemNameSize
		);

	`MSDN Documentation <http://msdn.microsoft.com/en-us/library/windows/desktop/aa364993(v=vs.85).aspx>`_
	"""

def GetVolumeInfo(filepath):
	"""
	Return information for the volume containing the given path. This is going
	to be a pair containing (file system, file system flags).
	"""

	# Add 1 for a trailing backslash if necessary, and 1 for the terminating
	# null character.
	volpath = GetVolumePathName(filepath)
	fsnamebuf = create_unicode_buffer(MAX_PATH + 1)
	fsflags = DWORD(0)
	if not GetVolumeInformationW(volpath, None, 0, None, None, byref(fsflags),
			fsnamebuf, len(fsnamebuf)):
		raise WinError()
	return fsnamebuf.value, fsflags.value

GetFileInformationByHandle = kernel32.GetFileInformationByHandle
GetFileInformationByHandle.restype = BOOL
GetFileInformationByHandle.argtypes = [HANDLE, LPBY_HANDLE_FILE_INFORMATION]
GetFileInformationByHandle.__doc__ = \
	"""
	Retrieves file information for the specified file.

		BOOL WINAPI GetFileInformationByHandle(
			_In_   HANDLE hFile,
			_Out_  LPBY_HANDLE_FILE_INFORMATION lpFileInformation
		);

	`MSDN Documentation <http://msdn.microsoft.com/en-us/library/aa364952%28v=vs.85%29.aspx>`_
	"""

def getfileinfo(path):
	"""
	Return information for the file at the given path. This is going to be a
	struct of type BY_HANDLE_FILE_INFORMATION.
	"""
	hfile = CreateFile(path, GENERIC_READ, FILE_SHARE_READ, OPEN_EXISTING, 0)
	if hfile is None: raise WinError()
	info = BY_HANDLE_FILE_INFORMATION()
	rv = GetFileInformationByHandle(hfile, byref(info))
	CloseHandle(hfile)
	if rv == 0: raise WinError()
	return info

try:
	CreateHardLinkW = kernel32.CreateHardLinkW
	CreateHardLinkW.restype = BOOLEAN
	CreateHardLinkW.argtypes = [LPWSTR, LPWSTR, LPSECURITY_ATTRIBUTES]
	CreateHardLinkW.__doc__ = \
		""" BOOLEAN CreateHardLinkW(LPWSTR lpFileName, LPWSTR lpExistingFileName, LPSECURITY_ATTRIBUTES lpSecurityAttributes) """
except:
	CreateHardLinkW = None

try:
	CreateSymbolicLinkW = kernel32.CreateSymbolicLinkW
	CreateSymbolicLinkW.restype = BOOLEAN
	CreateSymbolicLinkW.argtypes = [LPWSTR, LPWSTR, DWORD]
	CreateSymbolicLinkW.__doc__ = \
		""" BOOLEAN CreateSymbolicLinkW(LPWSTR lpSymlinkFileName, LPWSTR lpTargetFileName, DWORD dwFlags) """
except:
	CreateSymbolicLinkW = lambda x, y, z: None

## CTypes Function Call Wrappers


