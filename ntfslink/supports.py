# encoding: utf-8
"""
supports.py
Module for testing the capabilities of an individual hard drive or of the current OS.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
import sys
from common import *

# The Windows XP Driver can be found at: http://homepage1.nifty.com/emk/
#	Download (32-bit): http://homepage1.nifty.com/emk/symlink-1.06-x86.cab
#	Download (64-bit): http://homepage1.nifty.com/emk/symlink-1.06-x64.zip
#	English Info: http://schinagl.priv.at/nt/hardlinkshellext/hardlinkshellext.html#symboliclinksforwindowsxp
_WINXP_DRIVER_FILE = 'symlink.sys'

class FileSystemSupports(object):
	__slots__ = (
		'CreationTimestamp',  'LastAccessTimestamp', 'LastChangeTimestamp',
		'HardLinks', 'SymbolicLinks', 'MountPoints',
		'SparseFiles', 'NamedStreams', 'AlternateDataStreams',
		'ExtendedAttributes', 'Compression', 'Encryption',
		'FileChangeLog', 'FileOwner', 'ACL',
	)

	def __init__(self, **kw):
		support = lambda key: setattr(self, key, kw.get(key, True))
		map(support, self.__slots__)

FSFormats = {
	'NTFS':  FileSystemSupports(),
	'UDF':   FileSystemSupports(
		SymbolicLinks=False, MountPoints=False,
		Compression=False, Encryption=False,
		FileChangeLog=False, FileOwner=False, ACL=False
	),
	'exFAT': FileSystemSupports(
		HardLinks=False, SymbolicLinks=False, MountPoints=False,
		SparseFiles=False, NamedStreams=False, AlternateDataStreams=False,
		ExtendedAttributes=False, Compression=False, Encryption=False,
		FileChangeLog=False, FileOwner=False, ACL=False
	),
	'FAT32': FileSystemSupports(
		HardLinks=False, SymbolicLinks=False, MountPoints=False,
		SparseFiles=False, NamedStreams=False, AlternateDataStreams=False,
		ExtendedAttributes=False, Compression=False, Encryption=False,
		FileChangeLog=False, FileOwner=False, ACL=False
	)
}

def supports_hardlinks():
	""" Check whether the current system supports hard links. """
	# TODO: Implement a real test of this.
	return CreateHardLinkW is not None

def supports_symlinks():
	""" Checks whether or not the current system supports symbolic links. """
	if sys.getwindowsversion()[0] >= 6: return True
	sysdir = GetSystemDirectory()
	driver = path.join(sysdir, 'drivers', _WINXP_DRIVER_FILE)
	return path.isfile(driver)

def path_supports_symlinks(filepath):
	"""
	Checks if a path is valid for symbolic links.

	Right now, this just verifieds that symbolic links are supported on the machine, and the filepath's volume
	has an NTFS filesystem.
	"""
	if not supports_symlinks(): return False
	drive = path.splitdrive(path.abspath(filepath))[0] + '\\'
	fs = create_unicode_buffer(MAX_PATH+1)
	if GetVolumeInformationW(drive, None, 0, None, None, None, fs, MAX_PATH+1) == FALSE:
		raise WindowsError()
	return fs.value.strip() == 'NTFS'



