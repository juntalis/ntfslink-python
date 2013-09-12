# encoding: utf-8
"""
cyglinks.py
Module for dealing with cygwin symbolic links.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
from .common import *

__all__ = [ 'create', 'check', 'read', 'unlink' ]

# Cygwin symbolic links start with:
cyglink_tag = '!<symlink>'

def utf8str(data):
	databuf = data
	if isinstance(data, unicode):
		databuf = data.encode('utf8')
	elif data[:2] == '\xff\xfe':
		databuf = data.decode('utf16')
	return databuf.rstrip('\0')

def utf16str(data):
	databuf = data
	if isinstance(data, unicode):
		databuf = data.decode('utf8').encode('utf16')
	elif data[:2] != '\xff\xfe':
		databuf = data.encode('utf16')
	return databuf.rstrip('\0') + '\0\0'

def verify_filepath(filepath):
	""" Verify that a filepath has the proper attributes to be a cygwin symlink. """
	return os.path.isfile(filepath) and \
		(GetFileAttributesW(filepath) & FILE_ATTRIBUTE_SYSTEM) == FILE_ATTRIBUTE_SYSTEM

def verify_data(data):
	""" Verify that data contains a valid cygwin symlink """
	databuf = data
	if isinstance(data, file):
		pos = data.tell()
		data.seek(0)
		databuf = data.read()
		data.seek(pos)
	return len(databuf) > 10 and databuf[:10] == cyglink_tag

def create(srcpath, linkpath):
	"""
	Create a cygwin symbolic link at link_name pointing to srcpath.

	See: os.symlink
	"""
	src = utf16str(srcpath)
	with open(linkpath, 'wb') as f:
		f.write(cyglink_tag)
		f.write(src)
	return SetFileAttributesW(srcpath, FILE_ATTRIBUTE_SYSTEM) != FALSE

def check(linkpath):
	"""
	Checks if filepath is a cygwin symbolic link.

	See: os.path.islink
	"""
	if verify_filepath(linkpath):
		with open(linkpath, 'rb') as f:
			return verify_data(f)
	return False

def read(linkpath):
	"""
	Read the target of the cygwin symbolic link at filepath.

	See: os.readlink
	"""
	if not verify_filepath(linkpath): raise InvalidLinkException(linkpath)
	with open(linkpath, 'rb') as f: databuf = f.read()
	if not verify_data(databuf): raise InvalidLinkException(linkpath)
	return utf8str(databuf[10:])

def unlink(linkpath):
	"""
	Remove the cygwin symbolic link at linkpath.

	See: os.rmdir
	"""
	if not verify_filepath(linkpath): raise InvalidLinkException(linkpath)
	if SetFileAttributesW(linkpath, FILE_ATTRIBUTE_NORMAL) == FALSE:
		raise WinError()
	os.unlink(linkpath)
	return True, 0
