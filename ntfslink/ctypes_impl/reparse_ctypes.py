# encoding: utf-8
"""
TODO: Description

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
import ctypes
from ctypes.wintypes import WCHAR


from .reparse_common import *
from .._compat import buffer_type
from ._winapi import DWORD, WORD, BYTE

#############
# Constants #
#############

## Header Size Constants
REPARSE_POINT_HEADER_SIZE = SIZEOF(DWORD) + (2 * SIZEOF(WORD))
REPARSE_GUID_DATA_BUFFER_HEADER_SIZE = REPARSE_POINT_HEADER_SIZE + (SIZEOF(DWORD) * 4)

## Buffer Size Constants
MAX_GENERIC_REPARSE_BUFFER = MAX_REPARSE_BUFFER - REPARSE_GUID_DATA_BUFFER_HEADER_SIZE
MAX_MOUNTPOINT_REPARSE_BUFFER = MAX_GENERIC_REPARSE_BUFFER - SIZEOF(WORD) * 4
MAX_SYMLINK_REPARSE_BUFFER = MAX_MOUNTPOINT_REPARSE_BUFFER - SIZEOF(DWORD)

################
# Type Aliases #
################

UCHAR = ctypes.c_ubyte

##############
# Structures #
##############

class GUID(ctypes.Structure):
	""" Borrowed small parts of this from the comtypes module. """
	_fields_ = [
		('Data1', DWORD),
		('Data2', WORD),
		('Data3', WORD),
		('Data4', (BYTE * 8)),
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
	
	def copy(self, other):
		"""
		:param other:
		:type other:
		:return:
		:rtype:
		"""
		return GUID(
			Data1=self.Data1,
			Data2=self.Data2,
			Data3=self.Data3,
			Data4=self.Data4
		)

GUID.NULL = GUID()

class ReparsePointHeader(ctypes.Structure):
	""" Reparse Point Header for MS reparse points (symlinks, junctions,
	    mountpoints) """
	_fields_ = [
		('ReparseTag', DWORD),
		('ReparseDataLength', WORD),
		('Reserved', WORD),
	]

class ReparsePointGUIDHeader(ctypes.Structure):
	""" Reparse Point Header for third party reparse points (I don't know
	    of any) """
	_fields_ = [
		('ReparseTag', DWORD),
		('ReparseDataLength', WORD),
		('Reserved', WORD),
		('ReparseGuid', GUID),
	]

class SymbolicLinkBuffer(ctypes.Structure):
	""" Symbolic link Reparse Point Buffer """
	_fields_ = [
		('SubstituteNameOffset', WORD),
		('SubstituteNameLength', WORD),
		('PrintNameOffset', WORD),
		('PrintNameLength', WORD),
		('Flags', DWORD),
		('PathBuffer', WCHAR * MAX_SYMLINK_REPARSE_BUFFER)
	]

class MountPointBuffer(ctypes.Structure):
	""" Mount Point/Junction Reparse Point Buffer """
	_fields_ = [
		('SubstituteNameOffset', WORD),
		('SubstituteNameLength', WORD),
		('PrintNameOffset', WORD),
		('PrintNameLength', WORD),
		('PathBuffer', WCHAR * MAX_SYMLINK_REPARSE_BUFFER)
	]

class GenericReparseBuffer(ctypes.Structure):
	""" Generic Reparse Point Buffer """
	_fields_ = [('PathBuffer', UCHAR * MAX_GENERIC_REPARSE_BUFFER)]

class ReparsePointBuffer(ctypes.Union):
	""" Union containing all supported reparse point buffer types. """
	_fields_ = [
		('SymbolicLink', SymbolicLinkBuffer),
		('MountPoint', MountPointBuffer),
		('Generic', GenericReparseBuffer)
	]

def _get_reparse_point_buffer(self):
	""" Logic for :attr:`ReparsePointGUIDData.Buffer` &
	    :attr:`ReparsePointData.Buffer` properties. """
	if self.ReparseTag == IO_REPARSE_TAG_MOUNT_POINT:
		return self._Buffer.MountPoint
	elif self.ReparseTag == IO_REPARSE_TAG_SYMLINK:
		return self._Buffer.SymbolicLink
	else:
		return self._Buffer

class ReparsePointData(ReparsePointHeader):
	""" Combines the reparse point buffer union with the header struct. """
	_fields_ = [
		('_Buffer', ReparsePointBuffer)
	]
	
	@property
	def Buffer(self):
		"""
		Accesses the reparse point buffer based on the value of
		:attr:`ReparsePointGUIDHeader.ReparseTag`
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
		:attr:`ReparsePointGUIDHeader.ReparseTag`
		:return: Buffer instance
		:rtype: SymbolicLinkBuffer | MountPointBuffer | GenericReparseBuffer
		"""
		# noinspection PyTypeChecker
		return _get_reparse_point_buffer(self)
