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
from common import *

__all__ = ['create', 'check', 'read', 'unlink']

def create(source, link_name):
	"""
	Create a symbolic link at link_name pointing to source.

	See: os.symlink
	"""
	source = str_cleanup(source)
	link_name = str_cleanup(link_name)
	if os.path.isabs(source) and not path.exists(source):
		raise Exception('Symbolic link source does not exist or is not a directory.')

	link_name = path.abspath(link_name)
	if path.exists(link_name):
		raise Exception('Filepath for new symbolic link already exists.')

	link_isdir = os.path.isdir(source)
	if link_isdir:
		link_isdir = True
		if not CreateDirectory(link_name):
			raise Exception('Failed to create new directory for target symbolic link.')

	dwFlags = DWORD(SYMBOLIC_LINK_FLAG_DIRECTORY if link_isdir else SYMBOLIC_LINK_FLAG_FILE)
	result = CreateSymbolicLinkW(link_name, source, dwFlags) != FALSE
	if link_isdir and not result:
		RemoveDirectory(link_name)
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
	reparseInfo.SymbolicLink.Flags = SYMLINK_FLAG_RELATIVE if not isabs else 0

	(bufflen, reparseInfo.ReparseDataLength) = CalculateLength(SymbolicLinkBuffer, reparseInfo.SymbolicLink)

	# Assign the PathBuffer, then resize it, etc.
	reparseInfo.SymbolicLink.PathBuffer = u'%s%s' % (substlink, source)
	pReparseInfo = pointer(reparseInfo)
	reparseInfo.SymbolicLink._fields_[5] = ('PathBuffer', bufflen)
	return pReparseInfo

def broken_create(source, link_name):
	"""
	TODO: Fix this.
	"""
	source = str_cleanup(source)
	link_name = str_cleanup(link_name)
	if os.path.isabs(source) and not path.exists(source):
		raise Exception('Symbolic link source does not exist or is not a directory.')

	link_name = path.abspath(link_name)
	if path.exists(link_name):
		raise Exception('Filepath for new symbolic link already exists.')

	link_isdir = os.path.isdir(source)
	if link_isdir:
		link_isdir = True
		if not CreateDirectory(link_name):
			raise Exception('Failed to create new directory for target symbolic link.')

	result = create_reparse_point(source, link_name, _prefill, os.path.isabs(source))
	if link_isdir and not result:
		RemoveDirectory(link_name)
	return result

def check(fpath):
	"""
	Checks if fpath is a symbolic link.

	See: os.path.islink
	"""
	return IsReparsePoint(fpath)

def read(fpath):
	"""
	Read the target of the symbolic link at fpath.

	See: os.readlink
	"""
	reparseInfo = get_buffer(fpath, ReparsePoint, check)
	if reparseInfo is not None:
		# Unfortunately I cant figure out a way to get the PrintName. The problem is, PathBuffer should currently
		# contain a c_wchar array that holds SubstituteName\0PrintName\0. Unfortunately, since it automatically
		# converts it to a unicode string, I've been unable to figure out a way to access the data past the first
		# terminating \0. So instead, we'll just use the SubstituteName and remove the \??\ from the front.
		slink = reparseInfo.SymbolicLink
		target = str(slink.PathBuffer)[slink.PrintNameOffset:slink.PrintNameLength]
		if target[:4] == '\\??\\':
			target = target[4:]
		return target
	return None

def unlink(fpath):
	"""
	Remove the symbolic link at fpath.

	See: os.rmdir
	"""
	link_isdir = os.path.isdir(fpath)
	result, dwRet = delete_reparse_point(fpath, IO_REPARSE_TAG_SYMBOLIC_LINK, check)
	if link_isdir and result: RemoveDirectory(fpath)
	return result, dwRet
