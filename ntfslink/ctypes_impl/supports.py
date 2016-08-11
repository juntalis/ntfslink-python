# encoding: utf-8
"""
supports.py
TODO: Description

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
from .volumes import volumeinfo
from ..supports import is_gt_winxp
from ._winapi import errcheck_bool_result, BOOL, LPVOID, get_last_error, \
	WinError, DWORD, set_last_error, WINFUNCDECL, HANDLE, LPTSTR, advapi32, \
	errcheck_nonzero_success

#########
# WinXP #
#########

if not is_gt_winxp:
	# The following is only necessary for Windows XP users, who can use symbolic
	# links through a third party driver.
	# The Windows XP Driver can be found at: http://homepage1.nifty.com/emk/
	# Download (32-bit): http://homepage1.nifty.com/emk/symlink-1.06-x86.cab
	# Download (64-bit): http://homepage1.nifty.com/emk/symlink-1.06-x64.zip
	# English Info: http://schinagl.priv.at/nt/hardlinkshellext/hardlinkshellext.html#symboliclinksforwindowsxp
	WINXP_DRIVER_NAME = 'symlink'

	ERROR_SUCCESS                = 0x00000000
	ERROR_SERVICE_DOES_NOT_EXIST = 0x00000424

	SC_MANAGER_CONNECT = SERVICE_QUERY_CONFIG = 0x00000001

	# Easier to work with LPVOID, especially we're just using NULL for most
	# parameters.
	_OpenSCManager = WINFUNCDECL(
		'OpenSCManager', [ LPVOID, LPVOID, DWORD ],
		restype=HANDLE, use_tchar=True, dll=advapi32,
		errcheck=errcheck_nonzero_success
	)
	_OpenService = WINFUNCDECL(
		'OpenService', [ HANDLE, LPTSTR, DWORD ],
		restype=HANDLE, use_tchar=True, dll=advapi32
	)
	_CloseServiceHandle = WINFUNCDECL(
		'CloseServiceHandle', [ HANDLE ],
		restype=BOOL, dll=advapi32,
		errcheck=errcheck_bool_result
	)

	def xp_symlinks():
		installed = True
		hSCM = _OpenSCManager(0, 0, SC_MANAGER_CONNECT)
		hService = _OpenService(hSCM, WINXP_DRIVER_NAME, SERVICE_QUERY_CONFIG)
		if not hService:
			lasterror = get_last_error()
			if lasterror == ERROR_SERVICE_DOES_NOT_EXIST:
				hService = None
				installed = False
				set_last_error(ERROR_SUCCESS)
			else:
				raise WinError(code=lasterror)

		if hService is not None:
			_CloseServiceHandle(hService)
		_CloseServiceHandle(hSCM)
		return installed
else:
	# Just for API uniformity

	def xp_symlink():
		# Should never actually be called
		return True

##########################
# Common Implementations #
##########################

FILE_SUPPORTS_HARD_LINKS     = 0x00400000
FILE_SUPPORTS_REPARSE_POINTS = 0x00000080

def fs_reparse_points(filepath, use_cache=False):
	""" Determine if a path supports reparse point records based on the volume flags. """
	# TODO: Verify that FILE_SUPPORTS_REPARSE_POINTS in WinXP.
	fsflags = volumeinfo(filepath, use_cache)[1]
	return bool(fsflags & FILE_SUPPORTS_REPARSE_POINTS)

def fs_hardlinks(filepath, use_cache=False):
	"""
	Note: FILE_SUPPORTS_HARD_LINKS isn't supported until Windows 7, so this
	should only be called for Windows 7+ systems.
	"""
	fsflags = volumeinfo(filepath, use_cache)[1]
	return bool(fsflags & FILE_SUPPORTS_HARD_LINKS)





