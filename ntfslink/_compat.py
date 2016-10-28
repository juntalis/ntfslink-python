# encoding: utf-8
"""
Python/Windows version compatibility utilities
"""
import sys as _sys, functools as _func, operator as _oper, types as _types

#############
# Constants #
#############

# :data:`winver` value calculation.
_build_winvers = lambda versobj: versobj.major * 100 + versobj.minor

# Python version info.
_py_ver = _sys.version_info[:2]

#: A numerical representation of the current Windows OS version.
winvers = _build_winvers(_sys.getwindowsversion()) # type: int

#: Is the current OS Vista or newer?
is_gt_winxp = winvers >= 600

#: Is the current OS Windows 7 or newer?
is_gt_vista = winvers >= 601

#: Python 2.x?
is_py2 = _py_ver[0] == 2

#: Python 2.5?
is_py25 = _py_ver == (2, 5)

#: Python 2.6?
is_py26 = _py_ver == (2, 6)

#: Python 2.7?
is_py27 = _py_ver == (2, 7)

#: >= Python 2.6?
is_gte_py26 = _py_ver >= (2, 6)

#: >= Python 2.7?
is_gte_py27 = _py_ver >= (2, 7)

#: Python 3.x?
is_py3 = _py_ver[0] == 3

#: Python 3.1?
is_py31 = _py_ver == (3, 1)

#: Python 3.2?
is_py32 = _py_ver == (3, 2)

#: Python 3.3?
is_py33 = _py_ver == (3, 3)

#: Python 3.4?
is_py34 = _py_ver == (3, 4)

#: Python 3.5?
is_py35 = _py_ver == (3, 5)

#: >= Python 3.3?
is_gte_py33 = _py_ver >= (3, 3)

#: >= Python 3.4?
is_gte_py34 = _py_ver >= (3, 4)

######################
# Internal Utilities #
######################

#: "No operation" lambda
_noop_func = lambda obj: obj

# Accessor for builtins. Technically unnecessary, but PyCharm will highlight
# the code as an error otherwise.
if isinstance(__builtins__, dict):
	# noinspection PyUnresolvedReferences
	_get_builtin = lambda attr: __builtins__.get(attr)
else:
	_get_builtin = lambda attr: getattr(__builtins__, attr)

def _builtin(*attrs):
	""" Extract one or multiple attributes from :mod:`__builtins__` """
	results = []
	count = len(attrs)
	for attr in attrs:
		results.append(_get_builtin(attr))
	return tuple(results) if count > 1 else results[0]

def _add_doc(obj, doc):
	""" Add documentation to a function. """
	obj.__doc__ = doc

#######################
# Compatibility Shims #
#######################

if is_py3:
	#: String type used internally
	text_type = _builtin('str') # type: str
	
	#: Binary type used internally for comparison operations of structures
	buffer_type = _builtin('bytes') # type: bytes
	
	#: Binary string type
	bytes_type = _builtin('bytes') # type: bytes
	
	#: Types used when testing if an instance is a string
	str_types = _builtin('str'), # type: (str,)
	
	#: Types used when testing if an instance is an integer
	int_types = _builtin('int'), # type: (int,)
	
	#: Pass-through to :func:`functools.reduce` / :func:`reduce` depending on
	#: Python version.
	reduce = _func.reduce
	
	#: Used to coerce a string into a binary string
	encode_bytes = lambda data: data.encode() \
	               if isinstance(data, str) else \
	               bytes_type(data) # type: (T) -> str
	
	#: Used to coerce a binary string into a string
	decode_bytes = lambda data: data.decode() \
	               if isinstance(data, bytes_type) else \
	               str(data) # type: (T) -> str
	
	# Used internally to access a method's underlying function
	_meth_func = '__func__'
	
	#: Grab the underlying function of a bound method.
	get_bound_method_function = lambda obj: getattr(obj, _meth_func, None) # type: (method) -> function
	
	#: Grab the underlying function of an unbound method.
	get_unbound_method_function = _noop_func # type: (method) -> function
	
	#: Grab the underlying function of a method
	get_method_function = lambda method: get_bound_method_function(method) \
	                      if isinstance(method, _types.MethodType) else \
	                      get_unbound_method_function(method)
	
	# Used internally for executing code in a namespace
	exec_ = _builtin('exec')
	
	def reraise(tp, value, tb=None):
		if value is None:
			value = tp()
		if value.__traceback__ is not tb:
			raise value.with_traceback(tb)
		raise value
	
else:
	#: String type used internally
	text_type = _builtin('unicode') # type: type
	
	#: Binary type used internally for comparison operations of structures
	buffer_type = _builtin('buffer') # type: type
	
	#: Binary string type
	bytes_type = _builtin('str') # type: type
	
	#: Types used when testing if an instance is a string
	str_types = _builtin('basestring'), # type: (type,)
	
	#: Types used when testing if an instance is an integer
	int_types = _builtin('int', 'long') # type: (type,)
	
	#: Pass-through to :func:`functools.reduce` / :func:`reduce` depending on
	#: Python version.
	reduce = _builtin('reduce')
	
	#: Used to coerce a string into a binary string
	decode_bytes = lambda data: str(data) # type: (T) -> str
	
	#: Used to coerce a binary string into a string
	decode_bytes = lambda data: str(data) # type: (T) -> str
	
	# Used internally to access a method's underlying function
	_meth_func = 'im_func'
	
	#: Grab the underlying function of a bound method.
	get_bound_method_function = _oper.attrgetter(_meth_func) # type: (method) -> function
	
	#: Grab the underlying function of an unbound method
	get_unbound_method_function = get_bound_method_function
	
	#: Grab the underlying function of a method
	get_method_function = get_bound_method_function
	
	# noinspection PyProtectedMember
	def exec_(_code_, _globs_=None, _locs_=None):
		""" Used internally for executing code in a namespace."""
		if _globs_ is None:
			frame = _sys._getframe(1)
			_globs_ = frame.f_globals
			if _locs_ is None:
				_locs_ = frame.f_locals
			del frame
		elif _locs_ is None:
			_locs_ = _globs_
		exec('exec _code_ in _globs_, _locs_')
	
	exec_("""def reraise(tp, value, tb=None):
	raise tp, value, tb
""")

# noinspection PyMissingOrEmptyDocstring
def raise_from(value, from_value):
	raise value

if is_py32:
	del raise_from
	exec_("""def raise_from(value, from_value):
    if from_value is None:
        raise value
    raise value from from_value
""")
elif is_gte_py33:
	del raise_from
	exec_("""def raise_from(value, from_value):
    raise value from from_value
""")

if is_gte_py34:
	# Pass-thru wraps to functools
	wraps = _func.wraps
else:
	def wraps(wrapped, assigned=_func.WRAPPER_ASSIGNMENTS,
	    updated=_func.WRAPPER_UPDATES):
		def wrapper(f):
			f = _func.wraps(wrapped, assigned, updated)(f)
			f.__wrapped__ = wrapped
			return f
		
		return wrapper
	
	_func.update_wrapper(wraps, _func.wraps)

def with_metaclass(meta, *bases):
	""" Create a base class with a metaclass. """
	
	# This requires a bit of explanation: the basic idea is to make a dummy
	# metaclass for one level of class instantiation that replaces itself with
	# the actual metaclass.
	class metaclass(meta):
		def __new__(cls, name, this_bases, d):
			return meta(name, bases, d)
	
	return type.__new__(metaclass, 'temporary_class', (), { })

def add_metaclass(metaclass):
	""" Class decorator for creating a class with a metaclass. """
	def wrapper(cls):
		orig_vars = cls.__dict__.copy()
		slots = orig_vars.get('__slots__')
		if slots is not None:
			if isinstance(slots, str):
				slots = [slots]
			for slots_var in slots:
				orig_vars.pop(slots_var)
		orig_vars.pop('__dict__', None)
		orig_vars.pop('__weakref__', None)
		return metaclass(cls.__name__, cls.__bases__, orig_vars)
	return wrapper

_add_doc(get_bound_method_function, """
Grab the underlying function of a bound method.
:param obj: Target bound method
:type obj: method
:return: Method's underlying function
:rtype: function
""")

_add_doc(get_unbound_method_function, """
Grab the underlying function of an unbound method.
:param obj: Target unbound method
:type obj: method
:return: Method's underlying function
:rtype: function
""")

_add_doc(get_method_function, """
Grab the underlying function of a method, regardless of whethere's it's
currently bound to an instance or not.
:param obj: Target method
:type obj: method
:return: Method's underlying function
:rtype: function
""")

_add_doc(reraise, """
Reraise an exception.
:param tp: Exception type or instance
:type tp: type | None
:param value: Optional exception value.
:param tb: Optional traceback instance.
:type tb: traceback | None
""")

_add_doc(raise_from, """
Exception chaining mechanism.
:param value: Newly raised exception instance
:type value: T <= Exception
:param from_value: Optional predecessor exception instance
:type value: T <= Exception | None
""")

del _py_ver, _build_winvers, _get_builtin, _builtin
