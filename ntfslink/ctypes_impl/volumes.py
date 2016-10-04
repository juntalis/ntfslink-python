# encoding: utf-8
"""
Volume utilities.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
import copy
from ._winapi import errcheck_bool_result_checked, BOOL, BYREF, DWORD, MAX_PATH, \
	WINFUNCDECL, create_tstring_buffer, LPTSTR, LPDWORD

##################
# C Declarations #
##################

_GetVolumePathName = WINFUNCDECL(
	'GetVolumePathName', LPTSTR, LPTSTR, DWORD,
	restype=BOOL,  use_tchar=True, errcheck=errcheck_bool_result_checked
)

_GetVolumeInformation = WINFUNCDECL(
	'GetVolumeInformation',
	LPTSTR, LPTSTR, DWORD, LPDWORD, LPDWORD, LPDWORD, LPTSTR, DWORD,
	restype=BOOL, use_tchar=True, errcheck=errcheck_bool_result_checked
)

######################
# API Implementation #
######################

_volume_cache = dict()

def volumename(path, raw=False):
	"""
	Grab the volume name for a given filepath
	:param path: Filepath to get the volume of
	:type path: str
	:param raw: Whether or not to return the ctype instance or just the value
	:type raw: bool
	:return: The volume name for this filepath
	:rtype: ctypes.c_char_p | ctypes.c_wchar_p | str | unicode
	"""
	# Add 1 for a trailing backslash if necessary, and 1 for the terminating
	# null character.
	buflen = len(path) + 2
	volpath = create_tstring_buffer(buflen)
	_GetVolumePathName(path, volpath, buflen)
	return volpath if raw else volpath.value

def volumeinfo(path, use_cache=False):
	"""
	Return information for the volume containing the given path. This is going
	to be a pair containing (file system, file system flags).
	:param path: Filepath to get the volumeinfo for
	:type path: str
	:param use_cache: Whether or not to use a cache for this volume's info
	:type use_cache: bool
	"""
	global _volume_cache
	namebuf = volumename(path, True)

	# Check cache if use_cache was specified
	volkey = copy.copy(namebuf.value).upper()
	if use_cache and volkey in _volume_cache:
		return _volume_cache[volkey]

	# Now that we have the volume root path, we can request the necessary
	# information that will allow us to determine the volume's supported
	# capabilities.
	fsflags = DWORD(0)
	buflen = MAX_PATH + 1
	fsnamebuf = create_tstring_buffer(buflen)
	_GetVolumeInformation(path, None, 0, None, None, BYREF(fsflags), fsnamebuf, buflen)

	# Handle caching if specified
	if use_cache:
		_volume_cache[volkey] = (fsnamebuf.value, fsflags.value)
	return fsnamebuf.value, fsflags.value

__all__ = ['volumename', 'volumeinfo']
