from os import path
from ctypes import *
from ctypes.wintypes import *

#class MountPointReparseBuffer(Structure):
#	_fields_ = [
#		("SubstituteNameOffset", c_ushort),
#		("SubstituteNameLength", c_ushort),
#		("PrintNameOffset", c_ushort),
#		("PrintNameLength", c_ushort),
#		("PathBuffer", c_wchar_p)
#	]
#("Buffer", MountPointReparseBuffer)

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

IO_REPARSE_TAG_MOUNT_POINT = 0xA0000003

FSCTL_GET_REPARSE_POINT = 589992
FSCTL_SET_REPARSE_POINT = 589988
FSCTL_DELETE_REPARSE_POINT = 589996

REPARSE_MOUNTPOINT_HEADER_SIZE = 8
MAX_NAME_LENGTH = 1024
MAX_REPARSE_BUFFER = 16 * MAX_NAME_LENGTH

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

# Structures

class ReparsePoint(Structure):
	"""
	CTypes implementation of:

	typedef struct {
			DWORD	ReparseTag;
			DWORD	ReparseDataLength;
			WORD	Reserved;
			WORD	ReparseTargetLength;
			WORD	ReparseTargetMaximumLength;
			WORD	Reserved1;
			WCHAR	ReparseTarget[1];
	} REPARSE_MOUNTPOINT_DATA_BUFFER, *PREPARSE_MOUNTPOINT_DATA_BUFFER;
	"""

	#noinspection PyTypeChecker
	_fields_ = [
		("ReparseTag", DWORD),
		("ReparseDataLength", DWORD),
		("Reserved", WORD),

		("ReparseTargetLength", WORD),
		("ReparseTargetMaximumLength", WORD),
		("Reserved1", WORD),
		("ReparseTarget", c_wchar * (MAX_PATH + 4)), # +4 for the \??\
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


# Exception Classes
class InvalidLinkException(Exception):
	"""
	Exception class for when a filepath is specified that is not a symbolic link/junction.
	"""

class InvalidHandleException(Exception):
	"""
	Exception class for when a call to CreateFile returns INVALID_HANDLE (-1).
	"""

def CreateFile(filename, access, sharemode, creation, flags):
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
	return windll.kernel32.CreateDirectoryW(LPWSTR(fpath), LPSECURITY_ATTRIBUTES(NULL)) != FALSE

def RemoveDirectory(fpath):
	return windll.kernel32.RemoveDirectoryW(LPWSTR(fpath)) != FALSE

def GetFileAttributes(fpath):
	return windll.kernel32.GetFileAttributesW(LPWSTR(fpath))

def IsFolder(fpath):
	return True if GetFileAttributes(fpath) & FILE_ATTRIBUTE_DIRECTORY else False

def IsReparsePoint(fpath):
	return True if GetFileAttributes(fpath) & FILE_ATTRIBUTE_REPARSE_POINT else False

def IsReparseDir(fpath):
	return True if GetFileAttributes(fpath) & FILE_ATTRIBUTE_REPARSE_DIRECTORY else False

def TranslatePath(fpath):
	fpath = path.abspath(fpath)
	if fpath[len(fpath)-1] == '\\' and fpath[len(fpath)-2] == ':':
		fpath = fpath[:len(fpath)-1]
	return '\\??\\%s\0' % fpath

def ObtainRestorePrivilege(readwrite = False):
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

