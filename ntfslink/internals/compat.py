# encoding: utf-8
"""
Most of the functionality for dealing with compatibility issues between
Python versions and x86/x64 architectures can be found here. Parts of this
were borrowed from the ctypesgen module.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
import sys, ctypes

## TCHAR configuration
# TODO: Implement a check to see whether the user's filesystem supports unicode.
TCHAR_UNICODE = True

def uses_tchar(obj):
	"""
	:param obj: Object to annotate
	:type obj: object
	:return: decorator
	:rtype: object
	"""
	setattr(obj, '_tchar_', True)
	return obj

# Set the appropriate string char/string variations.
if TCHAR_UNICODE:
	TCHAR_SUFFIX = 'W'
	c_tchar = ctypes.c_wchar
	c_tchar_p = ctypes.c_wchar_p
	create_tstring_buffer = ctypes.create_unicode_buffer
	tstring_at = ctypes.wstring_at
else:
	TCHAR_SUFFIX = 'A'
	c_tchar = ctypes.c_char
	c_tchar_p = ctypes.c_char_p
	create_tstring_buffer = ctypes.create_string_buffer
	tstring_at = ctypes.string_at

## Processor Architecture Compatibility
isx64 = ctypes.sizeof(ctypes.c_void_p) == ctypes.sizeof(ctypes.c_ulonglong)

class c_void(ctypes.Structure):
	# c_void_p is a buggy return type, converting to int, so
	# POINTER(None) == c_void_p is actually written as
	# POINTER(c_void), so it can be treated as a real pointer.
	_fields_ = [('dummy', ctypes.c_int)]

def POINTER(obj):
	ptr = ctypes.POINTER(obj)
	# Convert None to a real NULL pointer to work around bugs
	# in how ctypes handles None on 64-bit platforms
	if not isinstance(ptr.from_param, classmethod):
		def from_param(cls, x):
			if x is None: return cls()
			return x
		ptr.from_param = classmethod(from_param)
	return ptr

# Shadow built-in c_void_p
c_void_p = POINTER(c_void)

#noinspection PyProtectedMember
def UNCHECKED(typ):
	if hasattr(typ, '_type_') and \
	  isinstance(typ._type_, basestring) and \
	  typ._type_ != 'P':
		return typ
	else:
		return c_void_p

# Pointer types
if isx64:
	SHalfPtrType = ctypes.c_int32
	UHalfPtrType = ctypes.c_uint32
	SPtrType = ctypes.c_int64
	UPtrType  = ctypes.c_uint64
else:
	SHalfPtrType = ctypes.c_int16
	UHalfPtrType = ctypes.c_uint16
	SPtrType = ctypes.c_int32
	UPtrType = ctypes.c_uint32

## Python Version Compatibility
binary = bytes if sys.version_info >= (2, 6) else buffer

# While I'm not currently trying to support python 3, I figured
# I might as well start putting the compatibility stubs in place.
if sys.version_info[0] < 3: #major
	def tobyte(s): return s
	def frombyte(s): return s
else:
	def tobyte(s):
		return s \
			if type(s) is bytes else \
			s.encode('utf-8')
	def frombyte(s):
		return s \
			if type(s) is not bytes else \
		s.decode('utf-8')

__all__ = ['c_void', 'c_void_p', 'POINTER', 'UNCHECKED', 'SHalfPtrType', 'SPtrType', 'UHalfPtrType', 'UPtrType',
		   'binary', 'frombyte', 'tobyte', 'isx64', 'TCHAR_SUFFIX', 'c_tchar', 'c_tchar_p',
		   'uses_tchar', 'create_tstring_buffer', 'tstring_at' ]
