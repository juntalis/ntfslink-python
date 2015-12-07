# encoding: utf-8
"""
hardlinks.py
Module for dealing with hard links.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
from .common import *
from contextlib import contextmanager

__all__ = ['example', 'findlinks', 'get_fileinfo']

def timeval(fi, attr):
	print '  %s:' % attr
	val = getattr(fi, attr)
	print '    dwLowDateTime      => 0x%X' % val.dwLowDateTime
	print '    dwHighDateTime     => 0x%X' % val.dwHighDateTime

def example(filepath):
	fileInfo = None
	with HANDLE.open(filepath) as hFile:
		fileInfo = BY_HANDLE_FILE_INFORMATION()
		result = GetFileInformationByHandle(hFile, byref(fileInfo)) != FALSE
		if not result:
			raise WinError()

	print filepath
	print 'File Information'
	print '  dwFileAttributes     => 0x%X' % fileInfo.dwFileAttributes
	timeval(fileInfo, 'ftCreationTime')
	timeval(fileInfo, 'ftLastAccessTime')
	timeval(fileInfo, 'ftLastWriteTime')
	print '  dwVolumeSerialNumber => 0x%X' % fileInfo.dwVolumeSerialNumber
	print '  nFileSizeHigh        => 0x%X' % fileInfo.nFileSizeHigh
	print '  nFileSizeLow         => 0x%X' % fileInfo.nFileSizeLow
	print '  nNumberOfLinks       => 0x%X' % fileInfo.nNumberOfLinks
	print '  nFileIndexHigh       => 0x%X' % fileInfo.nFileIndexHigh
	print '  nFileIndexLow        => 0x%X' % fileInfo.nFileIndexLow


def get_fileinfo(filepath):
	fileinfo = BY_HANDLE_FILE_INFORMATION()
	with HANDLE.open(filepath, 'rw') as hFile:
		if not bool(GetFileInformationByHandle(hFile, byref(fileinfo))):
			raise WinError()
	return fileinfo


def findlinks(filepath):
	fileinfo = get_fileinfo(filepath)
	fileref = LARGE_INTEGER()
	fileref.Parts.LowPart = fileinfo.nFileIndexLow
	fileref.Parts.HighPart = fileinfo.nFileIndexHigh
	buffer = NTFS_FILE_RECORD_OUTPUT_BUFFER()
	result, retcode = deviceioctl(
		filepath, FSCTL_GET_NTFS_FILE_RECORD,
		byref(fileref), sizeof(fileref),
		byref(buffer), sizeof(buffer)
	)
	
	#if not result:
	#	print 'retcode => 0x%08X' % retcode.value
	#	raise WinError()
	#
	return buffer


