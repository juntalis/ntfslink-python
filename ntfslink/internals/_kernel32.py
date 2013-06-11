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
#define FILE_ATTRIBUTE_READONLY             0x00000001
#define FILE_ATTRIBUTE_HIDDEN               0x00000002
#define FILE_ATTRIBUTE_SYSTEM               0x00000004
#define FILE_ATTRIBUTE_DIRECTORY            0x00000010
#define FILE_ATTRIBUTE_ARCHIVE              0x00000020
#define FILE_ATTRIBUTE_DEVICE               0x00000040
#define FILE_ATTRIBUTE_NORMAL               0x00000080
#define FILE_ATTRIBUTE_TEMPORARY            0x00000100
#define FILE_ATTRIBUTE_SPARSE_FILE          0x00000200
#define FILE_ATTRIBUTE_REPARSE_POINT        0x00000400
#define FILE_ATTRIBUTE_COMPRESSED           0x00000800
#define FILE_ATTRIBUTE_OFFLINE              0x00001000
#define FILE_ATTRIBUTE_NOT_CONTENT_INDEXED  0x00002000
#define FILE_ATTRIBUTE_ENCRYPTED            0x00004000
#define FILE_ATTRIBUTE_VIRTUAL              0x00010000
#define FILE_NOTIFY_CHANGE_FILE_NAME    0x00000001
#define FILE_NOTIFY_CHANGE_DIR_NAME     0x00000002
#define FILE_NOTIFY_CHANGE_ATTRIBUTES   0x00000004
#define FILE_NOTIFY_CHANGE_SIZE         0x00000008
#define FILE_NOTIFY_CHANGE_LAST_WRITE   0x00000010
#define FILE_NOTIFY_CHANGE_LAST_ACCESS  0x00000020
#define FILE_NOTIFY_CHANGE_CREATION     0x00000040
#define FILE_NOTIFY_CHANGE_SECURITY     0x00000100
#define FILE_ACTION_ADDED                   0x00000001
#define FILE_ACTION_REMOVED                 0x00000002
#define FILE_ACTION_MODIFIED                0x00000003
#define FILE_ACTION_RENAMED_OLD_NAME        0x00000004
#define FILE_ACTION_RENAMED_NEW_NAME        0x00000005
#define MAILSLOT_NO_MESSAGE             ((DWORD)-1)
#define MAILSLOT_WAIT_FOREVER           ((DWORD)-1)
#define FILE_CASE_SENSITIVE_SEARCH          0x00000001
#define FILE_CASE_PRESERVED_NAMES           0x00000002
#define FILE_UNICODE_ON_DISK                0x00000004
#define FILE_PERSISTENT_ACLS                0x00000008
#define FILE_FILE_COMPRESSION               0x00000010
#define FILE_VOLUME_QUOTAS                  0x00000020
#define FILE_SUPPORTS_SPARSE_FILES          0x00000040
#define FILE_SUPPORTS_REPARSE_POINTS        0x00000080
#define FILE_SUPPORTS_REMOTE_STORAGE        0x00000100
#define FILE_VOLUME_IS_COMPRESSED           0x00008000
#define FILE_SUPPORTS_OBJECT_IDS            0x00010000
#define FILE_SUPPORTS_ENCRYPTION            0x00020000
#define FILE_NAMED_STREAMS                  0x00040000
#define FILE_READ_ONLY_VOLUME               0x00080000
#define FILE_SEQUENTIAL_WRITE_ONCE          0x00100000
#define FILE_SUPPORTS_TRANSACTIONS          0x00200000
#define FILE_SUPPORTS_HARD_LINKS            0x00400000
#define FILE_SUPPORTS_EXTENDED_ATTRIBUTES   0x00800000
#define FILE_SUPPORTS_OPEN_BY_FILE_ID       0x01000000
#define FILE_SUPPORTS_USN_JOURNAL           0x02000000

# File command codes
FILE_READ_DATA = 0x0001
FILE_LIST_DIRECTORY = 0x0001
FILE_WRITE_DATA = 0x0002
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

# File attribute codes
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

class BY_HANDLE_FILE_INFORMATION(Structure):
	"""
	Ctypes implementation of

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
		("dwFileAttributes", DWORD),
		("ftCreationTime", FILETIME),
		("ftLastAccessTime", FILETIME),
		("ftLastWriteTime", FILETIME),
		("dwVolumeSerialNumber", DWORD),
		("nFileSizeHigh", DWORD),
		("nFileSizeLow", DWORD),
		("nNumberOfLinks", DWORD),
		("nFileIndexHigh", DWORD),
		("nFileIndexLow", DWORD)
	]


## Functions exported from kernel32.dll
CreateFileW = kernel32.CreateFileW
CreateFileW.restype = HANDLE
CreateFileW.argtypes = [LPCWSTR, DWORD, DWORD, LPSECURITY_ATTRIBUTES, DWORD, DWORD, HANDLE]
CreateFileW.__doc__ = \
""" HANDLE CreateFileW(LPCWSTR lpFileName, DWORD dwDesiredAccess, DWORD dwShareMode, LPSECURITY_ATTRIBUTES lpSecurityAttributes, DWORD dwCreationDisposition, DWORD dwFlagsAndAttributes, HANDLE hTemplateFile) """

CreateDirectoryW = kernel32.CreateDirectoryW
CreateDirectoryW.restype = BOOL
CreateDirectoryW.argtypes = [LPCWSTR, LPSECURITY_ATTRIBUTES]
CreateDirectoryW.__doc__ = \
""" BOOL CreateDirectoryW(LPCWSTR lpPathName, LPSECURITY_ATTRIBUTES lpSecurityAttributes) """

RemoveDirectory = kernel32.RemoveDirectoryW
RemoveDirectory.restype = BOOL
RemoveDirectory.argtypes = [LPCWSTR]
RemoveDirectory.__doc__ = \
"""
Self-explanatory.

	BOOL WINAPI RemoveDirectory(
		__in  LPCTSTR lpPathName
	);

`MSDN Documentation <http://msdn.microsoft.com/en-us/library/windows/desktop/aa365488(v=vs.85).aspx>`_
"""

GetFileAttributes = kernel32.GetFileAttributesW
GetFileAttributes.restype = DWORD
GetFileAttributes.argtypes = [LPCWSTR]
GetFileAttributes.__doc__ = \
"""
Used pretty heavily for a number of different tests, but it should be self-explanatory to people who've done
any Win32 API stuff.

`MSDN Documentation <http://msdn.microsoft.com/en-us/library/windows/desktop/aa364944(v=vs.85).aspx>`_
"""

GetCurrentProcess = kernel32.GetCurrentProcess
GetCurrentProcess.restype = HANDLE
GetCurrentProcess.argtypes = []
GetCurrentProcess.__doc__ = \
""" Gets a handle to the current process. """

CloseHandle = kernel32.CloseHandle
CloseHandle.restype = BOOL
CloseHandle.argtypes = [ HANDLE ]
CloseHandle.__doc__ = \
""" Closes a previously opened handle.. """

DeviceIoControl = kernel32.DeviceIoControl
DeviceIoControl.restype = BOOL
DeviceIoControl.argtypes = [HANDLE, DWORD, LPVOID, DWORD, LPVOID, DWORD, LPDWORD, LPOVERLAPPED]
DeviceIoControl.__doc__ =\
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
GetSystemDirectoryW.__doc__ =\
"""
Retrieves the path of the system directory. The system directory contains system files such as dynamic-link libraries and drivers.

	UINT WINAPI GetSystemDirectory(
		_Out_  LPTSTR lpBuffer,
		_In_   UINT uSize
	);

`MSDN Documentation <http://msdn.microsoft.com/en-us/library/windows/desktop/ms724373(v=vs.85).aspx>`_
"""

GetVolumeInformation = kernel32.GetVolumeInformationW
GetVolumeInformation.restype = BOOL
GetVolumeInformation.argtypes = [ LPCWSTR, LPWSTR, DWORD, LPDWORD, LPDWORD, LPDWORD, LPWSTR, DWORD ]
GetVolumeInformation.__doc__ = \
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
	CreateSymbolicLinkW = lambda x,y,z: None

## CTypes Function Call Wrappers

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
	return CreateFileW(filename, access, sharemode, None, creation, flags, None)

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

def GetSystemDirectory():
	""" Just a wrapper around the C API to provide a parameter-less function."""
	buf = create_unicode_buffer(MAX_PATH+1)
	if GetSystemDirectoryW(buf, MAX_PATH) == 0: raise WindowsError()
	return buf.value
