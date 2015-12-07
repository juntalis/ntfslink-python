# encoding: utf-8
"""
cutil.py
I wanted a clean way to declare the external function call prototypes
with the appropriate TCHAR suffix. (A or W depending on whether we're
using unicode) In the end, I kind of went a bit overboard and
implemented some unncessary shorcuts to the ctypes paramflags
functionality.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
import ctypes
from .compat import TCHAR_SUFFIX

def deref(addr, typ):
	""" Dereference a numerical address into a ctypes object """
	return ctypes.cast(addr, ctypes.POINTER(typ)).contents

def enum(name, **named):
	class Enum(object): pass
	named['__keys__'] = dict([(o[1],o[0]) for o in named.items()])
	getitem = lambda self, item: self.__keys__[item]
	named['__getitem__'] = classmethod(getitem)
	named['__name__'] = name
	return type(name, (Enum,), named)()

ArgFlags = enum('ArgFlags', In=1, Out=2, InOpt=1)

class CParamEx(object):
	def __init__(self, ctype, flag, *args):
		if flag is None:
			#noinspection PyUnresolvedReferences
			flag = ArgFlags.In
		flag = [flag]
		if len(args) > 0: flag += list(args)
		self.paramflag = tuple(flag)
		self.ctype = ctype

# Using the verbage from http://msdn.microsoft.com/en-us/library/hh916383.aspx

def In(ctype, *args):
	""" Parameter is input to the called function. """
	return ctype \
		if isinstance(ctype, CParamEx) else \
		CParamEx(ctype, ArgFlags.In, *args)

def Out(ctype, *args):
	""" Parameter is output to caller. """
	return ctype \
		if isinstance(ctype, CParamEx) else \
		CParamEx(ctype, ArgFlags.Out, *args)

def InOpt(ctype, *args):
	""" Parameter is optional. """
	return ctype \
		if isinstance(ctype, CParamEx) else \
		CParamEx(ctype, ArgFlags.InOpt, *args)

def _ctypename(typestr):
	typestr = str(typestr).replace('c_', '').replace('LP_', 'LP').upper()
	return 'LP' + typestr.replace('CHAR_P', 'STR') \
		if 'CHAR_P' in typestr else \
		typestr

def _argstr(ctype, paramflag):
	flaglen = len(paramflag)
	cname = _ctypename(ctype.__name__)
	annotation = ArgFlags[paramflag[0]]
	result = '{0} {1}'.format(annotation, cname)
	if flaglen > 1:
		result += ' ' + paramflag[1]
	if flaglen > 2:
		result += '=' + repr(paramflag[2])
	return result

class CFuncExCallable(object):
	""" Pointless overkill to implement our own repr() and str() """
	def __init__(self, func, declstr):
		self._func_ = func
		self._decl_ = declstr

	def __call__(self, *args, **kwargs):
		try:
			return self._func_(*args, **kwargs)
		except:
			print repr(self)
			raise

	def __repr__(self):
		return '<%s at 0x08%X>' % (self._decl_, id(self._func_))

	def __str__(self):
		return self._decl_

class CFuncEx(object):
	""" Utility wrapper class. Processes a declaration such as:

	GetVolumePathName = kernel32.GetVolumePathName(BOOL, PTSTR, Out(PTSTR), DWORD)

	And depending on whether or not we're
	 """
	def __init__(self, dll, name, functype):
		self._name_ = name
		self._dll_ = dll
		self._type_ = functype

	def __call__(self, restype, *args, **kwargs):
		uses_tchar = hasattr(restype, '_tchar_')
		proto_args = []
		proto_parts = [ restype ]
		argstrs = []
		if len(args) > 0:
			paramflags = []
			for arg in list(args):
				if isinstance(arg, CParamEx):
					ctype = arg.ctype
					paramflag = arg.paramflag
				else:
					#noinspection PyUnresolvedReferences
					ctype = arg
					paramflag = (ArgFlags.In,)
				if not uses_tchar and hasattr(ctype, '_tchar_'):
					uses_tchar = True
				proto_parts.append(ctype)
				paramflags.append(paramflag)
				argstrs.append(_argstr(ctype, paramflag))
			proto_args.append(tuple(paramflags))
		prototype = self._type_(*tuple(proto_parts))

		if uses_tchar: self._name_ += TCHAR_SUFFIX
		proto_args = [ (self._name_, self._dll_,) ] + proto_args
		return CFuncExCallable(
			prototype(*tuple(proto_args)),
			'{0} {1}({2})'.format(
				_ctypename(restype.__name__),
				self._name_,
				', '.join(argstrs)
			)
		)

class BaseDLLEx(object):
	""" Base utility wrapper. Essentially, this """
	def __init__(self, dll, functype):
		self._dll_ = dll
		self._functype_ = functype

	def __getattr__(self, item):
		return CFuncEx(self._dll_, item, self._functype_)

class CDLLEx(BaseDLLEx):
	""" A utility wrapper around ctypes.CDLL. """
	def __init__(self, *args, **kwargs):
		super(CDLLEx, self).__init__(ctypes.CDLL(*args, **kwargs), ctypes.CFUNCTYPE)

class WinDLLEx(BaseDLLEx):
	""" A utility wrapper around ctypes.WinDLL. """
	def __init__(self, *args, **kwargs):
		super(WinDLLEx, self).__init__(ctypes.WinDLL(*args, **kwargs), ctypes.WINFUNCTYPE)

# Store a local copy of ctypes.WinError before we shadow the builtin.
_RealWinError = ctypes.WinError

def WinError(code=None, descr=None, tmpl=None):
	""" Shadow ctypes.WinError to add the ability to specify a format string. """
	err = _RealWinError(code, descr)
	err.message = err.strerror
	if tmpl is not None:
		assert(isinstance(tmpl, basestring))
		err.strerror = tmpl.format(
			args=err.args,
			errno=err.errno,
			message=err.message,
			winerror=err.winerror
		)
	return err

__all__ = [ 'enum', 'WinDLLEx', 'CDLLEx', 'In', 'Out', 'InOpt', 'WinError' ]
