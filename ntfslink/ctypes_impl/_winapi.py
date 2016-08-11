# encoding: utf-8
"""
_winapi.py
TODO: Description

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
import os
from .. import _util as utility
from functools import wraps as _wraps, partial as _partial

# ctypes imports
import ctypes
from _ctypes import FUNCFLAG_USE_LASTERROR, FUNCFLAG_STDCALL
from ctypes.wintypes import BOOL, WORD, DWORD, HANDLE, LPVOID, ULARGE_INTEGER, \
                            LARGE_INTEGER

###########
# Globals #
###########

## Shortcuts to ctypes stuff
BYREF, SIZEOF = ctypes.byref, ctypes.sizeof
POINTER, pointer = ctypes.POINTER, ctypes.pointer
Structure, Union = ctypes.Structure, ctypes.Union

WinError = ctypes.WinError
get_last_error = ctypes.get_last_error
set_last_error = ctypes.set_last_error

## Platform Info
is_x64 = SIZEOF(ctypes.c_void_p) == SIZEOF(ctypes.c_ulonglong)

## Type Aliases (Windows Naming Conventions)
SIZE_T = ctypes.c_size_t
QWORD = ctypes.c_ulonglong
LPWORD = PWORD = POINTER(WORD)
LPDWORD = PDWORD = POINTER(DWORD)
LPHANDLE = PHANDLE = POINTER(HANDLE)
ULONG_PTR = QWORD if is_x64 else DWORD

## Loaded DLL References
kernel32 = ctypes.WinDLL('kernel32')
advapi32 = ctypes.WinDLL('advapi32')

## Standard Constants
NULL = 0
MAX_PATH = 260
PNULL = ctypes.c_void_p(NULL)
INVALID_HANDLE_VALUE = ULONG_PTR(-1).value

###############
# TCHAR Stuff #
###############

# TODO: This is just a placeholder. Having trouble finding any concrete info on unicode filepath support across Windows versions.
TCHAR_UNICODE = os.path.supports_unicode_filenames

# Set the appropriate handlers
if TCHAR_UNICODE:
	# TODO: Python 3 Fix here
	_T = unicode
	TCHAR_SUFFIX = 'W'
	tstring_at = ctypes.wstring_at
	TCHAR = c_tchar = ctypes.c_wchar
	LPTSTR = c_tchar_p = ctypes.c_wchar_p
	create_tstring_buffer = ctypes.create_unicode_buffer
else:
	_T = str
	TCHAR_SUFFIX = 'A'
	tstring_at = ctypes.string_at
	TCHAR = c_tchar = ctypes.c_char
	LPTSTR = c_tchar_p = ctypes.c_char_p
	create_tstring_buffer = ctypes.create_string_buffer

_TFUNC = lambda name: name + TCHAR_SUFFIX
_TPAIR = lambda name, dll: (_TFUNC(name), dll,)

################################
# Common Handlers for errcheck #
################################

_uses_last_error = lambda func: bool(func._flags_ & FUNCFLAG_USE_LASTERROR)

def _errcheck_failure(result, func, args):
	if _uses_last_error(func):
		return ctypes.WinError(ctypes.get_last_error())
	else:
		return ctypes.WinError(
			descr='Failed call made to {0} (Result: {1}) with args: {2}'.format(
				func.__name__, result, repr(args)
			)
		)

def errcheck_nonzero_failure(result, func, args):
	if bool(result):
		raise _errcheck_failure(result, func, args)
	return result

def errcheck_nonzero_success(result, func, args):
	if not bool(result):
		raise _errcheck_failure(result, func, args)
	return result

def errcheck_handle_result(result, func, args):
	if not bool(result) or result == INVALID_HANDLE_VALUE:
		raise _errcheck_failure(result, func, args)
	return result

def errcheck_bool_result(result, func, args):
	""" Use errcheck functionality to force a Python bool result """
	return bool(result)

def errcheck_bool_result_checked(result, func, args):
	""" Same as errcheck_bool_result, but will only return for True return
	values. False values will be handled as a function failure and handled in
	errcheck_nonzero_success. """
	return bool(errcheck_nonzero_success(result, func, args))

def WINFUNCDECL(name, argtypes, restype=None, **kwargs):
	# Need to remove our custom keyword arguments before calling the prototype
	# factory.
	funcdoc = kwargs.pop('doc', None)
	errcheck = kwargs.pop('errcheck', None)
	paramflags = kwargs.pop('paramflags', None)
	func_spec = (name, kwargs.pop('dll', kernel32))
	FUNCTYPE = kwargs.pop('proto', ctypes.WINFUNCTYPE)
	use_last_error = kwargs.setdefault('use_last_error', True)

	# Handle TCHAR naming if necessary
	if kwargs.pop('use_tchar', False):
		func_spec = _TPAIR(*func_spec)

	# Construct our prototype and apply it to the (name_or_ordinal, dll) pair
	funcptr = FUNCTYPE(restype, *argtypes, **kwargs)(func_spec, paramflags)

	# Apply any specified properties.
	if funcdoc is not None:
		funcptr.__doc__ = funcdoc
	if errcheck is not None:
		funcptr.errcheck = errcheck

	return funcptr

CloseHandle = WINFUNCDECL(
	'CloseHandle', [ HANDLE ], restype=BOOL, errcheck=errcheck_bool_result
)
