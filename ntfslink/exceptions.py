# encoding: utf-8
"""
Exception classes used by :mod:`ntfslink`

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""

class InvalidHandleError(Exception):
	""" Raised when a necessary handle contains INVALID_HANDLE_VALUE (-1). """
	
	def __init__(self, descr=None):
		"""
		Initialize a new instance of :class:`InvalidHandleException`.
		:param descr: Optional message parameter.
		:type descr: str | None
		"""
		if descr is None: descr = 'Invalid HANDLE value detected!'
		super(InvalidHandleError, self).__init__(descr)

class BaseInvalidFilePathError(Exception):
	""" Base for :class:`InvalidTargetError` and :class:`InvalidLinkError` """
	
	def __init__(self, filepath, descr, default_descr):
		if descr is None: descr = default_descr
		super(BaseInvalidFilePathError, self).__init__(descr)
		self.filepath = filepath

class InvalidTargetError(BaseInvalidFilePathError):
	""" Raised when an invalid path is specified as the target of a link. """
	
	def __init__(self, filepath, descr=None):
		"""
		Initalize a new instance of :class:`InvalidTargetError`
		:param filepath: Filepath attempted
		:type filepath: str
		:param descr: Error message
		:type descr: str | None
		"""
		super(InvalidTargetError, self).__init__(
			filepath, descr,
			'Invalid target path specified!'
		)

class InvalidLinkError(BaseInvalidFilePathError):
	""" Raised when an invalid path is specified for a target link. """
	
	def __init__(self, filepath, descr=None):
		"""
		Initalize a new instance of :class:`InvalidLinkException`
		:param filepath: Filepath attempted
		:type filepath: str
		:param descr: Error message
		:type descr: str | None
		"""
		super(InvalidLinkError, self).__init__(
			filepath, descr,
			'Invalid link path specified!'
		)

__all__ = [ 'InvalidHandleError', 'InvalidTargetError', 'InvalidLinkError' ]
