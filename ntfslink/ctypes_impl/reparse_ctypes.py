# encoding: utf-8
"""
CTypes implementation of the reparse point structures etc.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
import ctypes
from ctypes.wintypes import WCHAR


from .reparse_common import *
from .._compat import buffer_type, unicode_type, str_types
from ._win_api import DWORD, WORD, BYTE, UCHAR

#############
# Constants #
#############

## Header Size Constants
WCHAR_SIZE = ctypes.sizeof(ctypes.c_wchar)
REPARSE_POINT_HEADER_SIZE = SIZEOF(DWORD) + (2 * SIZEOF(WORD))
REPARSE_GUID_DATA_BUFFER_HEADER_SIZE = REPARSE_POINT_HEADER_SIZE + (SIZEOF(DWORD) * 4)

## Buffer Size Constants
MAX_GENERIC_REPARSE_BUFFER = MAX_REPARSE_BUFFER - REPARSE_GUID_DATA_BUFFER_HEADER_SIZE
MAX_MOUNTPOINT_REPARSE_BUFFER = MAX_GENERIC_REPARSE_BUFFER - SIZEOF(WORD) * 4
MAX_SYMLINK_REPARSE_BUFFER = MAX_MOUNTPOINT_REPARSE_BUFFER - SIZEOF(DWORD)


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

##############
# Structures #
##############

class GUID(ctypes.Structure):
	""" Borrowed small parts of this from the comtypes module. """
	_fields_ = [
		('Data1', QWORD),
		('Data2', QWORD),
	]
	
	#: Represents an empty (zero-ed out) :class:`GUID` instance.
	NULL = None
	
	def __nonzero__(self):
		"""
		Non-zero test
		:return: ``True`` if ``self`` does not match ``GUID.NULL``.
		:rtype: bool
		"""
		return self != GUID.NULL
	
	def __eq__(self, other):
		"""
		Equality operator
		:param other: object to compare against
		:type other: GUID | object
		:return: Whether the two GUIDs are equal
		:rtype: bool
		"""
		return isinstance(other, GUID) and \
		       buffer_type(self) == buffer_type(other)
	
	def __hash__(self):
		"""
		hash operator
		:return:Unique hash
		:rtype: int
		"""
		return hash(buffer_type(self))
	
	def __copy__(self):
		"""
		Copy magic method
		:return: Newly created GUID struct populated with the same values.
		:rtype: GUID
		"""
		return self.copy()
	
	def copy(self):
		"""
		Creates a new GUID struct with the same data.
		:return: Newly created GUID struct populated with the same values.
		:rtype: GUID
		"""
		return GUID(
			Data1=self.Data1,
			Data2=self.Data2
		)
	
	def copyfrom(self, other):
		"""
		Copies another GUID into this one.
		:param other: Other GUID
		:type other: GUID
		:return: self
		:rtype: GUID
		"""
		self.Data1 = other.Data1
		self.Data2 = other.Data2
		return self

GUID.NULL = GUID()

class ReparsePointHeader(ctypes.Structure):
	""" Reparse Point Header for MS reparse points (symlinks, junctions,
	    mountpoints) """
	_fields_ = [
		('tag', DWORD),     # ReparseTag
		('length', WORD),   # ReparseDataLength
		('reserved', WORD), # Reserved
	]

class ReparsePointGUIDHeader(ReparsePointHeader):
	""" Reparse Point Header for third party reparse points (I don't know
	    of any) """
	_fields_ = [
		('guid', GUID), # ReparseGuid
	]

class MSReparsePointBuffer(ctypes.Structure):
	"""
	Base class for MS reparse points that provides easy
	access to the substitute_name and PrintNAme fields.
	"""
	_fields_ = [
		('substitute_name_offset', WORD), # SubstituteNameOffset
		('substitute_name_size', WORD),   # SubstituteNameSize
		('print_name_offset', WORD),      # PrintNameOffset
		('print_name_size', WORD),        # PrintNameSize
	]
	
	def wstring_at(self, offset, length):
		"""
		:param offset: String offset (in bytes)
		:param length: String size (in wchars)
		:return:
		:rtype: str
		"""
		cls = type(self)
		path_buffer_addr = ctypes.addressof(self) + cls.path_buffer.offset
		wstring_addr = path_buffer_addr + offset
		return ctypes.wstring_at(wstring_addr, length)
	
	@property
	def substitute_name(self):
		"""
		:return: substitute_name
		:rtype: str
		"""
		offset = self.substitute_name_offset
		length = self.substitute_name_size // WCHAR_SIZE
		return self.wstring_at(offset, length)
	
	@property
	def print_name(self):
		"""
		:return: substitute_name
		:rtype: str
		"""
		offset = self.print_name_offset
		length = self.print_name_size // WCHAR_SIZE
		return self.wstring_at(offset, length)

class SymbolicLinkBuffer(MSReparsePointBuffer):
	""" Symbolic link Reparse Point Buffer """
	_fields_ = [
		('flags', DWORD),
		('path_buffer', WCHAR * MAX_SYMLINK_REPARSE_BUFFER)
	]

class MountPointBuffer(MSReparsePointBuffer):
	""" Mount Point/Junction Reparse Point Buffer """
	_fields_ = [
		('path_buffer', WCHAR * MAX_MOUNTPOINT_REPARSE_BUFFER)
	]

class GenericReparseBuffer(ctypes.Structure):
	""" Generic Reparse Point Buffer """
	_fields_ = [('path_buffer', UCHAR * MAX_GENERIC_REPARSE_BUFFER)]

class ReparsePointBuffer(ctypes.Union):
	""" Union containing all supported reparse point buffer types. """
	_fields_ = [
		('symbolic_link', SymbolicLinkBuffer),
		('mount_point', MountPointBuffer),
		('generic', GenericReparseBuffer)
	]

def _get_reparse_point_buffer(self):
	""" Logic for :attr:`ReparsePointGUIDData.Buffer` &
	    :attr:`ReparsePointData.Buffer` properties. """
	if self.tag == IO_REPARSE_TAG_MOUNT_POINT:
		return self._buffer.mount_point
	elif self.tag == IO_REPARSE_TAG_SYMLINK:
		return self._buffer.symbolic_link
	else:
		return self._buffer.generic

class ReparsePointData(ReparsePointHeader):
	""" Combines the reparse point buffer union with the header struct. """
	_fields_ = [
		('_buffer', ReparsePointBuffer)
	]
	
	@property
	def buffer(self):
		"""
		Accesses the reparse point buffer based on the value of
		:attr:`ReparsePointGUIDHeader.tag`
		:return: Buffer instance
		:rtype: SymbolicLinkBuffer | MountPointBuffer | GenericReparseBuffer
		"""
		# noinspection PyTypeChecker
		return _get_reparse_point_buffer(self)

class ReparsePointGUIDData(ReparsePointGUIDHeader):
	""" Combines the reparse point buffer union with the header struct. """
	_fields_ = [
		('_Buffer', ReparsePointBuffer)
	]
	
	@property
	def Buffer(self):
		"""
		Accesses the reparse point buffer based on the value of
		:attr:`ReparsePointGUIDHeader.tag`
		:return: Buffer instance
		:rtype: SymbolicLinkBuffer | MountPointBuffer | GenericReparseBuffer
		"""
		# noinspection PyTypeChecker
		return _get_reparse_point_buffer(self)

##################
# Implementation #
##################

def create_ms_reparse_point(tag, data=None, guid=False):
	"""
	Creates a ctypes buffer containing

	:param tag: Reparse tag
	:type tag: int
	:param data: Filepath or raw buffer
	:type data: str | None
	:param guid: Whether or not to use the GUID-based header
	:type guid: bool | tuple[int,...] | tuple[long,...]
	:return: Buffer size, ctypes buffer
	:rtype: int, ctypes.c_void_p
	:raises NotImplementedError: if the specified tag is unrecognized/unsupported.
	"""
	# Handle guid param
	struct_type = ReparsePointData
	if guid:
		struct_type = ReparsePointGUIDData
		if isinstance(guid, bool):
			guid = GUID(0,0)
		elif isinstance(guid, tuple):
			guid = GUID(*guid)
	
	struct_size = ctypes.sizeof(struct_type)
	struct_data = struct_type(tag, struct_size, 0)
	struct_buffer = struct_data.buffer
	
	# Process GUID
	if guid:
		struct_data.guid.copyfrom(guid)
	
	# Process data
	if data is not None:
		# Extract path names and calculate sizes
		flags, subst_name, print_name = extract_buffer_attrs(tag, data)
		subst_size, print_size = wsize(subst_name), wsize(print_name)
		
		# Process tag-specific functionality.
		if tag == IO_REPARSE_TAG_SYMLINK:
			struct_buffer.flags = flags
			path_buffer_format = '{0}{1}'
			print_offset = subst_size
		elif tag == IO_REPARSE_TAG_MOUNT_POINT:
			path_buffer_format = '{0}\0{1}'
			print_offset = subst_size + WCHAR_SIZE
		else:
			raise NotImplementedError('Unknown MS tag specified: 0x{:08X}'.format(tag))

		# Fill in our buffer
		struct_buffer.substitute_name_offset = 0
		struct_buffer.substitute_name_size = subst_size
		struct_buffer.print_name_offset = print_offset
		struct_buffer.print_name_size = print_size
		struct_buffer.path_buffer = unicode_type(
			path_buffer_format.format(subst_name, print_name)
		)
	
	return struct_size, struct_data
