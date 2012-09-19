from consts import *

## Type Definitions
# First, we'll do all of our stupid MS-specific typedecl's
CHAR = c_char
UCHAR = c_ubyte

LPOVERLAPPED = c_void_p
LPSECURITY_ATTRIBUTES = c_void_p

PHANDLE = POINTER(HANDLE)
LPHANDLE = PHANDLE

PWORD = POINTER(WORD)
LPWORD = PWORD
PDWORD = POINTER(DWORD)
LPDWORD = PDWORD
DEVICE_TYPE = DWORD

ULONG_PTR = ULONG
PULONG_PTR = POINTER(ULONG_PTR)
LONG_PTR = c_long
PLONG_PTR = POINTER(LONG_PTR)

SIZE_T = ULONG_PTR
PSIZE_T = POINTER(SIZE_T)
SSIZE_T = LONG_PTR
PSSIZE_T = POINTER(SSIZE_T)

# Char-size constants
SZCHAR = sizeof(CHAR)
SZWCHAR = sizeof(WCHAR)
SZUCHAR = sizeof(UCHAR)

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
		# Unfortunately, I can't set this to c_wchar * 1 because it will be too small
		# for our buffer when I call this structure's constructor. Instead, I have to
		# resize it later in the process. For now, I'll add +4 for the \??\, in addition
		# to an extra 2 characters for the two sets of ending \0's
		("PathBuffer", WCHAR * (((MAX_PATH + 1)*2) + 4))
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
		("PathBuffer", WCHAR * (((MAX_PATH + 1)*2) + 4))
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
		("PathBuffer", UCHAR * (1+MAX_PATH))
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


BYTES8 = (BYTE * 8)

class GUID(Structure):
	"""
	CTypes implementation of:

		typedef struct _GUID {
			DWORD Data1;
			WORD  Data2;
			WORD  Data3;
			BYTE  Data4[8];
		} GUID;
	"""
	_fields_ = [
		("Data1", DWORD),
		("Data2", WORD),
		("Data3", WORD),
		("Data4", BYTES8),

	]

class ReparseGuidDataBuffer(Structure):
	"""
	CTypes implementation of:

	typedef struct _REPARSE_GUID_DATA_BUFFER {
		DWORD  ReparseTag;
		WORD   ReparseDataLength;
		WORD   Reserved;
		GUID   ReparseGuid;
		-- ReparsePointBuffer ---
	} REPARSE_GUID_DATA_BUFFER, *PREPARSE_GUID_DATA_BUFFER;
	"""
	_anonymous_ = ("du",)
	_fields_ = [
		("ReparseTag", ULONG),
		("ReparseDataLength", USHORT),
		("Reserved", USHORT),
		("ReparseGuid",GUID),
		("du", DUMMYUNIONNAME)
	]

PReparseGuidDataBuffer = POINTER(ReparseGuidDataBuffer)

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

PLUID = POINTER(LUID)

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

PTokenPrivileges = POINTER(TokenPrivileges)

## Utility Classes (Exceptions, etc)

class InvalidLinkException(Exception):
	"""
	Exception class for when a filepath is specified that is not a symbolic link/junction.
	"""

class InvalidHandleException(Exception):
	"""
	Exception class for when a call to CreateFile returns INVALID_HANDLE (-1).
	"""
