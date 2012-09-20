#!/usr/bin/env python
from common import *

# The Windows XP Driver can be found at: http://homepage1.nifty.com/emk/
#	Download (32-bit): http://homepage1.nifty.com/emk/symlink-1.06-x86.cab
#	Download (64-bit): http://homepage1.nifty.com/emk/symlink-1.06-x64.zip
#	English Info: http://schinagl.priv.at/nt/hardlinkshellext/hardlinkshellext.html#symboliclinksforwindowsxp
_WINXP_DRIVER_FILE = 'symlink.sys'

def supports_hardlinks():
	""" Check whether the current system supports hard links. """
	# TODO: Implement a real test of this.
	return has_hardlink_support

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



