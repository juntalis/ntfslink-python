# encoding: utf-8
"""
TODO: Description

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
from ctypes import c_void_p as _voidp, sizeof as _sizeof
from ctypes.wintypes import MAX_PATH

## Constants
# Windows definitions
ANYSIZE_ARRAY = 1

NULL = 0
INVALID_HANDLE_VALUE = -1

# Access
FILE_ANY_ACCESS = 0
FILE_SPECIAL_ACCESS = FILE_ANY_ACCESS
FILE_READ_DATA = FILE_READ_ACCESS = 0x0001
FILE_WRITE_DATA = FILE_WRITE_ACCESS = 0x0002

# File open flags
FILE_FLAG_WRITE_THROUGH = 0x80000000
FILE_FLAG_OVERLAPPED = 0x40000000
FILE_FLAG_NO_BUFFERING = 0x20000000
FILE_FLAG_RANDOM_ACCESS = 0x10000000
FILE_FLAG_SEQUENTIAL_SCAN = 0x08000000
FILE_FLAG_DELETE_ON_CLOSE = 0x04000000
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
FILE_FLAG_POSIX_SEMANTICS = 0x01000000
FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
FILE_FLAG_OPEN_NO_RECALL = 0x00100000
FILE_FLAG_FIRST_PIPE_INSTANCE = 0x00080000
FILE_FLAG_REPARSE_BACKUP = FILE_FLAG_OPEN_REPARSE_POINT | FILE_FLAG_BACKUP_SEMANTICS

# The variables below deal with some of the more general stuff. (File
# IO, file access privileges, flags, basic typedefs, etc) There's a few
# flags dealing with reparse points that I left in this section for naming
# consistency.

# Generic access
GENERIC_READ = 0x80000000L
GENERIC_WRITE = 0x40000000L
GENERIC_EXECUTE = 0x20000000L
GENERIC_ALL = 0x10000000L

# File shared access
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
FILE_SHARE_DELETE = 0x00000004
FILE_SHARE_READ_WRITE = FILE_SHARE_READ | FILE_SHARE_WRITE
FILE_SHARE_ALL = FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE

# Creation flags
CREATE_NEW = 1
CREATE_ALWAYS = 2
OPEN_EXISTING = 3
OPEN_ALWAYS = 4
TRUNCATE_EXISTING = 5

## Constants used specifically by our kernel32 functions.
FILE_ATTRIBUTE_READONLY = 0x00000001
FILE_ATTRIBUTE_HIDDEN = 0x00000002
FILE_ATTRIBUTE_SYSTEM = 0x00000004
FILE_ATTRIBUTE_DIRECTORY = 0x00000010
FILE_ATTRIBUTE_NORMAL = 0x00000080
FILE_ATTRIBUTE_REPARSE_POINT = 0x00000400
FILE_ATTRIBUTE_OFFLINE = 0x00001000
FILE_ATTRIBUTE_REPARSE_DIRECTORY = (FILE_ATTRIBUTE_DIRECTORY | FILE_ATTRIBUTE_REPARSE_POINT)

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

# File command codes
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


## Constants used specifically by our advapi32 functions.
# Access Types
# The following are masks for the predefined standard access types
DELETE = 0x00010000L
READ_CONTROL = 0x00020000L
WRITE_DAC = 0x00040000L
WRITE_OWNER = 0x00080000L
SYNCHRONIZE = 0x00100000L

STANDARD_RIGHTS_REQUIRED = 0x000F0000L
STANDARD_RIGHTS_READ = READ_CONTROL
STANDARD_RIGHTS_WRITE = READ_CONTROL
STANDARD_RIGHTS_EXECUTE = READ_CONTROL

STANDARD_RIGHTS_ALL = 0x001F0000L
SPECIFIC_RIGHTS_ALL = 0x0000FFFFL

# AccessSystemAcl access type
ACCESS_SYSTEM_SECURITY = 0x01000000L

# MaximumAllowed access type
MAXIMUM_ALLOWED = 0x02000000L

# Security Tokens
TOKEN_ASSIGN_PRIMARY = 0x0001
TOKEN_DUPLICATE = 0x0002
TOKEN_IMPERSONATE = 0x0004
TOKEN_QUERY = 0x0008
TOKEN_QUERY_SOURCE = 0x0010
TOKEN_ADJUST_PRIVILEGES = 0x0020
TOKEN_ADJUST_GROUPS = 0x0040
TOKEN_ADJUST_DEFAULT = 0x0080
TOKEN_ADJUST_SESSIONID = 0x0100

TOKEN_ALL_ACCESS_P = STANDARD_RIGHTS_REQUIRED | TOKEN_ASSIGN_PRIMARY | TOKEN_DUPLICATE | TOKEN_IMPERSONATE | TOKEN_QUERY | TOKEN_QUERY_SOURCE | TOKEN_ADJUST_PRIVILEGES | TOKEN_ADJUST_GROUPS | TOKEN_ADJUST_DEFAULT
TOKEN_ALL_ACCESS = TOKEN_ALL_ACCESS_P | TOKEN_ADJUST_SESSIONID

# SE Privileges
SE_PRIVILEGE_ENABLED_BY_DEFAULT = 0x00000001L
SE_PRIVILEGE_ENABLED = 0x00000002L
SE_PRIVILEGE_REMOVED = 0X00000004L
SE_PRIVILEGE_USED_FOR_ACCESS = 0x80000000L

SE_PRIVILEGE_VALID_ATTRIBUTES = SE_PRIVILEGE_ENABLED_BY_DEFAULT | SE_PRIVILEGE_ENABLED | SE_PRIVILEGE_REMOVED | SE_PRIVILEGE_USED_FOR_ACCESS

# Privilege Set Control flags
PRIVILEGE_SET_ALL_NECESSARY = 1

# Privilege names.
SE_CREATE_TOKEN_NAME = 'SeCreateTokenPrivilege'
SE_ASSIGNPRIMARYTOKEN_NAME = 'SeAssignPrimaryTokenPrivilege'
SE_RESTORE_NAME = 'SeRestorePrivilege'
SE_BACKUP_NAME = 'SeBackupPrivilege'
SE_CREATE_SYMBOLIC_LINK_NAME = 'SeCreateSymbolicLinkPrivilege'
SE_MANAGE_VOLUME_NAME = 'SeManageVolumePrivilege'
SE_LOAD_DRIVER_NAME = 'SeLoadDriverPrivilege'
SE_UNSOLICITED_INPUT_NAME = 'SeUnsolicitedInputPrivilege'

## Macros
def CTL_CODE(DeviceType, Function, Method, Access): return (DeviceType << 16) | (Access << 14) | (Function << 2) | Method
def DEVICE_TYPE_FROM_CTL_CODE(ctrlCode): return (ctrlCode & 0xffff0000) >> 16
def METHOD_FROM_CTL_CODE(ctrlCode): return ctrlCode & 3

# File Device codes
FILE_DEVICE_CD_ROM = 0x00000002
FILE_DEVICE_CD_ROM_FILE_SYSTEM = 0x00000003
FILE_DEVICE_CONTROLLER = 0x00000004
FILE_DEVICE_DATALINK = 0x00000005
FILE_DEVICE_DFS = 0x00000006
FILE_DEVICE_DISK = 0x00000007
FILE_DEVICE_DISK_FILE_SYSTEM = 0x00000008
FILE_DEVICE_FILE_SYSTEM = 0x00000009
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
FILE_DEVICE_VIRTUAL_DISK = 0x00000024

# Methods
METHOD_BUFFERED = 0
METHOD_IN_DIRECT = 1
METHOD_OUT_DIRECT = 2
METHOD_NEITHER = 3

METHOD_DIRECT_TO_HARDWARE = METHOD_IN_DIRECT
METHOD_DIRECT_FROM_HARDWARE = METHOD_OUT_DIRECT


