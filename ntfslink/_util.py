# encoding: utf-8
"""
_shared.py
Contains general non-platform related utilities that are used
internally within the module.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
import sys as _sys
from functools import wraps as _wraps


def once(func):
	"""
	Fires once, then returns the same result for every call after that.

	:param function func: The decorated function
	:rtype: function
	"""
	func._lazycall = (False, None,)

	# noinspection PyProtectedMember
	@_wraps(func)
	def lazy_deco(*args, **kwargs):
		if not func._lazycall[0]:
			func._lazycall = (True, func(*args, **kwargs),)
		return func._lazycall[1]
	return lazy_deco


def memoize(func):
	"""
	From the Python Decorator Library (http://wiki.python.org/moin/PythonDecoratorLibrary):
	Cache the results of a function call with specific arguments. Note that this decorator ignores **kwargs.

	:param function func: The decorated function
	:rtype: function
	"""
	cache = func._cache = dict()

	@_wraps(func)
	def memoizer(*args, **kwargs):
		if args not in cache:
			cache[args] = func(*args, **kwargs)
		return cache[args]
	return memoizer



