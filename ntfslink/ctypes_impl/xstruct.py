# encoding: utf-8
"""
Utility wrappers for :mod:`struct`.

Currently unused until I can come up with a good way to do variable
sized fields.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
import struct, operator, copy
from collections import OrderedDict as odict

from .._util import memoize
from .._compat import with_metaclass, reduce as _reduce, encode_bytes

#############
# Internals #
#############

_second = operator.itemgetter(1)
_calcsize = memoize(struct.calcsize)
_sizegetter = operator.attrgetter('size')
_formatgetter = operator.attrgetter('format')
_countergetter = operator.attrgetter('counter')
_exclude_first = operator.itemgetter(slice(1, None))
_field_sorter = lambda pair: _countergetter(_second(pair))
_format_joiner = lambda fields: ''.join(map(_formatgetter, fields))

##################
# Public Classes #
##################

def _expand_format(format):
	result = ''
	chars = list(format)
	while chars:
		ch = chars.pop(0)
		if ch.isdigit():
			while chars and chars[0].isdigit():
				ch += chars.pop(0)
			num = int(ch)
			ch = chars.pop(0)
			if ch is None:
				raise ValueError('Expected a format char to follow {}'.format(num))
			ch = ch * num
		result += ch
	return result

class Field(object):
	""" Represents an individual field on a structure """
	
	__slots__ = ('name', 'format', 'counter', 'size', 'count', 'offset', )
	
	#:Tracks each time a StructField instance is created. Used to retain order.
	_counter = 0
	_format_count_cache = dict()
	
	def __init__(self, format):
		"""
		StructField(fmt) --> compiled struct object
		
		Return a new StructField object which writes and reads binary data
		according to the format string fmt. See help(struct) for more on
		format strings.
		"""
		# Increase the creation counter, and save our local copy.
		self.counter = self._increment_count()
		
		# default name to `None`
		self.name = None
		
		# Default field offset to 0
		self.offset = 0
		
		# Simplify the format string and store it.
		self.format = _expand_format(format)
		
		# Store size and count
		self.size = self.get_format_size(self.format)
		self.count = self.get_format_count(self.count)
	
	@classmethod
	def _increment_count(cls):
		""" Internally used - increments field counter. """
		result = cls._counter
		cls._counter += 1
		return result

	@classmethod
	def get_format_size(cls, format):
		"""
		
		:param format:
		:type format: str
		:return:
		:rtype: int
		"""
		return _calcsize(format)

	@classmethod
	def get_format_count(cls, format):
		cache = cls._format_count_cache
		count = cache.get(format, None)
		if count is None:
			size = cls.get_format_size(format)
			data = encode_bytes('\0' * size)
			values = struct.unpack(format, data)
			count = cache[format] = len(values)
		return count
	
	def __deepcopy__(self, memo):
		result = copy.copy(self)
		memo[id(self)] = result
		return result

def _get_fields(attrs):
	"""
	Extract all field instances from the class attributes dict
	:param attrs: Class attributes
	:type attrs: dict
	:return: generator of fields
	:rtype: [(str,Field), (str,Field)]
	"""
	class_attrs = tuple(attrs.items())
	for name, field in class_attrs:
		if isinstance(field, Field):
			attrs.pop(name)
			yield (name, field)

def _set_field_offset(size, field):
	field.offset = size
	return size + field.size

class StructMetaclass(type):
	""" Metaclass for :class:`BaseStruct`-based classes. """
	
	def __new__(mcs, name, bases, attrs):
		# Cache references
		super_new = super(StructMetaclass, mcs).__new__
		
		# Verify valid parents
		parents = [ base for base in bases if isinstance(base, StructMetaclass) ]
		if not parents:
			return super_new(mcs, name, bases, attrs)
		
		# Collect fields from current class.
		size, format = 0, ''
		fields = sorted(_get_fields(attrs), key=_field_sorter)
		if len(fields) > 0:
			attrs['declared_fields'] = odict(fields)
			attrs['declared_format'] = format = _format_joiner(map(_second, fields))
			attrs['declared_size'] = size = sum(_sizegetter(_second(f)) for f in fields)
		
		# Initialize the new class.
		newcls = super_new(mcs, name, bases, attrs)
		
		# Walk through the MRO.
		bases = _exclude_first(newcls.__mro__)
		inherited_size, inherited_fields, inherited_format = 0, [], ''
		for base in reversed(bases):
			# Identify Struct classes with declared fields
			declared_fields = getattr(base, 'declared_fields', None)
			if declared_fields is None: continue
			inherited_fields.extend(declared_fields.items())
			inherited_size += getattr(base, 'declared_size', 0)
			inherited_format += getattr(base, 'declared_format', 0)
		
		# Process inherited fields and sizes
		if inherited_fields:
			size += inherited_size
			offset = inherited_size
			format = inherited_format + format
			fields = inherited_fields + fields
			newcls.inherited_size = inherited_size
			newcls.inherited_fields = inherited_fields
			for field_name, field_inst in fields:
				field_inst.offset = offset
				offset += field_inst.size
		
		newcls.size = size
		newcls.format = format
		newcls.fields = odict(fields)
		return newcls

class BaseStruct(Field):
	"""
	Abstract base struct class
	:type field: list[StructField]
	:type declared_fields: list[StructField]
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
		super(BaseStruct, self).__init__(self.format)

class Struct(with_metaclass(StructMetaclass, BaseStruct)):
	""" Extended struct """

class ReparsePointHeader(Struct):
	""" Header structure definition for MS reparse points """
	tag = Field('I')
	length = Field('H')
	reserved = Field('H')

class ReparsePointGUIDHeader(ReparsePointHeader):
	""" Header structure definition for third-party reparse points """
	guid = Field('2Q')

class MountPointBuffer(Struct):
	""" Buffer structure definition for mount points & junctions (not including
	    path buffer) """
	substitute_offset = Field('H')
	substitute_length = Field('H')
	print_offset = Field('H')
	print_length = Field('H')

class SymbolicLinkBuffer(MountPointBuffer):
	""" Buffer structure definition for symbolic links (not including path
	    buffer)"""
	flags = Field('I')
