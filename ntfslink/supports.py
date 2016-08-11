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
import sys as _sys
from . import _util as utility
from ._impl import supports as impl

# Utility lambdas
_build_winvers = lambda versobj: versobj.major * 100 + versobj.minor

## Windows version stuff
winvers = _build_winvers(_sys.getwindowsversion())
is_gt_winxp = winvers >= 600
is_gt_vista = winvers >= 601

@utility.once
def _os_symlinks():
	return is_gt_winxp or impl.xp_symlinks()

def hardlinks(path=None, use_cache=False):
	"""
	Checks if hardlinks are supported by the operating system. If a file/folder
	path is specified, the volume of that path will also be checked for hardlink
	support.

	Note: I haven't been able to find any definitive information on when
	hardlink support was actually introduced. (Other than some vague info about
	NTFS always supporting hardlinks) Until I can find some definitive info,
	we're just going to assume that os support is always available. The ability
	to check volume support wasn't added until Windows 7, so we're assuming
	support for any systems older than Windows 7.
	:param path: Optional file/folder path to check volume hardlink support
	:type path: str|unicode|None
	:param use_cache: Optional flag to cache the volume info across calls.
	:type use_cache: bool
	:return: Whether or not the system/path supports hardlinks.
	:rtype: bool
	"""
	if path is None or not is_gt_vista:
		return True
	else:
		return impl.fs_hardlinks(path, use_cache)

def reparse_points(path=None, use_cache=False):
	"""
	Checks if reparse points are supported by the operating system. If a
	file/folder path is specified, the volume of that path will also be checked
	for support.

	Note: As with hardlinks, I haven't really been able to find much in terms
	of definitive information regarding support on this. For now, we'll assume
	all supported operating systems have built-in support for reparse points.
	:param path: Optional file/folder path to check volume reparse point support
	:type path: str|unicode|None
	:param use_cache: Optional flag to cache the volume info across calls.
	:type use_cache: bool
	:return: Whether or not the system/path supports symlinks.
	:rtype: bool
	"""
	return path is None or impl.fs_reparse_points(path, use_cache)

def junctions(path=None, use_cache=False):
	"""
	Checks if reparse points are supported by the operating system. If a
	file/folder path is specified, the volume of that path will also be checked
	for support.

	Note: Just passes through to supports.reparse_points
	:param path: Optional file/folder path to check volume symlink support
	:type path: str|unicode|None
	:param use_cache: Optional flag to cache the volume info across calls.
	:type use_cache: bool
	:return: Whether or not the system/path supports symlinks.
	:rtype: bool
	"""
	return reparse_points(path, use_cache)

# TODO: Think of a way to handle the cache stuff nicely at this level (rather than at the impl level)
def symlinks(path=None, use_cache=False):
	"""
	Checks if symlinks are supported by the operating system. If a file/folder
	path is specified, the volume of that path will also be checked for symlink
	support.

	Note: See project README for info on symlink support pre-Vista.
	:param path: Optional file/folder path to check volume symlink support
	:type path: str|unicode|None
	:param use_cache: Optional flag to cache the volume info across calls.
	:type use_cache: bool
	:return: Whether or not the system/path supports symlinks.
	:rtype: bool
	"""
	os_support = _os_symlinks()
	if not os_support or path is None:
		return os_support
	else:
		return impl.fs_reparse_points(path, use_cache)

# Cleanup unnecessary lambdas
del _build_winvers

__all__ = [ 'hardlinks', 'reparse_points', 'junctions', 'symlinks' ]
