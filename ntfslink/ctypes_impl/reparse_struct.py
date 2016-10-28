# encoding: utf-8
"""
Using the :mod:`struct` module, parse the following structures:

	typedef struct {
		DWORD ReparseTag;
		WORD ReparseDataLength;
		WORD Reserved;
		-- ReparsePointBuffer --
	} REPARSE_DATA_BUFFER, *PREPARSE_DATA_BUFFER;
	
	typedef struct {
		DWORD ReparseTag;
		WORD  ReparseDataLength;
		WORD  Reserved;
		GUID  ReparseGuid;
		-- ReparsePointBuffer ---
	} REPARSE_GUID_DATA_BUFFER, *PREPARSE_GUID_DATA_BUFFER;

	struct {
		WORD SubstituteNameOffset;
		WORD SubstituteNameLength;
		WORD PrintNameOffset;
		WORD PrintNameLength;
		WCHAR PathBuffer[ANYSIZE_ARRAY];
	} MountPointReparseBuffer;

	struct {
		WORD SubstituteNameOffset;
		WORD SubstituteNameLength;
		WORD PrintNameOffset;
		WORD PrintNameLength;
		DWORD Flags;
		WCHAR PathBuffer[ANYSIZE_ARRAY];
	} SymbolicLinkReparseBuffer;
	
	struct {
		BYTE DataBuffer[ANYSIZE_ARRAY];
	} GenericReparseBuffer;

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
import struct

from .reparse_common import *
from .._compat import bytes_type

##################
# Ctypes-Related #
##################

class


######################
# Struct Definitions #
######################

#: GUID structure format string
GUID_format = 'IHH8B' # 2Q

#: ReparsePointHeader format string
ReparsePointHeader_format = 'IHH' # 'IH2x'

#: MountPointBuffer format string
MountPointBuffer_format = 'HHHH'

#: Reparse point header structure definition for MS reparse points
ReparsePointHeader = struct.Struct(ReparsePointHeader_format)

#: Reparse point header structure definition for third-party reparse points
ReparsePointGUIDHeader = struct.Struct(
	ReparsePointHeader_format + GUID_format
)

#: Buffer structure definition for mount points & junctions (not including path
#: buffer)
MountPointBuffer = struct.Struct(MountPointBuffer_format)

#: Buffer structure definition for symbolic links (not including path buffer)
SymbolicLinkBuffer = struct.Struct(
	MountPointBuffer_format + 'I'
)

#############
# Constants #
#############

## wchar_t size
WCHAR_SIZE = struct.calcsize('H')

## Header Size Constants
REPARSE_POINT_HEADER_SIZE = ReparsePointHeader.size
REPARSE_POINT_GUID_HEADER_SIZE = ReparsePointGUIDHeader.size

## Buffer Size Constants (without header sizes factored in)
MAX_MOUNTPOINT_REPARSE_BUFFER = MAX_REPARSE_BUFFER - MountPointBuffer.size
MAX_SYMLINK_REPARSE_BUFFER = MAX_REPARSE_BUFFER - SymbolicLinkBuffer.size

def alloc_empty_reparse_point():
	"""
	Creates an empty ctypes buffer
	:return: Buffer size, ctypes buffer
	:rtype: int, array[ctypes.c_char]
	"""

def alloc_reparse_point_inner(tag, header, header_size, buffer, buffer_size, *hfields):
	"""
	Handles the common functionality between :func:`create_ms_reparse_point` and
	:func:`create_custom_reparse_point`.
	:param tag: Reparse point tag
	:type tag: int
	:param header: Header structure to use
	:type header: struct.Struct
	:param header_size: Size of header struct (avoid repeated lookup)
	:type header_size: int
	:param buffer: The data buffer's raw bytes.
	:type buffer: bytes | str
	:param buffer_size: Size of buffer (avoid recalculation)
	:type buffer_size: int
	:param hfields: Additional header fields. (Currently only GUID for custom reparse points)
	:type hfields:
	:return: Buffer size, ctypes buffer
	:rtype: int, array[ctypes.c_char]
	"""
	header_bytes = header.pack(tag, buffer_size, 0, *hfields)
	struct_size = header_size + buffer_size
	return struct_size, ctypes.create_string_buffer(header_bytes + buffer, struct_size)

def create_ms_reparse_point(tag, data=None):
	"""
	Creates a ctypes buffer containiing
	
	:param tag: Reparse tag
	:type tag: int
	:param data: Filepath or raw buffer
	:type data: str | None
	:return: Buffer size, ctypes buffer
	:rtype: int, array[ctypes.c_char]
	:raises NotImplementedError: if the specified tag is unrecognized.
	"""
	# Shorten up references to header stuff.
	header, header_size = ReparsePointHeader, REPARSE_POINT_HEADER_SIZE
	
	# Assemble buffer
	buffer, extra_attrs = None, tuple()
	buffer_size, buffer_struct = 0, None
	if data is None:
		buffer_size = MAX_REPARSE_BUFFER - header_size
		buffer = bytes_type()
	else:
		if tag == IO_REPARSE_TAG_MOUNT_POINT:
			buffer_struct = MountPointBuffer
			buffer_size = buffer_struct.size
		elif tag == IO_REPARSE_TAG_SYMLINK:
			buffer_struct = SymbolicLinkBuffer
			buffer_size = buffer_struct.size
			extra_attrs = (0 if os.path.isabs(data) \
				             else SYMBOLIC_LINK_FLAG_RELATIVE,)
		elif not is_ms_tag(tag):
			raise NotImplementedError('Unknown tag specified: 0x%08X' % tag)
		
		if buffer_struct is None:
			path_length = len(data)
			path_size = path_length * WCHAR_SIZE
			buffer_attrs = buffer_struct.pack(0, path_size, path_size + WCHAR_SIZE + path_size, *extra_attrs)
			buffer = buffer_attrs + cstr2wstr(data) + cstr2wstr('\0') + cstr2wstr(data)
			buffer_size += len(buffer)
	
	return create_reparse_point_inner(tag, header, header_size, buffer, buffer_size)
