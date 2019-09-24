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
import operator
from ._compat import wraps as _wraps, reduce as _reduce

###########
# Globals #
###########

#: Locally cached reference to builtin_function_or_method type.
builtin_function = type(ord)

##############
# Decorators #
#############

def once(func):
	"""
	Fires once, then returns the same result for every call after that.

	:param function func: The decorated function
	:rtype: function
	"""
	call_result = [False]
	
	# noinspection PyProtectedMember,PyMissingOrEmptyDocstring
	@_wraps(func)
	def once_deco(*args, **kwargs):
		if not call_result[0]:
			call_result[0] = True
			call_result.append(func(*args, **kwargs))
		return call_result[1]
	
	return once_deco

def memoize(func):
	"""
	From the Python Decorator Library (http://wiki.python.org/moin/PythonDecoratorLibrary):
	Cache the results of a function call with specific arguments. Note that this decorator ignores **kwargs.

	:param function func: The decorated function
	:rtype: function
	"""
	cache = dict()
	
	# noinspection PyMissingOrEmptyDocstring
	@_wraps(func)
	def memoizer(*args, **kwargs):
		if args not in cache:
			cache[args] = func(*args, **kwargs)
		return cache[args]
	
	return memoizer

###############################
# Utility Classes & Functions #
###############################

def nameof(obj, default=None):
	"""
	Determine the name of a class/function/whatever and return it. If no
	name can be resolved, return the ``default`` parameter.
	:param obj: Object to get the name of.
	:param default: Defaul value to return when no name is detected.
	:return: Name of object or ``default``.
	:rtype: str | None
	"""
	return getattr(obj, '__name__', default)

def delegate_property(*attrs):
	"""
	Define an instance property that is delegated to self.attr1[.attr2.attr3...]

	Example::

		>>> class MyClass(object):
		...
		...     def __init__(self, obj):
		...         self.obj = obj
		...
		...     foo = delegate_property('obj', '__class__')
		...
		>>> a = MyClass(obj=list())
		>>> a.foo
		<class 'list'>
		>>> a.obj.__class__
		<class 'list'>

	:param str attrs: Nested attributes to access
	:return: Class property that delegates to the nested attr.
	:raise ValueError: if called without any attr names
	"""
	if not attrs:
		raise ValueError('delegate_property expects at least one attr name!')
	return property(operator.attrgetter('.'.join(attrs)))

# Used within reduce to call each callable on the result of the previous
_chained = lambda value, _callable: _callable(value)

class CallChain(object):
	"""
	Represents a chain of function/method/whatever calls, executed left to
	right.
	"""
	__slots__ = ('_funcs',)
	
	def __init__(self, *callables):
		"""
		Initializer
		:param callables: Function collection
		:type callables: tuple[callable]
		"""
		self._funcs = list(callables)
	
	def chain(self, *callables):
		"""
		Adds additional callables to the chain.
		:param callables: Function collection
		:type callables: tuple[callable]
		:return: self
		:rtype: CallChain
		"""
		self._funcs.extend(list(callables))
		return self
	
	def __call__(self, value):
		"""
		Return result of passing 'value' through chained callables.
		:param value: Parameter
		:type value: any
		:return: The result after all functions have been called.
		:rtype: any
		:raises ValueError: when the chain is empty.
		"""
		if len(self._funcs) == 0:
			raise ValueError('Empty call chain called!')
		
		return _reduce(_chained, self._funcs, value)

def chain(*callables):
	"""
	Creates a :class:`CallChain` instance with the given callables.
	:param callables: Function collection
	:type callables: tuple[callable]
	:return: self
	:rtype: CallChain
	"""
	return CallChain(*callables)

