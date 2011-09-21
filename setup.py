#!/usr/bin/env python
"""
setup.py file for junction module.
"""
from distutils.core import setup, Extension

junction_module = Extension(
	'junction._junction',
	sources=['junction/junction.cpp', 'junction/pyjunction.cpp'],
	define_macros=[('_CRT_SECURE_NO_WARNINGS', None)],
	include_dirs=['include'],
	libraries=['advapi32']
)
setup (name = 'junction',
	version = '1.0',
	author = "Charles Grunwald (Juntalis) <cgrunwald@gmail.com>",
	description = """ Simple module wrapping some of the Win32 API to allow support for junctions. """,
	packages=['junction'],
	ext_modules = [junction_module],
	py_modules = ['junction']
)