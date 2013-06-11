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
from common import *

__all__ = ['example']

def example(filepath):
	inbuf = NTFS_FILE_RECORD_INPUT_BUFFER()
	inbuf.FileReferenceNumber = 1
	outbuf = NTFS_FILE_RECORD_OUTPUT_BUFFER()
	result, dwRet = deviceioctl(filepath,
		FSCTL_GET_NTFS_FILE_RECORD,
		byref(inbuf),
		sizeof(NTFS_FILE_RECORD_INPUT_BUFFER),
		byref(outbuf),
		sizeof(NTFS_FILE_RECORD_OUTPUT_BUFFER)
	)
	print outbuf.raw
	if not result: raise WinError()
