from os import path
from typedecls import *

# Some common configuration stuff that will be changed as the module auto-detects
# the current machine's capabilities.
has_hardlink_support = True
#supports_mountpoints = True


## CTypes Function Prototypes

##########################
# Kernel32.dll Functions #
##########################

kernel32 = WinDLL('kernel32.dll')

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

GetVolumeInformationW = kernel32.GetVolumeInformationW
GetVolumeInformationW.restype = BOOL
GetVolumeInformationW.argtypes = [LPCWSTR, LPWSTR, DWORD, LPDWORD, LPDWORD, LPDWORD, LPWSTR, DWORD]
GetVolumeInformationW.__doc__ = \
"""BOOL GetVolumeInformationW(LPCWSTR lpRootPathName, LPWSTR lpVolumeNameBuffer, DWORD nVolumeNameSize, LPDWORD lpVolumeSerialNumber, LPDWORD lpMaximumComponentLength, LPDWORD lpFileSystemFlags, LPWSTR lpFileSystemNameBuffer, DWORD nFileSystemNameSize)"""

try:
	CreateHardLinkW = kernel32.CreateHardLinkW
	CreateHardLinkW.restype = BOOLEAN
	CreateHardLinkW.argtypes = [LPWSTR, LPWSTR, LPSECURITY_ATTRIBUTES]
	CreateHardLinkW.__doc__ = \
	""" BOOLEAN CreateHardLinkW(LPWSTR lpFileName, LPWSTR lpExistingFileName, LPSECURITY_ATTRIBUTES lpSecurityAttributes) """
except:
	has_hardlink_support = False

##########################
# AdvApi32.dll Functions #
##########################

advapi32 = WinDLL('advapi32.dll')

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


def IsFolder(fpath):
	"""
	Checks whether a given path is a folder by using the GetFileAttributes call and testing the result against the
	FILE_ATTRIBUTE_DIRECTORY flag.
	"""
	return True if GetFileAttributes(fpath) & FILE_ATTRIBUTE_DIRECTORY else False

def IsReparsePoint(fpath):
	"""
	Checks whether a given path is a reparse point by using the GetFileAttributes call and testing the result against
	the FILE_ATTRIBUTE_REPARSE_POINT flag.
	"""
	return True if GetFileAttributes(fpath) & FILE_ATTRIBUTE_REPARSE_POINT else False

def IsReparseDir(fpath):
	"""
	Checks whether a given path is a reparse point and a folder by using the GetFileAttributes call and testing the
	result against the FILE_ATTRIBUTE_REPARSE_DIRECTORY flag. (which is just:
		FILE_ATTRIBUTE_DIRECTORY | FILE_ATTRIBUTE_REPARSE_POINT
	)
	"""
	return True if GetFileAttributes(fpath) & FILE_ATTRIBUTE_REPARSE_DIRECTORY else False

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

def _OpenFileForIO(filepath, generic, share, backup):
	flag = FILE_FLAG_OPEN_REPARSE_POINT
	if backup:
		ObtainRestorePrivilege()
		flag = FILE_FLAG_REPARSE_BACKUP
	hFile = CreateFile(filepath, generic, share, OPEN_EXISTING, flag)
	if hFile == HANDLE(INVALID_HANDLE_VALUE):
		raise InvalidHandleException('Failed to open path: %s' % filepath)
	return hFile

def OpenFileForRead(filepath, backup = False):
	""" Opens a file for reading. """
	return _OpenFileForIO(filepath, GENERIC_READ, FILE_SHARE_READ, backup)

def OpenFileForWrite(filepath, backup = False):
	""" Opens a file for writing/deleting. """
	return _OpenFileForIO(filepath, GENERIC_WRITE, FILE_SHARE_ALL, backup)

def CalculateLength(bufferType, buff):
	"""
	Used internally to find the ReparseDataLength and the size of the PathBuffer to allocate.

	It returns a tuple containing (PathBufferLength, ReparseDataLength).
	"""
	bufflen = buff.PrintNameOffset + buff.PrintNameLength + SZWCHAR # Ending \0
	return bufflen, bufferType.PathBuffer.offset + bufflen