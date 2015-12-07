# encoding: utf-8
"""
Commonly used Windows datatypes. Additionally, we'll also be shadowing types
already implemented in the standard ctypes module.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
import ctypes, ctypes.wintypes
from _ctypes import _SimpleCData
from .cutil import Out as _out
from .compat import *

# Numerical types representing pointers
HALF_PTR  = SHalfPtrType
UHALF_PTR = UHalfPtrType
LONG_PTR  = SPtrType
ULONG_PTR = UPtrType

SBYTE      = ctypes.c_byte  # for lack of a better name
BYTE       = ctypes.c_ubyte # this is to remain true to the Windows declaration.
SHORT      = ctypes.c_int16
USHORT     = ctypes.c_uint16
INT        = ctypes.c_int32
UINT       = ctypes.c_uint32
LONG       = ctypes.c_int32
ULONG      = ctypes.c_uint32 # Should be the same as INT
LONGLONG   = ctypes.c_int64
ULONGLONG  = ctypes.c_uint64
BOOLEAN    = ctypes.c_bool

CHAR       = ctypes.c_char
WCHAR      = ctypes.c_wchar
UCHAR      = BYTE

SIZE_T     = ULONG_PTR
SSIZE_T    = LONG_PTR
WORD       = USHORT
DWORD      = ULONG
QWORD      = ULONGLONG

#noinspection PyMethodMayBeStatic
class BOOL(INT):
	def from_param(self, value):
		if value is None:
			return INT(0)
		elif isinstance(value, _SimpleCData):
			return value
		else:
			return INT(value)

	def __eq__(self, other):
		value = self.value
		if isinstance(other, bool):
			return value == other
		elif isinstance(other, _SimpleCData):
			return value == bool(other.value)
		else:
			return value == bool(other)

	def __hash__(self):
		return hash(self._as_parameter_)

#noinspection PyMethodMayBeStatic
# class HANDLE(ULONG_PTR):
	# INVALID_VALUE = ULONG_PTR(-1)
	# def from_param(self, value):
		# if value is None:
			# return ULONG_PTR(0)
		# elif isinstance(value, _SimpleCData):
			# return value
		# else:
			# return ULONG_PTR(value)

	# def __nonzero__(self):
		# return super(HANDLE, self).__nonzero__() and \
			# self.value != HANDLE.INVALID_VALUE

#raise 

class HANDLE(ULONG_PTR):
	"""
	Wrapper around the numerical representation of a pointer to
	add checks for INVALID_HANDLE_VALUE
	"""
	NULL = None
	INVALID = None

	def __init__(self, value=None):
		if value is None: value = 0
		super(HANDLE, self).__init__(value)
		self.autoclose = False

	@classmethod
	def from_param(cls, value):
		if value is None:
			return HANDLE.NULL
		elif isinstance(value, ctypes._SimpleCData):
			return value
		else:
			return HANDLE(value)
	
	def close(self):
		if bool(self):
			try:
				from .prototypes import CloseHandle
				CloseHandle(self)
			except: pass
	
	def __enter__(self):
		if not bool(self):
			raise WinError
		self.autoclose = True
		return self
	
	def __exit__(self, exc_typ, exc_val, trace):
		self.close()
		return False
	
	def __del__(self):
		if hasattr(self, 'autoclose') and self.autoclose:
			self.close()
	
	def __nonzero__(self):
		return super(HANDLE, self).__nonzero__() and \
			self.value != HANDLE.INVALID.value
	
	@staticmethod
	def open(filepath, flags='r', backup = False):
		from . import helpers as _helpers
		handler = 'OpenFileRW' if 'w' in flags else 'OpenFileR'
		result = getattr(_helpers, handler)(filepath, backup)
		return HANDLE(result)

HANDLE.NULL    = HANDLE(0)
HANDLE.INVALID = HANDLE(-1)

@uses_tchar
class TCHAR(c_tchar): pass
@uses_tchar
class PTSTR(c_tchar_p): pass

# Sticking with the P prefix for all pointer types
PSBYTE      = POINTER(SBYTE)
PBYTE       = POINTER(BYTE)
PSHORT      = POINTER(SHORT)
PUSHORT     = POINTER(USHORT)
PINT        = POINTER(INT)
PUINT       = POINTER(UINT)
PLONG       = POINTER(LONG)
PULONG      = POINTER(ULONG)
PLONGLONG   = POINTER(LONGLONG)
PULONGLONG  = POINTER(ULONGLONG)
PBOOLEAN    = POINTER(BOOLEAN)

PSTR        = ctypes.c_char_p
PWSTR       = ctypes.c_wchar_p
PUSTR       = PBYTE

PSIZE_T     = POINTER(SIZE_T)
PSSIZE_T    = POINTER(SSIZE_T)
PWORD       = PUSHORT
PDWORD      = PULONG
PQWORD      = PULONGLONG

PVOID       = c_void_p
PBOOL       = POINTER(BOOL)
PHANDLE     = POINTER(HANDLE)

# Although there is no difference between the P<TYPE> and LP<TYPE> types in Win32 C code,
# we'll be doing things a little difference. For convenience purposes, LP<TYPE> will be
# used as a shortcut to the corresponding P<TYPE>, with an OUT annotation.
LPSBYTE     = _out(PSBYTE)
LPBYTE      = _out(PBYTE)
LPSHORT     = _out(PSHORT)
LPUSHORT    = _out(PUSHORT)
LPINT       = _out(PINT)
LPUINT      = _out(PUINT)
LPLONG      = _out(PLONG)
LPULONG     = _out(PULONG)
LPLONGLONG  = _out(PLONGLONG)
LPULONGLONG = _out(PULONGLONG)
LPBOOLEAN   = _out(PBOOLEAN)

LPSTR       = _out(PSTR)
LPWSTR      = _out(PWSTR)
LPUSTR      = _out(PUSTR)
LPTSTR      = _out(PTSTR)

LPSIZE_T    = _out(PSIZE_T)
LPSSIZE_T   = _out(PSSIZE_T)
LPWORD      = _out(PWORD)
LPDWORD     = _out(PDWORD)
LPQWORD     = _out(PQWORD)

LPBOOL      = _out(PBOOL)
LPVOID      = _out(PVOID)
LPHANDLE    = _out(PHANDLE)

cast = ctypes.cast
byref = ctypes.byref
sizeof = ctypes.sizeof
pointer = ctypes.pointer
addressof = ctypes.addressof

Union = ctypes.Union
WinError = ctypes.WinError
Structure = ctypes.Structure
LARGE_INTEGER = ctypes.wintypes.LARGE_INTEGER

SZCHAR  = sizeof(CHAR)  # 1
SZWCHAR = sizeof(WCHAR) # 2
SZTCHAR = sizeof(TCHAR) # ?
DEVICE_TYPE = DWORD

NULL = 0

__all__ = [ 'BOOL', 'BOOLEAN', 'BYTE', 'CHAR', 'DWORD', 'HALF_PTR', 'HANDLE', 'INT', 'LONG', 'LONGLONG', 'LONG_PTR',
		    'LPBOOL', 'LPBOOLEAN', 'LPBYTE', 'LPDWORD', 'LPHANDLE', 'LPINT', 'LPLONG', 'LPLONGLONG', 'LPQWORD',
		    'LPSBYTE', 'LPSHORT', 'LPSIZE_T', 'LPSSIZE_T', 'LPSTR', 'LPTSTR', 'LPUINT', 'LPULONG', 'LPULONGLONG',
		    'LPUSHORT', 'LPUSTR', 'LPVOID', 'LPWORD', 'LPWSTR', 'PBOOL', 'PBOOLEAN', 'PBYTE', 'PDWORD', 'PHANDLE',
		    'PINT', 'PLONG', 'PLONGLONG', 'PQWORD', 'PSBYTE', 'PSHORT', 'PSIZE_T', 'PSSIZE_T', 'PSTR', 'PTSTR', 'PUINT',
		    'PULONG', 'PULONGLONG', 'PUSHORT', 'PUSTR', 'PVOID', 'PWORD', 'PWSTR', 'QWORD', 'SBYTE', 'SHORT', 'SIZE_T',
		    'SSIZE_T', 'TCHAR', 'UCHAR', 'UHALF_PTR', 'UINT', 'ULONG', 'ULONGLONG', 'ULONG_PTR', 'USHORT', 'WCHAR',
		    'WORD', 'create_tstring_buffer', 'tstring_at', 'byref', 'sizeof', 'pointer', 'cast', 'addressof', 'WinError',
		    'LARGE_INTEGER', 'Union', 'Structure', 'SZCHAR', 'SZWCHAR', 'SZTCHAR', 'NULL' ]

