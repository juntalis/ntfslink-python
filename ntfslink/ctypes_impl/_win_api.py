# encoding: utf-8
"""


This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
import os

from .._compat import text_type
from .._util import nameof

# ctypes imports
import ctypes, ctypes.wintypes
from _ctypes import FUNCFLAG_USE_LASTERROR, FUNCFLAG_USE_ERRNO
from ctypes.wintypes import BOOLEAN, BOOL, DWORD, HANDLE, ULONG

###########
# Globals #
###########

## Shortcuts to ctypes functions/classes
POINTER, pointer = ctypes.POINTER, ctypes.pointer
Structure, Union = ctypes.Structure, ctypes.Union
CAST, BYREF, SIZEOF = ctypes.cast, ctypes.byref, ctypes.sizeof

## Platform Info
is_x64 = SIZEOF(ctypes.c_void_p) == SIZEOF(ctypes.c_ulonglong)

## Type Aliases (Windows Naming Conventions)
UCHAR = ctypes.c_ubyte
LPWSTR = ctypes.wintypes.LPWSTR
WORD = USHORT = ctypes.wintypes.WORD
LONG = NTSTATUS = ctypes.wintypes.LONG
QWORD = ULONGLONG = ctypes.c_ulonglong
SIZE_T, LONGLONG = ctypes.c_size_t, ctypes.c_longlong
BYTE, LPVOID = ctypes.wintypes.BYTE, ctypes.wintypes.LPVOID
LARGE_INTEGER, ULARGE_INTEGER = ctypes.wintypes.LARGE_INTEGER, \
                                ctypes.wintypes.ULARGE_INTEGER

LPWORD = PWORD = POINTER(WORD)
LPDWORD = PDWORD = POINTER(DWORD)
LPHANDLE = PHANDLE = POINTER(HANDLE)

## Pointer-sized integer types
if is_x64:
	LONG_PTR = LONGLONG
	ULONG_PTR = ULONGLONG
else:
	LONG_PTR = LONG
	ULONG_PTR = ULONG

## Commonly used function types
CFUNCTYPE = ctypes.CFUNCTYPE
WINFUNCTYPE = ctypes.WINFUNCTYPE

## Loaded DLL References
ntdll = ctypes.WinDLL('ntdll')
kernel32 = ctypes.WinDLL('kernel32')
advapi32 = ctypes.WinDLL('advapi32')

## Standard Constants
NULL = 0
MAX_PATH = 260
FALSE, TRUE = 0, 1
PNULL = ctypes.c_void_p(NULL)
INVALID_HANDLE_VALUE = ULONG_PTR(-1).value

###############
# TCHAR Stuff #
###############

# TODO: This is just a placeholder. Having trouble finding any concrete info on unicode filepath support across Windows versions.
TCHAR_UNICODE = os.path.supports_unicode_filenames

# Set the appropriate handlers
if TCHAR_UNICODE:
	T = text_type
	TCHAR_SUFFIX = 'W'
	tstring_at = ctypes.wstring_at
	TCHAR = c_tchar = ctypes.c_wchar
	LPTSTR = c_tchar_p = ctypes.c_wchar_p
	create_tstring_buffer = ctypes.create_unicode_buffer
else:
	T = str
	TCHAR_SUFFIX = 'A'
	tstring_at = ctypes.string_at
	TCHAR = c_tchar = ctypes.c_char
	LPTSTR = c_tchar_p = ctypes.c_char_p
	create_tstring_buffer = ctypes.create_string_buffer

_TFUNC = lambda name: name + TCHAR_SUFFIX
_TPAIR = lambda name, dll: (_TFUNC(name), dll,)

cstr2wstr = lambda cstr: cstr.encode('utf-16-le')
wstr2cstr = lambda wstr: wstr.decode('utf-16-le')

################################
# Common Handlers for errcheck #
################################

# noinspection PyProtectedMember
_uses_errno = lambda func: bool(func._flags_ & FUNCFLAG_USE_ERRNO)

# noinspection PyProtectedMember
_uses_last_error = lambda func: bool(func._flags_ & FUNCFLAG_USE_LASTERROR)

def _errcheck_failure(result, func, args):
	""" Initializes an exception class instance for a failed errcheck. """
	winerror, errno = None, None
	descr = 'Failed Call: {0}({1}) => {2}'.format(
		nameof(func), repr(args), result
	)
	if _uses_last_error(func):
		winerror = ctypes.get_last_error()
		descr = '{0} [LastError={1}]: {2}'.format(
			descr, winerror, ctypes.FormatError(winerror).strip()
		)
	elif _uses_errno(func):
		errno = ctypes.get_errno()
		descr = '{0} [errno={1}]: {2}'.format(
			descr, errno, os.strerror(errno)
		)
	
	return OSError(errno, descr, None, winerror)

def errcheck_nonzero_failure(result, func, args):
	"""
	Check that the function's result is zero.
	:param result: ctypes function call result
	:param func: ctypes function called
	:param args: function call arguments
	:return: function result
	:raises ctypes.WinError: when the result is non-zero.
	"""
	if bool(result):
		raise _errcheck_failure(result, func, args)
	return result

def errcheck_nonzero_success(result, func, args):
	"""
	Check that the function's result is non-zero.
	:param result: ctypes function call result
	:param func: ctypes function called
	:param args: function call arguments
	:return: function result
	:raises ctypes.WinError: when the result is zero.
	"""
	if not bool(result):
		raise _errcheck_failure(result, func, args)
	return result

def errcheck_handle_result(result, func, args):
	"""
	Check that the function results in a valid handle.
	:param result: Resulting HANDLE to test
	:type result: HANDLE
	:param func: ctypes function called
	:param args: function call arguments
	:return: function result
	:rtype: HANDLE
	:raises ctypes.WinError: when the resulting HANDLE is invalid.
	"""
	if not bool(result) or result == INVALID_HANDLE_VALUE:
		raise _errcheck_failure(result, func, args)
	return result

def errcheck_bool_result(result, func, args):
	""" Use errcheck functionality to force a Python bool result """
	return bool(result)

def errcheck_bool_result_checked(result, func, args):
	""" Same as errcheck_bool_result, but will only return for True return
	    values. False values will be handled as a function failure and handled
	    in errcheck_nonzero_success. """
	return bool(errcheck_nonzero_success(result, func, args))

# noinspection PyUnusedLocal
def errcheck_ntstatus_success(result, func, args):
	"""
	Tests the resulting status code to see whether the called operation was a
	success.
	:param result: ``NTSTATUS`` return from our function call.
	:type result: int | ctypes.c_long
	:param func: Called function
	:type func: (...) -> NTSTATUS
	:param args: Function call arguments
	:type args: tuple[any]
	:return: ``True`` if successful. False otherwise.
	:rtype: bool
	"""
	status = int(result)
	return (
		0 <= status <= 0x3FFFFFFF
	) or (
		0x40000000 <= status <= 0x7FFFFFFF
	)

def errcheck_ntstatus_checked(result, func, args):
	"""
	:func:`errcheck_ntstatus_success`, but throws an error if the call was not
	successful.
	:param result: ``NTSTATUS`` return from our function call.
	:type result: int | ctypes.c_long
	:param func: Called function
	:type func: (...) -> NTSTATUS
	:param args: Function call arguments
	:type args: tuple[any]
	:return: Always ``True``. In any other case, an error occurs.
	:rtype: bool
	:raises OSError: if the call was not successful.
	"""
	if not errcheck_ntstatus_success(result, func, args):
		_errcheck_failure(result, func, args)
	return True

# noinspection PyProtectedMember
def WINFUNCDECL(name, *argtypes, **kwargs):
	"""
	Utility function for easily declaring ctypes function bindings
	:param name: Function name. 
	:type name: str
	:param argtypes: parameter types
	:type argtypes: *type
	:param kwargs: doc, errcheck, paramflags, dll, proto, use_tchar
	:type kwargs: object
	:return: Callable function pointer
	:rtype: _CFuncPtr
	"""
	# Return type defaults to ``None``. (``void``)
	restype = kwargs.pop('restype', None)
	
	# Need to remove our custom keyword arguments before calling the prototype
	# factory.
	dll = kwargs.pop('dll', kernel32)
	funcdoc = kwargs.pop('doc', None)
	errcheck = kwargs.pop('errcheck', None)
	paramflags = kwargs.pop('paramflags', None)
	FUNCTYPE = kwargs.pop('proto', ctypes.WINFUNCTYPE)

	# Handle TCHAR naming if necessary
	func_spec = (name, dll)
	if kwargs.pop('use_tchar', False):
		func_spec = _TPAIR(*func_spec)

	# Set any remaining defaults
	kwargs.setdefault('use_last_error', True)

	# Construct our prototype and apply it to the (name_or_ordinal, dll) pair
	funcptr = FUNCTYPE(restype, *argtypes, **kwargs)(func_spec, paramflags)

	# Apply "name" properties
	funcptr._name = name
	funcptr._dll_name = dll._name
	funcptr.__name__ = '{0}.{1}'.format(funcptr._dll_name, name)

	# Apply any specified properties.
	if funcdoc is not None:
		funcptr.__doc__ = funcdoc
	if errcheck is not None:
		funcptr.errcheck = errcheck

	return funcptr

def NTFUNCDECL(name, *argtypes, **kwargs):
	"""
	Wrapper around :func:`WINFUNCDECL` providing defaults for native calls made
	to ntdll's exports.
	:param name: Function name.
	:type name: str
	:param argtypes: parameter types
	:type argtypes: *type
	:param kwargs: doc, errcheck, paramflags, dll, proto, use_tchar
	:type kwargs: object
	:return: Callable function pointer
	:rtype: _CFuncPtr
	"""
	kwargs.setdefault('dll', ntdll)
	kwargs.setdefault('restype', NTSTATUS)
	kwargs.setdefault('use_last_error', False)
	#kwargs.setdefault('errcheck', errcheck_ntstatus_checked)
	if name.startswith('Zw'): name = 'Nt' + name[2:]
	return WINFUNCDECL(name, *argtypes, **kwargs)

# Declare CloseHandle here to avoid circular import issues in :mod:`privileges`.
#: Used to close handles created by :func:`open_file_r`, :func:`open_file_w`,
#: and :func:`open_file_rw`.
CloseHandle = WINFUNCDECL(
	'CloseHandle', HANDLE, restype=BOOL, errcheck=errcheck_bool_result
)
