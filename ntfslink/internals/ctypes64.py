"""
ctypes64.py

Just a shim to import ctypes with some corrections. (From ctypesgen)
"""

from ctypes import *
import ctypes

_int_types = (c_int16, c_int32)
if hasattr(ctypes, 'c_int64'):
	# Some builds of ctypes apparently do not have c_int64
	# defined; it's a pretty good bet that these builds do not
	# have 64-bit pointers.
	_int_types += (c_int64,)
for t in _int_types:
	if sizeof(t) == sizeof(c_size_t):
		c_ptrdiff_t = t

del _int_types

class c_void(Structure):
	# c_void_p is a buggy return type, converting to int, so
	# POINTER(None) == c_void_p is actually written as
	# POINTER(c_void), so it can be treated as a real pointer.
	_fields_ = [('dummy', c_int)]

def POINTER(obj):
	p = ctypes.POINTER(obj)

	# Convert None to a real NULL pointer to work around bugs
	# in how ctypes handles None on 64-bit platforms
	if not isinstance(p.from_param, classmethod):
		def from_param(cls, x):
			if x is None:
				return cls()
			else:
				return x
		p.from_param = classmethod(from_param)

	return p

# Some quick overriding declarations.
c_void_p = POINTER(c_void)

# As of ctypes 1.0, ctypes does not support custom error-checking
# functions on callbacks, nor does it support custom datatypes on
# callbacks, so we must ensure that all callbacks return
# primitive datatypes.
#
# Non-primitive return values wrapped with UNCHECKED won't be
# typechecked, and will be converted to c_void_p.
def UNCHECKED(typ):
	if hasattr(typ, '_type_') and isinstance(typ._type_, str) and typ._type_ != 'P':
		return typ
	else:
		return c_void_p

#noinspection PyUnresolvedReferences
from ctypes.wintypes import *
