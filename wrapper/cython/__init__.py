#!/usr/bin/python
from distutils.core import setup, Extension

def ext_modules():
	from distutils.extension import Extension as Extension
	ntfslink_module = None
	cmd_class = {}
	try:
		from Cython.Distutils import build_ext
		from Cython.Distutils import Extension as ext
		cmd_class['build_ext'] = build_ext
		ntfslink_module = ext(
			'ntfslink',
			sources=['src/ntfslink.cpp','wrapper/cython/ntfslink.pyx'],
			define_macros=[('_CRT_SECURE_NO_WARNINGS', None)],
			include_dirs=['src'],
			libraries=['advapi32','Shlwapi'],
			pyrex_cplus=True,
		)

		cmd_class['build_ext'].user_options.append('pyrex-cplus')

	except ImportError:
		from distutils.command.build_ext import build_ext
		print "cython not found, using previously-cython'd .cpp file."
		cmd_class['build_ext'] = build_ext
		ntfslink_module = Extension(
			'ntfslink',
			sources=['src/ntfslink.cpp', 'wrapper/cython/ntfslink.cpp'],
			define_macros=[('_CRT_SECURE_NO_WARNINGS', None)],
			include_dirs=['src'],
			libraries=['advapi32','Shlwapi']
		)
	return (ntfslink_module, cmd_class)

def py_modules():
	return []