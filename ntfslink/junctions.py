# encoding: utf-8
"""
junctions.py
Module for dealing with junction points.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
from .common import *

__all__ = ['create', 'check', 'read', 'unlink']

def _prefill(reparseInfo, source, substlink, link_name, isabs):
	""" For create """
	reparseInfo.ReparseTag = IO_REPARSE_TAG_MOUNT_POINT

	# Calculate the lengths of the names.
	lensubst = len(substlink) * SZWCHAR
	lenprint = len(source) * SZWCHAR

	# reparseInfo.ReparseDataLength = datalen + 12
	reparseInfo.Reserved = 0
	reparseInfo.MountPoint = MountPointBuffer()
	reparseInfo.MountPoint.SubstituteNameOffset = 0
	reparseInfo.MountPoint.SubstituteNameLength = lensubst
	reparseInfo.MountPoint.PrintNameOffset = lensubst + SZWCHAR # Ending \0
	reparseInfo.MountPoint.PrintNameLength = lenprint

	(bufflen, reparseInfo.ReparseDataLength) = CalculateLength(MountPointBuffer, reparseInfo.MountPoint)

	# Assign the PathBuffer, then resize it, etc.
	reparseInfo.MountPoint.PathBuffer = u'%s\0%s' % (substlink, source)
	pReparseInfo = pointer(reparseInfo)
	#noinspection PyProtectedMember
	reparseInfo.MountPoint._fields_[4] = ('PathBuffer', bufflen)
	return pReparseInfo

def create(srcpath, linkpath):
	"""
	Create a junction at linkpath pointing to srcpath directory.

	See: os.symlink
	"""
	srcpath = str_cleanup(srcpath)
	linkpath = str_cleanup(linkpath)
	if not path.isdir(srcpath):
		raise InvalidSourceException('Non-existent source path, "{0}"'.format(srcpath))

	linkpath = path.abspath(linkpath)
	if path.exists(linkpath):
		raise InvalidSourceException('Filepath for new junction already exists.')

	if not CreateDirectory(linkpath):
		raise IOError('Failed to create new directory for target junction.')

	result = create_reparse_point(srcpath, linkpath, _prefill)
	if not result: RemoveDirectory(linkpath)
	return result

def check(linkpath):
	"""
	Checks if linkpath is a junction.

	See: os.path.islink
	"""
	return IsReparseDir(linkpath)

def read(linkpath):
	"""
	Read the target of the junction at linkpath.

	See: os.readlink
	"""
	reparseInfo = get_buffer(linkpath, ReparsePoint, check)
	if reparseInfo is not None:
		# Unfortunately I cant figure out a way to get the PrintName. The problem is, PathBuffer should currently
		# contain a c_wchar array that holds SubstituteName\0PrintName\0. Unfortunately, since it automatically
		# converts it to a unicode string, I've been unable to figure out a way to access the data past the first
		# terminating \0. So instead, we'll just use the SubstituteName and remove the \??\ from the front.
		target = str(reparseInfo.MountPoint.PathBuffer)
		if target[:4] == '\\??\\':
			target = target[4:]
		return target
	return None


def unlink(linkpath):
	"""
	Remove the junction at linkpath.

	See: os.rmdir
	"""
	result, dwRet = delete_reparse_point(linkpath, IO_REPARSE_TAG_MOUNT_POINT, check)
	if result: RemoveDirectory(linkpath)
	return result, dwRet

def example():
	import os
	sfolder = '/Temp'
	sjunction = 'temp'
	if path.isfile(sfolder):
		import random
		while path.isfile(sfolder):
			sfolder += '%d' % int(random.uniform(1, 10))

	print 'Junction Example'
	removeTemporaryFolder = False
	if not path.isdir(sfolder):
		os.mkdir(sfolder)
		print 'Temporarily created %s folder for the purpose of this example.' % path.abspath(sfolder)
		removeTemporaryFolder = True

	print 'create(%s, %s)' % (sfolder, sjunction), create(sfolder, sjunction)
	print 'check(%s)' % sjunction, check(sjunction)
	# For some reason, having read() directly followed by unlink results in the read function not returning correctly.
	# I'll try to figure it out, but since most use cases wont need to read a junction and immediately delete it,
	# I probably won't put much time into it.
	content = read(sjunction)
	if content is not None:
		import pprint
		pprint.pprint('read(%s) %s' % (sjunction, content))
	raw_input('Press any key to delete the "%s" junction.' % sjunction)
	print 'unlink(%s)' % sjunction, unlink(sjunction)

	if removeTemporaryFolder:
		print 'Removing the temporary folder created at %s.' % path.abspath(sfolder)
		os.rmdir(sfolder)

if __name__=='__main__':
	example()
