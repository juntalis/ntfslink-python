#!/usr/bin/env python
"""
setup.py file for ntfslink module.
"""
from distutils.core import setup
import sys


def get_wrapper(wrapper):
	from os import path
	_mod = False
	import imp
	fp, pathname, description = imp.find_module(
		'__init__', [path.join(path.dirname(__file__),'wrapper',wrapper)]
	)
	if fp is not None:
		try:
			_mod = imp.load_module('__init__', fp, pathname, description)
		finally:
			fp.close()
	return _mod

use_wrapper = 'swig'
supported_wrappers = ['swig','cython']

# Check for wrapper specified in args
if len(sys.argv) > 2:
	last = len(sys.argv) - 1
	check = sys.argv[last].lower()
	if check in supported_wrappers:
		print 'Using wrapper: %s' % check
		use_wrapper = check
		sys.argv = sys.argv[0:last]
else:
	print 'No wrapper set. Using default: SWIG'


wrapper = get_wrapper(use_wrapper)
(ext_module, cmd_class) = wrapper.ext_modules()

setup (name = 'ntfslink',
	version = '1.0',
	author = "Charles Grunwald (Juntalis)",
	author_email = 'cgrunwald@gmail.com',
	description = """ Simple module wrapping some of the Win32 API to allow support for junctions, hard links, and symbolic links. """,
	ext_modules = [ext_module],
	py_modules = wrapper.py_modules(),
	cmdclass = cmd_class,
)

