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
from _windows import *

## Macros
def CTL_CODE(DeviceType, Function, Method, Access): return (DeviceType << 16) | (Access << 14) | (Function << 2) | Method
def DEVICE_TYPE_FROM_CTL_CODE(ctrlCode): return (ctrlCode & 0xffff0000) >> 16
def METHOD_FROM_CTL_CODE(ctrlCode): return ctrlCode & 3

# File Device codes
FILE_DEVICE_BEEP = 0x00000001
FILE_DEVICE_CD_ROM = 0x00000002
FILE_DEVICE_CD_ROM_FILE_SYSTEM = 0x00000003
FILE_DEVICE_CONTROLLER = 0x00000004
FILE_DEVICE_DATALINK = 0x00000005
FILE_DEVICE_DFS = 0x00000006
FILE_DEVICE_DISK = 0x00000007
FILE_DEVICE_DISK_FILE_SYSTEM = 0x00000008
FILE_DEVICE_FILE_SYSTEM = 0x00000009
FILE_DEVICE_INPORT_PORT = 0x0000000a
FILE_DEVICE_KEYBOARD = 0x0000000b
FILE_DEVICE_MAILSLOT = 0x0000000c
FILE_DEVICE_MIDI_IN = 0x0000000d
FILE_DEVICE_MIDI_OUT = 0x0000000e
FILE_DEVICE_MOUSE = 0x0000000f
FILE_DEVICE_MULTI_UNC_PROVIDER = 0x00000010
FILE_DEVICE_NAMED_PIPE = 0x00000011
FILE_DEVICE_NETWORK = 0x00000012
FILE_DEVICE_NETWORK_BROWSER = 0x00000013
FILE_DEVICE_NETWORK_FILE_SYSTEM = 0x00000014
FILE_DEVICE_NULL = 0x00000015
FILE_DEVICE_PARALLEL_PORT = 0x00000016
FILE_DEVICE_PHYSICAL_NETCARD = 0x00000017
FILE_DEVICE_PRINTER = 0x00000018
FILE_DEVICE_SCANNER = 0x00000019
FILE_DEVICE_SERIAL_MOUSE_PORT = 0x0000001a
FILE_DEVICE_SERIAL_PORT = 0x0000001b
FILE_DEVICE_SCREEN = 0x0000001c
FILE_DEVICE_SOUND = 0x0000001d
FILE_DEVICE_STREAMS = 0x0000001e
FILE_DEVICE_TAPE = 0x0000001f
FILE_DEVICE_TAPE_FILE_SYSTEM = 0x00000020
FILE_DEVICE_TRANSPORT = 0x00000021
FILE_DEVICE_UNKNOWN = 0x00000022
FILE_DEVICE_VIDEO = 0x00000023
FILE_DEVICE_VIRTUAL_DISK = 0x00000024
FILE_DEVICE_WAVE_IN = 0x00000025
FILE_DEVICE_WAVE_OUT = 0x00000026
FILE_DEVICE_8042_PORT = 0x00000027
FILE_DEVICE_NETWORK_REDIRECTOR = 0x00000028
FILE_DEVICE_BATTERY = 0x00000029
FILE_DEVICE_BUS_EXTENDER = 0x0000002a
FILE_DEVICE_MODEM = 0x0000002b
FILE_DEVICE_VDM = 0x0000002c
FILE_DEVICE_MASS_STORAGE = 0x0000002d
FILE_DEVICE_SMB = 0x0000002e
FILE_DEVICE_KS = 0x0000002f
FILE_DEVICE_CHANGER = 0x00000030
FILE_DEVICE_SMARTCARD = 0x00000031
FILE_DEVICE_ACPI = 0x00000032
FILE_DEVICE_DVD = 0x00000033
FILE_DEVICE_FULLSCREEN_VIDEO = 0x00000034
FILE_DEVICE_DFS_FILE_SYSTEM = 0x00000035
FILE_DEVICE_DFS_VOLUME = 0x00000036
FILE_DEVICE_SERENUM = 0x00000037
FILE_DEVICE_TERMSRV = 0x00000038
FILE_DEVICE_KSEC = 0x00000039
FILE_DEVICE_FIPS = 0x0000003A
FILE_DEVICE_INFINIBAND = 0x0000003B
FILE_DEVICE_VMBUS = 0x0000003E
FILE_DEVICE_CRYPT_PROVIDER = 0x0000003F
FILE_DEVICE_WPD = 0x00000040
FILE_DEVICE_BLUETOOTH = 0x00000041
FILE_DEVICE_MT_COMPOSITE = 0x00000042
FILE_DEVICE_MT_TRANSPORT = 0x00000043
FILE_DEVICE_BIOMETRIC = 0x00000044
FILE_DEVICE_PMI = 0x00000045

# Methods
METHOD_BUFFERED = 0
METHOD_IN_DIRECT = 1
METHOD_OUT_DIRECT = 2
METHOD_NEITHER = 3

METHOD_DIRECT_TO_HARDWARE = METHOD_IN_DIRECT
METHOD_DIRECT_FROM_HARDWARE = METHOD_OUT_DIRECT

# Reparse Point buffer constants
REPARSE_POINT_HEADER_SIZE = sizeof(DWORD) + (2 * sizeof(WORD))
REPARSE_GUID_DATA_BUFFER_HEADER_SIZE = REPARSE_POINT_HEADER_SIZE + sizeof(GUID)

MAX_NAME_LENGTH = 1024
MAX_REPARSE_BUFFER = 16 * MAX_NAME_LENGTH

# Symbolic link flags
SYMBOLIC_LINK_FLAG_RELATIVE = 1
SYMBOLIC_LINK_FLAG_FILE = 0x0
SYMBOLIC_LINK_FLAG_DIRECTORY = 0x1

# Reparse Tags
def IsReparseTagMicrosoft(reparse_tag): return (reparse_tag & 0x80000000) == 0x80000000
def IsReparseTagNameSurrogate(reparse_tag): return (reparse_tag & 0x20000000) == 0x20000000

IO_REPARSE_TAG_RESERVED_ZERO   = 0x00000000
IO_REPARSE_TAG_RESERVED_ONE    = 0x00000001
IO_REPARSE_TAG_RESERVED_RANGE  = IO_REPARSE_TAG_RESERVED_ONE

IO_REPARSE_TAG_MOUNT_POINT = 0xA0000003L
IO_REPARSE_TAG_HSM = 0xC0000004L
IO_REPARSE_TAG_HSM2 = 0x80000006L
IO_REPARSE_TAG_SIS = 0x80000007L
IO_REPARSE_TAG_WIM = 0x80000008L
IO_REPARSE_TAG_CSV = 0x80000009L
IO_REPARSE_TAG_DFS = 0x8000000AL
IO_REPARSE_TAG_DFSR = 0x80000012L
IO_REPARSE_TAG_SYMBOLIC_LINK = 0xA000000CL

FSCTL_FILESYSTEM_GET_STATISTICS = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 24, METHOD_BUFFERED, FILE_ANY_ACCESS) # FILESYSTEM_STATISTICS
FSCTL_GET_NTFS_VOLUME_DATA = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 25, METHOD_BUFFERED, FILE_ANY_ACCESS)
FSCTL_GET_NTFS_FILE_RECORD = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 26, METHOD_BUFFERED, FILE_ANY_ACCESS)
FSCTL_FIND_FILES_BY_SID = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 35, METHOD_NEITHER, FILE_ANY_ACCESS)

FSCTL_SET_OBJECT_ID = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 38, METHOD_BUFFERED, FILE_SPECIAL_ACCESS) # FILE_OBJECTID_BUFFER
FSCTL_GET_OBJECT_ID = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 39, METHOD_BUFFERED,FILE_ANY_ACCESS) # FILE_OBJECTID_BUFFER
FSCTL_DELETE_OBJECT_ID = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 40, METHOD_BUFFERED, FILE_SPECIAL_ACCESS)

FSCTL_GET_COMPRESSION = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 15, METHOD_BUFFERED, FILE_ANY_ACCESS)
FSCTL_SET_COMPRESSION = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 16, METHOD_BUFFERED, FILE_READ_DATA | FILE_WRITE_DATA)

FSCTL_SET_REPARSE_POINT = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 41, METHOD_BUFFERED, FILE_SPECIAL_ACCESS)
FSCTL_GET_REPARSE_POINT = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 42, METHOD_BUFFERED, FILE_ANY_ACCESS)
FSCTL_DELETE_REPARSE_POINT = CTL_CODE(FILE_DEVICE_FILE_SYSTEM, 43, METHOD_BUFFERED, FILE_SPECIAL_ACCESS)

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
		('FileRecordBuffer', BYTE * MAX_REPARSE_BUFFER),
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

