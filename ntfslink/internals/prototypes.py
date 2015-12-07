"""
prototypes.py
Declarations and wrappers for the external C functions.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
from . import memoize
#noinspection PyUnresolvedReferences
from .cutil import In, Out, InOpt, WinDLLEx
from .structures import *

## Functions exported from Kernel32.dll
kernel32 = WinDLLEx('kernel32.dll')

CreateFile = kernel32.CreateFile(ULONG_PTR,
	In(PTSTR, 'lpFileName'),
	In(DWORD, 'dwDesiredAccess'),
	In(DWORD, 'dwShareMode'),
	InOpt(PVOID, 'lpSecurityAttributes', None),
	In(DWORD, 'dwCreationDisposition'),
	In(DWORD, 'dwFlagsAndAttributes'),
	InOpt(HANDLE, 'hTemplateFile')
)
GetFileInformationByHandle = kernel32.GetFileInformationByHandle(BOOL, HANDLE, PBY_HANDLE_FILE_INFORMATION)
CloseHandle = kernel32.CloseHandle(BOOL, HANDLE)

GetFileAttributes = kernel32.GetFileAttributes(DWORD, PTSTR)
SetFileAttributes = kernel32.GetFileAttributes(BOOL, PTSTR, DWORD)

CreateDirectoryT = kernel32.CreateDirectory(BOOL, PTSTR, InOpt(PVOID, 'lpSecurityAttributes', None))
RemoveDirectory = kernel32.RemoveDirectory(BOOL, PTSTR)

GetVolumePathNameT = kernel32.GetVolumePathName(BOOL, PTSTR, LPTSTR, DWORD)
GetVolumePathNamesForVolumeNameT = kernel32.GetVolumePathNamesForVolumeName(BOOL, PTSTR, LPTSTR, DWORD, LPDWORD)
GetVolumeInformationT = kernel32.GetVolumeInformation(BOOL,
	PTSTR, LPTSTR, DWORD, LPDWORD, LPDWORD, LPDWORD, LPTSTR, DWORD
)

GetCurrentProcess = kernel32.GetCurrentProcess(HANDLE)
GetSystemDirectoryT = kernel32.GetSystemDirectory(UINT, PTSTR, UINT)
DeviceIoControl = kernel32.DeviceIoControl(BOOL,
	HANDLE, DWORD, InOpt(PVOID), DWORD, PVOID, DWORD, PDWORD, InOpt(PVOID)
)

CreateHardLink = kernel32.CreateHardLink(BOOLEAN, PTSTR, PTSTR, InOpt(PVOID, 'lpSecurityAttrs', None))
CreateSymbolicLink = kernel32.CreateSymbolicLink(BOOLEAN, PTSTR, PTSTR, DWORD)

GetProcAddressEx = kernel32.GetProcAddress(DWORD, ULONG_PTR, PSTR)

def GetProcAddress(procname):
	return GetProcAddressEx(kernel32._dll_._handle, procname)

## Functions exported from AdvApi32.dll
advapi32 = WinDLLEx('advapi32')

OpenProcessToken = advapi32.OpenProcessToken(BOOL, HANDLE, DWORD, LPHANDLE)
LookupPrivilegeValue = advapi32.LookupPrivilegeValue(BOOL, InOpt(PTSTR), LPTSTR, LPLUID)
AdjustTokenPrivileges = advapi32.AdjustTokenPrivileges(BOOL,
	HANDLE, BOOL, InOpt(PTOKEN_PRIVILEGES), DWORD, LPTOKEN_PRIVILEGES, LPDWORD
)

@memoize
def GetSystemDirectory():
	""" Just a wrapper around the C API to provide a parameter-less function."""
	dirlen = GetSystemDirectoryT(None, 0)
	sysdir = create_tstring_buffer(dirlen)
	if not GetSystemDirectoryT(sysdir, dirlen):
		raise WindowsError()
	return sysdir.value

def GetVolumePathName(filename):
	""" Retrieves the volume mount point where the specified path is mounted. """
	szbuf = len(filename) + 1
	volbuf = create_tstring_buffer(szbuf)
	if GetVolumePathNameT(filename, volbuf, szbuf):
		raise WinError()
	return volbuf.value

def GetVolumePathNamesForVolumeName(volumeguid):
	""" Retrieves a list of drive letters and mounted folder paths for the specified volume. """
	dwsize = DWORD(0)
	# First call the function with an zero-sized buffer to determine the necessary size.
	GetVolumePathNamesForVolumeNameT(volumeguid, NULL, 0, byref(dwsize))
	if dwsize.value == 0:
		raise WinError()

	# Create our buffer and call again
	namesbuf = ctypes.cast(create_tstring_buffer('', dwsize + 1), c_void_p)
	if not GetVolumePathNamesForVolumeNameT(volumeguid, namesbuf, dwsize, byref(dwsize)):
		raise ctypes.WinError()

	# Now find each entry in our buffer and return it as a list.
	bufend = namesbuf.value + dwsize.value
	currname = namesbuf.value
	results = []
	while (currname + sizeof(TCHAR)) < bufend:
		name = tstring_at(currname)
		print name
		results.append(name)
	return results

def GetVolumeInformation(filepath):
	"""
	Return information for the volume containing the given path. This is going
	to be a pair containing (file system, file system flags).
	"""

	# Add 1 for a trailing backslash if necessary, and 1 for the terminating
	# null character.
	volpath = GetVolumePathName(filepath)
	fsnamebuf = create_tstring_buffer(len(filepath))
	fsflags = DWORD(0)
	if not GetVolumeInformationT(volpath, None, 0, None, None, byref(fsflags),
			fsnamebuf, len(fsnamebuf)):
		raise WinError()
	return fsnamebuf.value, fsflags.value
