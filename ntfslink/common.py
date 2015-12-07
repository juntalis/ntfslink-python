# encoding: utf-8
"""
common.py
Common base functions for manipulating reparse points and accomplishing generic tasks.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
from .internals.helpers import *

class PassThru(object):
	""" A class created for the purpose of passing function calls through to the underlying module. """

	def __init__(self, realmod):
		self._real_ = realmod

	def __call__(self, *args, **kwargs):
		return self._real_.create(*args, **kwargs)

	@property
	def create(self): return self._real_.create

	@property
	def read(self): return self._real_.read

	@property
	def unlink(self): return self._real_.unlink

	@property
	def check(self): return self._real_.check

def passthru(cls, realmod):
	""" Construct a PassThru derived class. """
	return type(cls, (PassThru,), { })(realmod)

def str_cleanup(s):
	""" Helper for cleaning a string prior to creating a reparse point. """
	return str(s).strip('\0 ')

def create_reparse_point(source, link_name, prefill, isabs = True):
	"""
	Create a reparse point at link_name pointing to source.

	"""
	# SubstituteName
	substlink = source
	if isabs:
		substlink = ExtendedAbspath(source)
	hFile = OpenFileRW(link_name, os.path.isdir(link_name))

	# Construct our structure. Note: We have enter the fields one by one due tot he fact that we still need
	# to resize the PathBuffer field.
	reparseInfo = ReparsePoint()
	pReparseInfo = prefill(reparseInfo, source, substlink, link_name, isabs)
	returnedLength = DWORD(0)
	result = bool(DeviceIoControl(
		hFile, FSCTL_SET_REPARSE_POINT, pReparseInfo,
		reparseInfo.ReparseDataLength + REPARSE_POINT_HEADER_SIZE,
		None, 0, byref(returnedLength), None
	))
	CloseHandle(hFile)
	return result

def deviceioctl(fpath, code, inbuf, insize, outbuf, outsize, hFile = INVALID_HANDLE_VALUE):
	"""
	Open a file and run it through DeviceIoControl with a specific code.
	"""
	close_handle = True
	if hFile == INVALID_HANDLE_VALUE:
		hFile = OpenFileRW(fpath, os.path.isdir(fpath))
	else:
		close_handle = False

	dwRet = DWORD(0)
	result = bool(DeviceIoControl(
		hFile, code, inbuf, insize,
		outbuf, outsize, byref(dwRet), None
	))

	if close_handle:
		CloseHandle(hFile)
	return result, dwRet

def get_buffer(fpath, cls, check, hFile = INVALID_HANDLE_VALUE):
	"""
	Get a reparse buffer.
	cls: The class we'll be using (either ReparsePoint or ReparseGuidDataBuffer)
	check: Function to check validity of a reparse point. (usually is_reparse_dir, is_reparse_point, etc)
	"""
	if check is not None and not check(fpath):
		raise InvalidLinkException("%s is not a reparse point." % fpath)

	close_handle = True
	if hFile == INVALID_HANDLE_VALUE:
		hFile = OpenFileR(fpath, os.path.isdir(fpath))
	else:
		close_handle = False

	dwRet = DWORD(0)
	reparseInfo = cls()
	result = bool(DeviceIoControl(
		hFile, FSCTL_GET_REPARSE_POINT, None, 0L,
		byref(reparseInfo), MAX_REPARSE_BUFFER, byref(dwRet), None
	))

	if close_handle:
		CloseHandle(hFile)
	return reparseInfo if result else None

def delete_reparse_point(fpath, tag, check):
	"""
	Remove the reparse point at fpath.

	See: get_buff for details
	"""
	if not check(fpath):
		raise InvalidLinkException("%s is not a reparse point." % fpath)

	hFile = OpenFileRW(fpath, os.path.isdir(fpath))
	dwRet = DWORD()

	# Try to delete it first without the reparse GUID
	reparseInfo = ReparseGuidDataBuffer()
	reparseInfo.ReparseTag = tag
	result = bool(DeviceIoControl(
		hFile,
		FSCTL_DELETE_REPARSE_POINT,
		byref(reparseInfo),
		REPARSE_GUID_DATA_BUFFER_HEADER_SIZE,
		None, 0L, byref(dwRet), None
	))

	if not result:
	# If the first try fails, we'll set the GUID and try again
		buf = get_buffer(fpath, ReparseGuidDataBuffer, None, hFile)
		reparseInfo.ReparseTag = buf.ReparseTag
		reparseInfo.ReparseGuid = buf.ReparseGuid
		result = bool(DeviceIoControl(
			hFile,
			FSCTL_DELETE_REPARSE_POINT,
			byref(reparseInfo),
			REPARSE_GUID_DATA_BUFFER_HEADER_SIZE,
			None, 0L, byref(dwRet), None
		))
		if not result:
			raise WinError()

	CloseHandle(hFile)
	return result, dwRet


