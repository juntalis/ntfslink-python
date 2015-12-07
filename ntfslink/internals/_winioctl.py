# encoding: utf-8
"""
_winioctl.py
Python implementations of some of the definitions/declarations in winioctl.h

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
from .structures import *
from .consts import FILE_DEVICE_FILE_SYSTEM, CTL_CODE,\
	METHOD_BUFFERED, FILE_ANY_ACCESS, METHOD_NEITHER, \
	FILE_SPECIAL_ACCESS, FILE_READ_DATA, FILE_WRITE_DATA, \
	MAX_PATH

MAX_NAME_LENGTH = 1024
MAX_REPARSE_BUFFER = 16 * MAX_NAME_LENGTH

# Symbolic link flags
SYMBOLIC_LINK_FLAG_RELATIVE = 1
SYMBOLIC_LINK_FLAG_FILE = 0x0
SYMBOLIC_LINK_FLAG_DIRECTORY = 0x1

IO_REPARSE_TAG_RESERVED_ZERO   = 0x00000000
IO_REPARSE_TAG_RESERVED_ONE    = 0x00000001
IO_REPARSE_TAG_RESERVED_RANGE  = IO_REPARSE_TAG_RESERVED_ONE

IO_REPARSE_TAG_MOUNT_POINT   = 0xA0000003L
IO_REPARSE_TAG_HSM           = 0xC0000004L
IO_REPARSE_TAG_HSM2          = 0x80000006L
IO_REPARSE_TAG_SIS           = 0x80000007L
IO_REPARSE_TAG_WIM           = 0x80000008L
IO_REPARSE_TAG_CSV           = 0x80000009L
IO_REPARSE_TAG_DFS           = 0x8000000AL
IO_REPARSE_TAG_DFSR          = 0x80000012L
IO_REPARSE_TAG_SYMBOLIC_LINK = 0xA000000CL

FSCTL_FILESYSTEM_GET_STATISTICS = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 24, METHOD_BUFFERED, FILE_ANY_ACCESS) # FILESYSTEM_STATISTICS
FSCTL_FIND_FILES_BY_SID = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 35, METHOD_NEITHER, FILE_ANY_ACCESS)

FSCTL_GET_NTFS_VOLUME_DATA = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 25, METHOD_BUFFERED, FILE_ANY_ACCESS)
FSCTL_GET_NTFS_FILE_RECORD = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 26, METHOD_BUFFERED, FILE_ANY_ACCESS)

FSCTL_SET_OBJECT_ID = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 38, METHOD_BUFFERED, FILE_SPECIAL_ACCESS) # FILE_OBJECTID_BUFFER
FSCTL_GET_OBJECT_ID = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 39, METHOD_BUFFERED,FILE_ANY_ACCESS) # FILE_OBJECTID_BUFFER
FSCTL_DELETE_OBJECT_ID = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 40, METHOD_BUFFERED, FILE_SPECIAL_ACCESS)

FSCTL_GET_COMPRESSION = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 15, METHOD_BUFFERED, FILE_ANY_ACCESS)
FSCTL_SET_COMPRESSION = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 16, METHOD_BUFFERED, FILE_READ_DATA | FILE_WRITE_DATA)

FSCTL_SET_REPARSE_POINT = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 41, METHOD_BUFFERED, FILE_SPECIAL_ACCESS)
FSCTL_GET_REPARSE_POINT = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 42, METHOD_BUFFERED, FILE_ANY_ACCESS)
FSCTL_DELETE_REPARSE_POINT = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 43, METHOD_BUFFERED, FILE_SPECIAL_ACCESS)

# Reparse Tags
def IsReparseTagMicrosoft(reparse_tag): return (reparse_tag & 0x80000000) == 0x80000000
def IsReparseTagNameSurrogate(reparse_tag): return (reparse_tag & 0x20000000) == 0x20000000

# Reparse Point buffer constants
REPARSE_POINT_HEADER_SIZE = sizeof(DWORD) + (2 * sizeof(WORD))
REPARSE_GUID_DATA_BUFFER_HEADER_SIZE = REPARSE_POINT_HEADER_SIZE + sizeof(GUID)

# Unfortunately, I can't set this to c_wchar * 1 because it will be too small
# for our buffer when I call this structure's constructor. Instead, I have to
# resize it later in the process. For now, I'll add +4 for the \??\, in addition
# to an extra 2 characters for the two sets of ending \0's
MAX_REPARSE_PATH_BUFFER = (((MAX_PATH + 1)*2) + 4)

# For our generic reparse buffer
MAX_GENERIC_REPARSE_BUFFER = MAX_REPARSE_BUFFER - REPARSE_GUID_DATA_BUFFER_HEADER_SIZE

class DummyReparseBuffer(Structure):
	""" Common fields for mount points and symbolic links
	"""
	_fields_ = [
		('SubstituteNameOffset', USHORT),
		('SubstituteNameLength', USHORT),
		('PrintNameOffset', USHORT),
		('PrintNameLength', USHORT),
	]

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
		('SubstituteNameOffset', USHORT),
		('SubstituteNameLength', USHORT),
		('PrintNameOffset', USHORT),
		('PrintNameLength', USHORT),
		('Flags', ULONG),
		('PathBuffer', WCHAR * MAX_REPARSE_PATH_BUFFER)
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

		# See SymbolicLinkBuffer.PathBuffer for our reasoning.
		('PathBuffer', WCHAR * MAX_REPARSE_PATH_BUFFER)
	]

class GenericReparseBuffer(Structure):
	"""
	CTypes implementation of:

	struct {
		UCHAR  DataBuffer[1];
	} GenericReparseBuffer;
	"""

	#noinspection PyTypeChecker
	_fields_ = [ ('PathBuffer', UCHAR * MAX_GENERIC_REPARSE_BUFFER) ]

class ReparsePoint(Structure):
	"""
	typedef struct _REPARSE_DATA_BUFFER {
		ULONG ReparseTag;
		USHORT ReparseDataLength;
		USHORT Reserved;
		union DUMMYUNIONNAME;
	} REPARSE_DATA_BUFFER, *PREPARSE_DATA_BUFFER;
	"""
	class ReparsePointVariations(Union):
		"""
		union {
			struct SymbolicLinkReparseBuffer;
			struct MountPointReparseBuffer;
			struct GenericReparseBuffer;
		} DUMMYUNIONNAME;
		"""
		_fields_ = [
			('SymbolicLink', SymbolicLinkBuffer),
			('MountPoint', MountPointBuffer),
			('Generic', GenericReparseBuffer)
		]

	_anonymous_ = ('du',)
	_fields_ = [
		('ReparseTag', ULONG),
		('ReparseDataLength', USHORT),
		('Reserved', USHORT),
		('du', ReparsePointVariations)
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
	_anonymous_ = ('du',)
	_fields_ = [
		('ReparseTag', ULONG),
		('ReparseDataLength', USHORT),
		('Reserved', USHORT),
		('ReparseGuid', GUID),
		('du', ReparsePoint.ReparsePointVariations)
	]

PReparseGuidDataBuffer = POINTER(ReparseGuidDataBuffer)

class NTFS_FILE_RECORD_INPUT_BUFFER(Structure):
	"""
	CTypes implementation of:

		typedef struct {
			LARGE_INTEGER FileReferenceNumber;
		} NTFS_FILE_RECORD_INPUT_BUFFER, *PNTFS_FILE_RECORD_INPUT_BUFFER;
	"""
	_fields_ = [
		('FileReferenceNumber', LARGE_INTEGER)
	]

BytesPerFileRecordSegment = 1024

class NTFS_FILE_RECORD_OUTPUT_BUFFER(Structure):
	"""
	Ctypes implementation of

		typedef struct {
			LARGE_INTEGER FileReferenceNumber;
			DWORD FileRecordLength;
			BYTE FileRecordBuffer[1];
		} NTFS_FILE_RECORD_OUTPUT_BUFFER, *PNTFS_FILE_RECORD_OUTPUT_BUFFER;
	"""
	_fields_ = [
		('FileReferenceNumber', LARGE_INTEGER),
		('FileRecordLength', DWORD),
		('FileRecordBuffer', BYTE * BytesPerFileRecordSegment),
	]

	@property
	def length(self):
		return self.FileRecordLength

	@property
	def bytes(self):
		res = []
		for b in self.FileRecordBuffer:
			res.append(b)
		return res

	@property
	def raw(self):
		return ''.join(map(chr, self.bytes))

