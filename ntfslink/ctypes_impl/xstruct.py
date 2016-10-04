# encoding: utf-8
"""
Utility wrappers for :mod:`struct`.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
import struct, operator, copy
from collections import OrderedDict as odict

from .._util import memoize
from .._compat import with_metaclass, reduce as _reduce

#############
# Internals #
#############

_second = operator.itemgetter(1)
_calcsize = memoize(struct.calcsize)
_sizegetter = operator.attrgetter('size')
_formatgetter = operator.attrgetter('format')
_countergetter = operator.attrgetter('counter')
_field_sorter = lambda pair: _countergetter(_second(pair))
_format_joiner = lambda fields: ''.join(map(_formatgetter, fields))

##################
# Public Classes #
##################

class FieldA(object):
	""" Represents an individual field on a structure """
	
	__slots__ = ('format', 'counter', 'size', 'count', 'offset')
	
	#:Tracks each time a StructField instance is created. Used to retain order.
	_counter = 0
	
	def __init__(self, *fmtchars):
		"""
		StructField(fmt) --> compiled struct object
		
		Return a new StructField object which writes and reads binary data
		according to the format string fmt. See help(struct) for more on
		format strings.
		"""
		# Increase the creation counter, and save our local copy.
		self.counter = FieldA._counter
		FieldA._counter += 1
		
		# Default field offset to 0
		self.offset = 0
		
		# Count the number of characters in order to predict how many values
		# are associated with this field.
		self.count = len(fmtchars)
		
		# Store the format string
		self.format = ''.join(fmtchars)
		
		# Store size
		self.size = _calcsize(self.format)
	
	def __deepcopy__(self, memo):
		result = copy.copy(self)
		memo[id(self)] = result
		return result

class FieldB(struct.Struct):
	""" Represents an individual field on a structure """
	
	#: Tracks each time a StructField instance is created. Used to retain order.
	_counter = 0
	
	def __init__(self, *fmtchars):
		"""
		StructField(fmt) --> compiled struct object
		
		Return a new StructField object which writes and reads binary data
		according to the format string fmt. See help(struct) for more on
		format strings.
		"""
		
		# Default field offset to 0
		self.offset = 0
		
		# Count the number of characters in order to predict how many values
		# are associated with this field.
		self.count = len(fmtchars)
		
		# Store the format string
		fmt = ''.join(fmtchars)
		
		# Increase the creation counter, and save our local copy.
		self.counter = FieldB._counter
		FieldB._counter += 1
		
		# Call :class:`struct.Struct` constructor
		super(FieldB, self).__init__(fmt)
	
	@property
	def format(self):
		"""
		struct format string
		:type: str
		"""
		return self._fmt
	
	def __deepcopy__(self, memo):
		result = copy.copy(self)
		memo[id(self)] = result
		return result

FieldImpl = FieldA

def switch_field_impl():
	global FieldImpl
	FieldImpl = FieldB if FieldImpl is FieldA else FieldA

def _get_fields(attrs):
	"""
	Extract all field instances from the class attributes dict
	:param attrs: Class attributes
	:type attrs: dict
	:return: generator of fields
	:rtype: [(str,FieldImpl), (str,FieldImpl)]
	"""
	for name, field in list(attrs.items()):
		if isinstance(field, FieldImpl):
			attrs.pop(name)
			yield (name, field)

def _set_field_offset(size, field):
	field.offset = size
	return size + field.size

class StructMetaclass(type):
	""" Metaclass for :class:`BaseStruct`-based classes. """
	
	def __new__(mcs, name, bases, attrs):
		# Collect fields from current class.
		fields = sorted(_get_fields(attrs), key=_field_sorter)
		if len(fields) > 0:
			attrs['declared_fields'] = odict(fields)
		
		# Initialize the new class.
		newcls = super(StructMetaclass, mcs).__new__(mcs, name, bases, attrs)
		
		# Walk through the MRO.
		size = 0
		fields = odict()
		mro = list(reversed(newcls.__mro__))
		for base in mro:
			# Collect fields from base class.
			declared_fields = getattr(base, 'declared_fields', None)
			if declared_fields is not None:
				size = _reduce(_set_field_offset, declared_fields.values(), size)
				fields.update(declared_fields)
		
		newcls.declared_fields = fields
		newcls._fmt = _format_joiner(fields.values())
		return newcls

class BaseStruct(FieldImpl):
	"""
	Abstract base struct class
	:type field: list[StructFieldImpl]
	:type declared_fields: list[StructFieldImpl]
	"""
	
	# noinspection PyUnresolvedReferences
	def __init__(self, data=None, **kwargs):
		"""
		:param data:
		:type data:
		:param kwargs:
		:type kwargs:
		"""
		self._bound_fields_cache = {}
		self.fields = copy.deepcopy(self.declared_fields)
		super(BaseStruct, self).__init__(self._fmt)

class Struct(with_metaclass(StructMetaclass, BaseStruct)):
	""" Extended struct """

class ReparsePointHeader(Struct):
	""" Header structure definition for MS reparse points """
	tag = FieldImpl('I')
	length = FieldImpl('H')
	reserved = FieldImpl('H')

class ReparsePointGUIDHeader(ReparsePointHeader):
	""" Header structure definition for third-party reparse points """
	guid = FieldImpl('Q', 'Q')

class MountPointBuffer(Struct):
	""" Buffer structure definition for mount points & junctions (not including
	    path buffer) """
	substitute_offset = FieldImpl('H')
	substitute_length = FieldImpl('H')
	print_offset = FieldImpl('H')
	print_length = FieldImpl('H')

class SymbolicLinkBuffer(MountPointBuffer):
	""" Buffer structure definition for symbolic links (not including path
	    buffer)"""
	flags = FieldImpl('I')
