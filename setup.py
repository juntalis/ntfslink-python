# encoding: utf-8
from distutils.core import setup
import os, sys

if os.name != 'nt':
	print 'Sorry, this module is made to support Windows. For non-Windows users, use os and os.path.'
	sys.exit(0)

def ntfslink_info():
	import ntfslink
	return ntfslink.__version__, ntfslink.__author__

version, author = ntfslink_info()
setup(
	name='ntfslink',
	version=version,
	url='https://github.com/juntalis/ntfslink-python/',
	license='WTFPL 2.0',
	author=author,
	author_email='ch@rles.grunwald.me',
	description='ctypes-based module providing support for junctions, symbolic links, and hard links',
	long_description='',
	packages=['ntfslink'],
	platforms='nt',
	classifiers=[
		# http://pypi.python.org/pypi?%3Aaction=list_classifiers
		'Development Status :: 1 - Planning',
		# 'Development Status :: 2 - Pre-Alpha',
		# 'Development Status :: 3 - Alpha',
		# 'Development Status :: 4 - Beta',
		# 'Development Status :: 5 - Production/Stable',
		# 'Development Status :: 6 - Mature',
		# 'Development Status :: 7 - Inactive',
		'Intended Audience :: Developers',
		'Intended Audience :: System Administrators',
		'Operating System :: Windows',
		'Programming Language :: Python',
		'Topic :: System :: Systems Administration',
		'Topic :: Utilities'
	]
)
