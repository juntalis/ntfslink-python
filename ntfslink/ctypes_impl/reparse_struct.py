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
import functools
from collections import namedtuple

from .reparse_common import *
from .._util import delegate_property
from .._compat import encode_bytes, decode_bytes, long_type, empty_tuple, str_types

########################
# Parse Result Objects #
########################

header_fields = ['tag', 'length', 'reserved']

ReparsePointHeader = namedtuple('ReparsePointHeader', header_fields)
_ReparsePointGUIDHeader = namedtuple('ReparsePointGUIDHeader', header_fields + ['guid'])

@functools.wraps(_ReparsePointGUIDHeader)
def ReparsePointGUIDHeader(tag, length, reserved, *guid):
	return _ReparsePointGUIDHeader(tag, length, reserved, guid)

buffer_fields = ['substitute_name_offset', 'substitute_name_size', 'print_name_offset',
                 'print_name_size' ]

MountPointBuffer = namedtuple('MountPointBuffer', buffer_fields)
SymbolicLinkBuffer = namedtuple('SymbolicLinkBuffer', buffer_fields + ['flags'])

PathBuffer = namedtuple('PathBuffer', ['substitute_name', 'print_name'])

class ReparsePoint(object):
	"""
	Represents the data parsed from a reparse point structure. Zero validation
	is performed on the constructor parameters, so you should probably avoid constructing
	it in your own code.
	"""
	
	__slots__ = ('header', 'buffer', 'path',)
	
	def __init__(self, header, buffer, path):
		"""
		Constructor
		:param header: Parsed header object
		:type header: ReparsePointGUIDHeader | ReparsePointHeader
		:param buffer: Parsed buffer object
		:type buffer: MountPointBuffer | SymbolicLinkBuffer
		:param path: Parsed path buffer
		:type path: PathBuffer
		"""
		self.header = header
		self.buffer = buffer
		self.path = path
	
	# Provide property accessors to all the potential header fields.
	tag = delegate_property('header', 'tag')
	length = delegate_property('header', 'length')
	reserved = delegate_property('header', 'reserved')
	guid = delegate_property('header', 'guid')
	
	# Provide property accessors to all the potential buffer fields.
	flags = delegate_property('buffer','flags')
	print_name_size = delegate_property('buffer','print_name_size')
	print_name_offset = delegate_property('buffer','print_name_offset')
	substitute_name_size = delegate_property('buffer','substitute_name_size')
	substitute_name_offset = delegate_property('buffer','substitute_name_offset')
	
	# Provide property accessors to all the potential path fields.
	print_name = delegate_property('path','print_name')
	substitute_name = delegate_property('path','substitute_name')


######################
# Struct Definitions #
######################

#: GUID structure format string
GUID_format = '2Q' # 2Q

#: ReparsePointHeader format string
ReparsePointHeader_format = 'IHH' # 'IH2x'

#: MountPointBuffer format string
MountPointBuffer_format = 'HHHH'

#: SymbolicLinkBuffer format string
SymbolicLinkBuffer_format = MountPointBuffer_format + 'I'

#: Reparse point header structure definition for MS reparse points
ReparsePointHeader_struct = struct.Struct(ReparsePointHeader_format)

#: Reparse point header structure definition for third-party reparse points
ReparsePointGUIDHeader_struct = struct.Struct(
	ReparsePointHeader_format + GUID_format
)

#: Buffer structure definition for mount points & junctions (not including path
#: buffer)
MountPointBuffer_struct = struct.Struct(MountPointBuffer_format)

#: Buffer structure definition for symbolic links (not including path buffer)
SymbolicLinkBuffer_struct = struct.Struct(SymbolicLinkBuffer_format)

#############
# Constants #
#############

## wchar_t size
WCHAR_SIZE = struct.calcsize('H')

## Header Size Constants
REPARSE_POINT_HEADER_SIZE = ReparsePointHeader_struct.size
REPARSE_POINT_GUID_HEADER_SIZE = ReparsePointGUIDHeader_struct.size

## Buffer Size Constants (without header sizes factored in)
MAX_MOUNTPOINT_REPARSE_BUFFER = MAX_REPARSE_BUFFER - MountPointBuffer_struct.size
MAX_SYMLINK_REPARSE_BUFFER = MAX_REPARSE_BUFFER - SymbolicLinkBuffer_struct.size

def wsize(data):
	"""

	:param data:
	:type data: str | int
	:return:
	:rtype: int
	"""
	if isinstance(data, str_types):
		data = len(data)
	return data * WCHAR_SIZE

##################
# Implementation #
##################

_struct_mapping = dict()
_struct_mapping[ReparsePointHeader_struct] = ReparsePointHeader
_struct_mapping[ReparsePointGUIDHeader_struct] = ReparsePointGUIDHeader
_struct_mapping[MountPointBuffer_struct] = MountPointBuffer
_struct_mapping[SymbolicLinkBuffer_struct] = SymbolicLinkBuffer
_struct_mapping[ReparsePointHeader] = ReparsePointHeader_struct
_struct_mapping[ReparsePointGUIDHeader] = ReparsePointGUIDHeader_struct
_struct_mapping[MountPointBuffer] = MountPointBuffer_struct
_struct_mapping[SymbolicLinkBuffer] = SymbolicLinkBuffer_struct

def _parse_reparse_point(data, header_type):
	"""
	TODO: Documentation
	:param data:
	:type data:
	:param header_type:
	:type header_type:
	:return:
	:rtype:
	"""
	# Resolve header struct and type
	match = _struct_mapping.get(header_type)
	if isinstance(header_type, struct.Struct):
		header_struct, header_type = header_type, match
	else:
		header_struct, header_type = match, header_type
	
	# Parse header
	header_data = header_struct.unpack_from(data)
	header_obj = header_type(*header_data)
	
	# Resolve buffer struct and type
	if header_obj.tag == IO_REPARSE_TAG_SYMLINK:
		buffer_struct = SymbolicLinkBuffer_struct
	elif header_obj.tag == IO_REPARSE_TAG_MOUNT_POINT:
		buffer_struct = MountPointBuffer_struct
	else:
		raise NotImplementedError('Custom reparse points are not currently supported!')
	
	# Parse buffer
	buffer_offset = header_struct.size
	buffer_type = _struct_mapping[buffer_struct]
	buffer_data = buffer_struct.unpack_from(data, offset=buffer_offset)
	buffer_obj = buffer_type(*buffer_data)
	
	# Parse PathBuffer
	path_offset = buffer_offset + buffer_struct.size
	if hasattr(data, 'raw'):
		data = encode_bytes(data.raw)
	path_data = data[path_offset:]
	print_ofs, print_size = buffer_obj.print_name_offset, buffer_obj.print_name_size
	subst_ofs, subst_size = buffer_obj.substitute_name_offset, buffer_obj.substitute_name_size
	subst_name = wstr2cstr(path_data[subst_ofs:subst_ofs + subst_size])
	print_name = wstr2cstr(path_data[print_ofs:print_ofs + print_size])
	path_obj = PathBuffer(subst_name, print_name)
	
	return ReparsePoint(header_obj, buffer_obj, path_obj)

def parse_reparse_point(data):
	"""
	Given the raw bytes of a reparse point structure without a GUID-based header, parse out
	all the struct details.
	:param data: Raw bytes for the reparse point structure
	:type data: bytes | ctypes.c_char_p
	:return: Parsed reparse point
	:rtype: ReparsePoint
	"""
	return _parse_reparse_point(data, ReparsePointHeader)

def parse_guid_reparse_point(data):
	"""
	Given the raw bytes of a reparse point structure with a GUID-based header, parse out
	all the struct details.
	:param data: Raw bytes for the reparse point structure
	:type data: bytes | ctypes.c_char_p
	:return: Parsed reparse point
	:rtype: ReparsePoint
	"""
	return _parse_reparse_point(data, ReparsePointGUIDHeader)

def alloc_empty_reparse_point(tag, header_struct, *hfields):
	"""
	Creates an empty ctypes buffer
	:return: Struct data size, ctypes buffer
	:rtype: int, array[ctypes.c_char]
	"""
	if tag is None: tag = 0
	data_length = MAX_REPARSE_BUFFER - header_struct.size
	buffer = header_struct.pack(tag, data_length, 0, *hfields)
	return MAX_REPARSE_BUFFER, ctypes.create_string_buffer(buffer, MAX_REPARSE_BUFFER)

def alloc_reparse_point(tag, header_struct, buffer_bytes, *hfields):
	"""
	Handles the common functionality between :func:`create_ms_reparse_point` and
	:func:`create_custom_reparse_point`.
	:param tag: Reparse point tag
	:type tag: int
	:param header_struct: Header structure to use
	:type header_struct: struct.Struct
	:param buffer_bytes: The data buffer's raw bytes.
	:type buffer_bytes: bytes | str
	:param hfields: Additional header fields. (Currently only GUID for custom reparse points)
	:type hfields:
	:return: Struct data size, ctypes buffer
	:rtype: int, array[ctypes.c_char]
	"""
	data_length = len(buffer_bytes)
	struct_size = header_struct.size + data_length
	header_bytes = header_struct.pack(tag, data_length, 0, *hfields)
	return struct_size, ctypes.create_string_buffer(header_bytes + buffer_bytes, struct_size)

def create_ms_reparse_point(tag, path=None, guid=False):
	"""
	Creates a ctypes buffer containing 
	
	:param tag: Reparse tag
	:type tag: int
	:param path: Filepath or raw buffer
	:type path: str | None
	:param guid: Whether or not to use the GUID-based header
	:type guid: bool | tuple[int,int] | tuple[long,long]
	:return: Buffer size, ctypes buffer
	:rtype: int, ctypes.c_void_p
	:raises NotImplementedError: if the specified tag is unrecognized.
	"""
	# Shorten up references to header stuff.
	header_struct = ReparsePointHeader_struct
	if guid:
		header_struct = ReparsePointGUIDHeader_struct
		if isinstance(guid, bool):
			guid = (long_type(0), long_type(0),)
	
	# Allocate and fill our buffer
	if path is None:
		extra_attrs = guid if guid else empty_tuple
		struct_size, struct_data = alloc_empty_reparse_point(tag, header_struct, *extra_attrs)
	else:
		
		# Forward declare our buffer variables
		buffer_bytes, extra_attrs = None, empty_tuple
		
		# Extract path names and calculate sizes
		flags, subst_name, print_name = extract_buffer_attrs(tag, path)
		subst_size, print_size = wsize(subst_name), wsize(print_name)
		
		if tag == IO_REPARSE_TAG_MOUNT_POINT:
			buffer_struct = MountPointBuffer_struct
			print_offset = subst_size + WCHAR_SIZE
			path_buffer_format = '{0}\0{1}'
		elif tag == IO_REPARSE_TAG_SYMLINK:
			buffer_struct = SymbolicLinkBuffer_struct
			extra_attrs = (flags,)
			print_offset = subst_size
			path_buffer_format = '{0}{1}'
		else:
			raise NotImplementedError('Unknown MS tag specified: 0x{:08X}'.format(tag))
		
		# Build actual path buffer
		buffer_attrs = buffer_struct.pack(0, subst_size, print_offset, print_size,*extra_attrs)
		buffer_bytes = buffer_attrs + cstr2wstr(
			path_buffer_format.format(subst_name, print_name)
		)
		
		extra_attrs = guid if guid else empty_tuple
		struct_size, struct_data = alloc_reparse_point(tag, header_struct, buffer_bytes, *extra_attrs)
	
	return struct_size, struct_data

def create_custom_reparse_point(tag, data=None, guid=False):
	raise NotImplementedError('Not currently implemented')

