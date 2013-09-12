# encoding: utf-8
"""
symlinks.py
Module for dealing with symbolic links.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
from .common import *

__all__ = ['create', 'check', 'read', 'unlink']

def create(srcpath, linkpath):
	"""
	Create a symbolic link at linkpath pointing to srcpath.

	See: os.symlink
	"""
	srcpath = str_cleanup(srcpath)
	linkpath = str_cleanup(linkpath)
	if os.path.isabs(srcpath) and not path.exists(srcpath):
		raise InvalidSourceException('Non-existent source path, "{0}"'.format(srcpath))

	linkpath = path.abspath(linkpath)
	if path.exists(linkpath):
		raise InvalidSourceException('Filepath for new symbolic link already exists.')

	link_isdir = os.path.isdir(srcpath)
	if link_isdir:
		link_isdir = True
		if not CreateDirectory(linkpath):
			raise IOError('Failed to create new directory for target symbolic link.')

	dwFlags = DWORD(SYMBOLIC_LINK_FLAG_DIRECTORY if link_isdir else SYMBOLIC_LINK_FLAG_FILE)
	result = CreateSymbolicLinkW(linkpath, srcpath, dwFlags) != FALSE
	if link_isdir and not result:
		RemoveDirectory(linkpath)
	return result

def _prefill(reparseInfo, source, substlink, link_name, isabs):
	""" For broken_create """
	reparseInfo.ReparseTag = IO_REPARSE_TAG_SYMBOLIC_LINK

	# Calculate the lengths of the names.
	lensubst = len(substlink) * SZWCHAR
	lenprint = len(source) * SZWCHAR

	# reparseInfo.ReparseDataLength = datalen + 12
	reparseInfo.Reserved = 0
	reparseInfo.SymbolicLink = SymbolicLinkBuffer()
	reparseInfo.SymbolicLink.PrintNameOffset = 0
	reparseInfo.SymbolicLink.PrintNameLength = lenprint
	reparseInfo.SymbolicLink.SubstituteNameOffset = lenprint
	reparseInfo.SymbolicLink.SubstituteNameLength = lensubst
	reparseInfo.SymbolicLink.Flags = SYMBOLIC_LINK_FLAG_RELATIVE if not isabs else 0

	(bufflen, reparseInfo.ReparseDataLength) = CalculateLength(SymbolicLinkBuffer, reparseInfo.SymbolicLink)

	# Assign the PathBuffer, then resize it, etc.
	reparseInfo.SymbolicLink.PathBuffer = u'%s%s' % (substlink, source)
	pReparseInfo = pointer(reparseInfo)
	reparseInfo.SymbolicLink._fields_[5] = ('PathBuffer', bufflen)
	return pReparseInfo

def broken_create(srcpath, linkpath):
	"""
	TODO: Fix this.
	"""
	srcpath = str_cleanup(srcpath)
	linkpath = str_cleanup(linkpath)
	if os.path.isabs(srcpath) and not path.exists(srcpath):
		raise InvalidSourceException('Symbolic link source does not exist or is not a directory.')

	linkpath = path.abspath(linkpath)
	if path.exists(linkpath):
		raise InvalidSourceException('Filepath for new symbolic link already exists.')

	link_isdir = os.path.isdir(srcpath)
	if link_isdir:
		link_isdir = True
		if not CreateDirectory(linkpath):
			raise IOError('Failed to create new directory for our target symbolic link.')

	result = create_reparse_point(srcpath, linkpath, _prefill, os.path.isabs(srcpath))
	if link_isdir and not result:
		RemoveDirectory(linkpath)
	return result

def check(linkpath):
	"""
	Checks if linkpath is a symbolic link.

	See: os.path.islink
	"""
	return IsReparsePoint(linkpath)

def read(linkpath):
	"""
	Read the target of the symbolic link at linkpath.

	See: os.readlink
	"""
	reparseInfo = get_buffer(linkpath, ReparsePoint, check)
	if reparseInfo is not None:
		symlink = reparseInfo.SymbolicLink
		return symlink.PathBuffer[symlink.PrintNameOffset/SZWCHAR:symlink.PrintNameLength/SZWCHAR]
	return None

def unlink(linkpath):
	"""
	Remove the symbolic link at linkpath.

	See: os.rmdir
	"""
	link_isdir = os.path.isdir(linkpath)
	result, dwRet = delete_reparse_point(linkpath, IO_REPARSE_TAG_SYMBOLIC_LINK, check)
	if link_isdir and result: RemoveDirectory(linkpath)
	return result, dwRet
