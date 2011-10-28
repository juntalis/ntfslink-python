from distutils.extension import Extension
from distutils.core import setup
import os, sys

if 'install' in sys.argv:
	print 'Probably not a good idea.'
	sys.exit(0)

setup (name = 'ntcyg',
	version = '0.2',
	author = "Charles Grunwald (Juntalis)",
	author_email = 'cgrunwald@gmail.com',
	description = """ blahblah """,
	ext_modules = [Extension(
		'ntcyg',
		['ntcyg.c'],
		define_macros=[('_CRT_SECURE_NO_WARNINGS', None)],
		libraries=['advapi32'],
	)]
)
