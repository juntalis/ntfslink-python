#!/usr/bin/env python
"""
setup.py file for ntfslink module.
"""
from distutils.core import setup, Extension

ntfslink_module = Extension(
	'ntfslink._ntfslink',
	sources=['ntfslink/ntfslink.cpp', 'ntfslink/pyntfslink.cpp'],
	define_macros=[('_CRT_SECURE_NO_WARNINGS', None)],
	include_dirs=['include'],
	libraries=['advapi32','Shlwapi']
)
setup (name = 'ntfslink',
	version = '1.0',
	author = "Charles Grunwald (Juntalis) <cgrunwald@gmail.com>",
	description = """ Simple module wrapping some of the Win32 API to allow support for junctions, hard links, and symbolic links. """,
	packages=['ntfslink'],
	ext_modules = [ntfslink_module],
	py_modules = ['ntfslink']
)