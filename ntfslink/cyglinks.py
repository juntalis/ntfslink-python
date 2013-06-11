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
from common import *

# Cygwin symbolic links start with:
CYGLINK_SIGNATURE = [ 0x21, 0x3C, 0x73, 0x79, 0x6D, 0x6C, 0x69, 0x6E, 0x6B, 0x3E, 0xFF, 0xFE ]

class CygLink(Structure):
	"""
	CTypes implementation of:

	typedef struct {
		char tag[10]; 
		unsigned short reserved1;
		wchar_t target[ANYSIZE_ARRAY];
	} cyglink;
	"""

	#noinspection PyTypeChecker
	_fields_ = [
		("Reserved1", BYTE * 12), # '!<symlink>' followed by '\xff\xfe'
		("PathBuffer", WCHAR * (MAX_PATH+1))
	]
	
	def __init__(self, target=None):
		super(CygLink, self).__init__()
		if target is not None:
			self.PathBuffer = target
		for i, b in enumerate(CYGLINK_SIGNATURE):
			self.Reserved1[i] = b
