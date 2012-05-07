from os import path
from ctypes import *
from ctypes.wintypes import *

## Definitions (Constants/Typedefs/Etc)

# The variables below deal with some of the more general stuff. (File
# IO, file access privileges, flags, basic typedefs, etc) There's a few
# flags dealing with reparse points that I left in this section for naming
# consistency.
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000

FILE_SHARE_DELETE = 0x00000004
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
FILE_SHARE_READ_WRITE = 0x00000003 # FILE_SHARE_READ | FILE_SHARE_WRITE

FILE_ATTRIBUTE_DIRECTORY = 16L
FILE_ATTRIBUTE_REPARSE_POINT = 1024L
FILE_ATTRIBUTE_REPARSE_DIRECTORY = 1040L # FILE_ATTRIBUTE_DIRECTORY | FILE_ATTRIBUTE_REPARSE_POINT

OPEN_EXISTING = 3

FILE_FLAG_OPEN_REPARSE_POINT = 2097152
FILE_FLAG_BACKUP_SEMANTICS = 33554432
FILE_FLAG_REPARSE_BACKUP = 35651584 # FILE_FLAG_OPEN_REPARSE_POINT | FILE_FLAG_BACKUP_SEMANTICS

TOKEN_ADJUST_PRIVILEGES = DWORD(32)
SE_PRIVILEGE_ENABLED = 2
SE_RESTORE_NAME = 'SeRestorePrivilege'
SE_BACKUP_NAME = 'SeBackupPrivilege'

LPOVERLAPPED = c_void_p
LPSECURITY_ATTRIBUTES = c_void_p

INVALID_HANDLE_VALUE = -1
MAX_PATH = 260
NULL = 0
ANYSIZE_ARRAY = 1

FALSE = BOOL(0)

# The following definitions are directly related to dealing with reparse
# points.

IO_REPARSE_TAG_MOUNT_POINT = 0xA0000003

FSCTL_GET_REPARSE_POINT = 589992
FSCTL_SET_REPARSE_POINT = 589988
FSCTL_DELETE_REPARSE_POINT = 589996

REPARSE_MOUNTPOINT_HEADER_SIZE = sizeof(ULONG) + (2 * sizeof(USHORT))
MAX_NAME_LENGTH = 1024
MAX_REPARSE_BUFFER = 16 * MAX_NAME_LENGTH


## Structures/Unions

class SymbolicLinkBuffer(Structure):
	"""
	CTypes implementation of:

	struct {
		USHORT SubstituteNameOffset;
		USHORT SubstituteNameLength;
		USHORT PrintNameOffset;
		USHORT PrintNameLength;
		ULONG Flags;
		WCHAR PathBuffer[1];
	} SymbolicLinkReparseBuffer;
	"""

	#noinspection PyTypeChecker
	_fields_ = [
		("SubstituteNameOffset", USHORT),
		("SubstituteNameLength", USHORT),
		("PrintNameOffset", USHORT),
		("PrintNameLength", USHORT),
		("Flags", ULONG),
		# Unfortunately, I can't se this to c_wchar * 1 because it will be too small
		# for our buffer when I call this structure's constructor. Instead, I have to
		# resize it later in the process. For now, I'll add +4 for the \??\, in addition
		# to an extra 2 characters for the two sets of ending \0's
		("PathBuffer", c_wchar * (((MAX_PATH + 1)*2) + 4))
	]

class MountPointBuffer(Structure):
	"""
	CTypes implementation of:

	struct {
		USHORT SubstituteNameOffset;
		USHORT SubstituteNameLength;
		USHORT PrintNameOffset;
		USHORT PrintNameLength;
		WCHAR PathBuffer[1];
	} MountPointReparseBuffer;
	"""

	#noinspection PyTypeChecker
	_fields_ = [
		("SubstituteNameOffset", USHORT),
		("SubstituteNameLength", USHORT),
		("PrintNameOffset", USHORT),
		("PrintNameLength", USHORT),
		# See SymbolicLinkBuffer.PathBuffer for our reasoning.
		("PathBuffer", c_wchar * (((MAX_PATH + 1)*2) + 4))
	]

class GenericReparseBuffer(Structure):
	"""
	CTypes implementation of:

	struct {
		UCHAR  DataBuffer[1];
	} GenericReparseBuffer;
	"""

	#noinspection PyTypeChecker
	_fields_ = [

		("PathBuffer", c_ubyte * (1+MAX_PATH))
	]

class DUMMYUNIONNAME(Union):
	"""
	CTypes implementation of:

	union {
		struct {
			USHORT SubstituteNameOffset;
			USHORT SubstituteNameLength;
			USHORT PrintNameOffset;
			USHORT PrintNameLength;
			ULONG Flags;
			WCHAR PathBuffer[1];
		} SymbolicLinkReparseBuffer;
		struct {
			USHORT SubstituteNameOffset;
			USHORT SubstituteNameLength;
			USHORT PrintNameOffset;
			USHORT PrintNameLength;
			WCHAR PathBuffer[1];
		} MountPointReparseBuffer;
		struct {
			UCHAR  DataBuffer[1];
		} GenericReparseBuffer;
	} DUMMYUNIONNAME;
	"""

	_fields_ = [("SymbolicLink", SymbolicLinkBuffer),
				("MountPoint", MountPointBuffer),
				("Generic", GenericReparseBuffer)]


class ReparsePoint(Structure):
	"""
	CTypes implementation of:

	typedef struct _REPARSE_DATA_BUFFER {
		ULONG  ReparseTag;
		USHORT ReparseDataLength;
		USHORT Reserved;
		union {
			struct {
				USHORT SubstituteNameOffset;
				USHORT SubstituteNameLength;
				USHORT PrintNameOffset;
				USHORT PrintNameLength;
				ULONG Flags;
				WCHAR PathBuffer[1];
			} SymbolicLinkReparseBuffer;
			struct {
				USHORT SubstituteNameOffset;
				USHORT SubstituteNameLength;
				USHORT PrintNameOffset;
				USHORT PrintNameLength;
				WCHAR PathBuffer[1];
			} MountPointReparseBuffer;
			struct {
				UCHAR  DataBuffer[1];
			} GenericReparseBuffer;
		} DUMMYUNIONNAME;
	} REPARSE_DATA_BUFFER, *PREPARSE_DATA_BUFFER;
	"""

	_anonymous_ = ("du",)
	_fields_ = [
		("ReparseTag", ULONG),
		("ReparseDataLength", USHORT),
		("Reserved", USHORT),
		("du", DUMMYUNIONNAME)
	]

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


## Utility Classes (Exceptions, etc)

class InvalidLinkException(Exception):
	"""
	Exception class for when a filepath is specified that is not a symbolic link/junction.
	"""

class InvalidHandleException(Exception):
	"""
	Exception class for when a call to CreateFile returns INVALID_HANDLE (-1).
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
	return HANDLE(windll.kernel32.CreateFileW(
		LPWSTR(filename),
		DWORD(access),
		DWORD(sharemode),
		LPSECURITY_ATTRIBUTES(NULL),
		DWORD(creation),
		DWORD(flags),
		HANDLE(NULL)
	))

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
	return windll.kernel32.CreateDirectoryW(LPWSTR(fpath), LPSECURITY_ATTRIBUTES(NULL)) != FALSE

def RemoveDirectory(fpath):
	"""
	Self-explanatory. Returns a python bool::

		BOOL WINAPI RemoveDirectory(
			__in  LPCTSTR lpPathName
		);

	`MSDN Documentation <http://msdn.microsoft.com/en-us/library/windows/desktop/aa365488(v=vs.85).aspx>`_
	"""
	return windll.kernel32.RemoveDirectoryW(LPWSTR(fpath)) != FALSE

def GetFileAttributes(fpath):
	"""
	Used pretty heavily for a number of different tests, but it should be self-explanatory to people who've done
	any Win32 API stuff.

	`MSDN Documentation <http://msdn.microsoft.com/en-us/library/windows/desktop/aa364944(v=vs.85).aspx>`_
	"""
	return windll.kernel32.GetFileAttributesW(LPWSTR(fpath))

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
	result against the FILE_ATTRIBUTE_REPARSE_DIRECTORY flag. (which is just::

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
	hProcess = HANDLE(windll.kernel32.GetCurrentProcess())
	lpName = SE_RESTORE_NAME if readwrite else SE_BACKUP_NAME
	if not windll.advapi32.OpenProcessToken(hProcess, TOKEN_ADJUST_PRIVILEGES, byref(hToken)) != FALSE:
		raise Exception('Could not open current process security token.')
	if not windll.advapi32.LookupPrivilegeValueW(LPWSTR(NULL), LPWSTR(lpName), byref(tp.Privileges[0].Luid)) != FALSE:
		windll.kernel32.CloseHandle(hToken)
		raise Exception('Could not look up %s privilege.' % lpName)
	tp.PrivilegeCount = 1
	tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED
	if not windll.advapi32.AdjustTokenPrivileges(hToken, FALSE, byref(tp), DWORD(sizeof(TokenPrivileges)), None, None) != FALSE:
		windll.kernel32.CloseHandle(hToken)
		raise Exception('Could not adjust current process\'s security privileges.')
	windll.kernel32.CloseHandle(hToken)

def CalculateLength(bufferType, buff):
	"""
	Used internally to find the ReparseDataLength and the size of the PathBuffer to allocate.

	It returns a tuple containing (PathBufferLength, ReparseDataLength).
	"""
	bufflen = buff.PrintNameOffset + buff.PrintNameLength + sizeof(c_wchar) # Ending \0
	return bufflen, bufferType.PathBuffer.offset + bufflen