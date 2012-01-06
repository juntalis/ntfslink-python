from distutils.extension import Extension
from distutils.core import setup
import os, sys

if os.name != 'nt':
	print 'Sorry, this module is made to support Windows. For non-Windows users, use os and os.path.'
	sys.exit(0)

if sys.getwindowsversion()[0] < 6:
	print 'Sorry, your version of Windows does not support symbolic links or junctions.'
	sys.exit(0)

setup (name = 'ntfslink',
	version = '1.2',
	author = "Charles Grunwald (Juntalis)",
	author_email = 'cgrunwald@gmail.com',
	description = """ Simple module wrapping some of the Win32 API to allow support for junctions, hard links, and symbolic links. """,
	ext_modules = [Extension(
		'ntfslink',
		['ntfslink/ext/ntfslinkmodule.c','ntfslink/ext/ntfslink.c'],
		define_macros=[('_CRT_SECURE_NO_WARNINGS', None)],
		libraries=['advapi32'],
		include_dirs=['src'],
	)]
)
