#!/usr/bin/env python
from wrapper import *
"""
Generate distutils Extension class for the SWIG wrapper.
"""

def ext_modules():
	from distutils.core import Extension
	from distutils.command.build_ext import build_ext
	ntfslink_module = None
	exe = program('swig')
	cmd_class = {}
	cmd_class['build_ext'] = build_ext
	if exe:
		ntfslink_module = Extension(
			'_ntfslink',
			sources=['src/ntfslink.cpp','wrapper/swig/ntfslink.i'],
			define_macros=[('_CRT_SECURE_NO_WARNINGS', None)],
			include_dirs=['src'],
			libraries=['advapi32','Shlwapi'],
			swig=exe,
			swig_opts=['-O', '-builtin', '-c++','-outdir','.'],
		)
	else:
		ntfslink_module = Extension(
			'_ntfslink',
			sources=['ntfslink/ntfslink.cpp', 'wrapper/swig/ntfslink_wrap.cpp'],
			define_macros=[('_CRT_SECURE_NO_WARNINGS', None)],
			include_dirs=['src'],
			libraries=['advapi32','Shlwapi']
		)
	return (ntfslink_module, cmd_class)


def py_modules():
	return ['ntfslink']
