# encoding: utf-8
"""
__init__.py
ntfslink Package

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""

from . import junctions, supports, symlinks, hardlinks, cyglinks
from .common import passthru

cyglink =  passthru('CygLink', cyglinks)
symlink =  passthru('SymLink', symlinks)
junction = passthru('Junction', symlinks)

__all__ = [
	'junctions', 'junction',
	'symlinks',  'symlink',
	'cyglinks',  'cyglink',
	'hardlinks',
	'supports'
]
