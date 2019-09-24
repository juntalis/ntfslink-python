# encoding: utf-8
"""
Glues together the parts from reparse_common and reparse_struct

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
import os

from .reparse_common import *
from .win_api import open_file_r, open_file_w, CloseHandle
from .reparse_struct import parse_reparse_point, parse_guid_reparse_point, \
                            create_ms_reparse_point, create_custom_reparse_point

def create_junction(src, dst):
	"""
	Create a junction pointing to src named dst.
	
	Validation is performed in order to determine if any (non-directory) files exist at either
	path.
	:param src: Target of the link
	:type src: str
	:param dst: Newly created link
	:type dst: str
	:raise IOError: If an existing file exists as either :param:`src` or :param:`dst`
	"""
	created_folder = False
	if os.path.isfile(src) or os.path.isfile(dst):
		raise IOError('Junctions only support linking from/to directories!')
	elif not os.path.isdir(dst):
		# Create the folder if it doesn't already exist.
		os.mkdir(dst)
		created_folder = True
	
	# Directory handle opened in a context to allow auto-closing on completion.
	with open_file_w(dst) as handle:
		# Create our reparse point struct
		in_size, in_buf = create_ms_reparse_point(IO_REPARSE_TAG_MOUNT_POINT, src)
		try:
			deviceioctl(handle, FSCTL_SET_REPARSE_POINT, in_buf, in_size, None, 0)
		except:
			# If we created the folder, remove it on exception.
			if created_folder:
				os.rmdir(dst)
			
			# Then reraise the exception
			raise

def create_symlink(src, dst):
	"""
	Create a symbolic link pointing to src named dst.
	:param src: Target of the link
	:type src: str
	:param dst: Newly created link
	:type dst: str
	:raise IOError: If an existing file exists as either :param:`src` or :param:`dst`
	"""
	# Directory handle opened in a context to allow auto-closing on completion.
	with open_file_w(dst) as handle:
		# Create our reparse point struct
		in_size, in_buf = create_ms_reparse_point(IO_REPARSE_TAG_SYMLINK, src)
		deviceioctl(handle, FSCTL_SET_REPARSE_POINT, in_buf, in_size, None, 0)

def read_reparse_point(path):
	"""
	Return a string representing the path to which the reparse point points. The result may be
	either an absolute or relative pathname
	:param path: Filepath
	:type path: str
	:return: Destination
	:rtype: str
	"""
	# Directory handle opened in a context to allow auto-closing on completion.
	with open_file_r(path) as handle:
		# Create our reparse point struct
		out_size, out_buf = create_ms_reparse_point(IO_REPARSE_TAG_RESERVED_ZERO, None)
		deviceioctl(handle, FSCTL_GET_REPARSE_POINT, None, 0, out_buf, out_size)
		reparse_point = parse_reparse_point(out_buf)
		return reparse_point.substitute_name
