#!/usr/bin/env cython
r"""
TODO: Description

"""

__all__ = ['cygroot', 'islink', 'readlink', 'symlink', 'cygtowin']
from cpython.string cimport PyString_FromString, PyString_Check, PyString_FromStringAndSize
from libc.stdlib cimport malloc, free
from libc.string cimport strlen
from libc.stdio cimport const_char, FILE, SEEK_END, SEEK_SET, fseek, ftell, feof, fopen, fclose, fread, fwrite
import re

cdef extern from *:
	int fgetc (
		FILE * stream
	)

	int _fgetc_nolock( 
		FILE *stream 
	)
	size_t _fread_nolock( 
		void *buffer,
		size_t size,
		size_t count,
		FILE *stream 
	)
	int _fseek_nolock( 
		FILE *stream,
		long offset,
		int origin 
	)
	#int _fseeki64_nolock( 
	#	FILE *stream,
	#	__int64 offset,
	#	int origin 
	#)
	long _ftell_nolock( 
		FILE *stream 
	)
	#__int64 _ftelli64_nolock( 
	#	FILE *stream 
	#)
	int _fclose_nolock( 
		FILE *stream 
	)
	size_t nlfgetc = _fgetc_nolock
	size_t nlfread = _fread_nolock
	
	int putc (int character, FILE * stream )

DEF MAX_PATH = 260
from windows cimport HANDLE, ULONG, LPCTSTR, LPTSTR, DWORD, LPDWORD, PVOID, LPDWORD, LPBYTE, LONG, BOOL, USHORT, LPWSTR, LPCWSTR, WCHAR
cdef extern from *:
	# Registry stuff
	ctypedef HANDLE HKEY
	ctypedef HKEY* PHKEY
	ctypedef ULONG REGSAM
	
	# Registry-specific declarations.
	LONG __stdcall RegGetValue(
		HKEY hkey,
		LPCTSTR lpSubKey,
		LPCTSTR lpValue,
		DWORD dwFlags,
		LPDWORD pdwType,
		PVOID pvData,
		LPDWORD pcbData
	)

	LONG __stdcall RegQueryValueEx(
		HKEY hkey,
		LPCTSTR lpValueName,
		LPDWORD lpReserved,
		LPDWORD lpType,
		LPBYTE lpData,
		LPDWORD lpcbData
	)

	LONG __stdcall RegOpenKeyEx(
		HKEY hKey,
		LPCTSTR lpSubKey,
		DWORD ulOptions,
		REGSAM samDesired,
		PHKEY phkResult
	)

	LONG __stdcall RegCloseKey(
		HKEY hKey
	)

	# Preset HKEYs
	HKEY HKEY_CURRENT_USER
	HKEY HKEY_LOCAL_MACHINE

	# Preset flags
	DWORD REG_DWORD
	DWORD REG_SZ
	REGSAM KEY_READ
	LONG ERROR_SUCCESS

cdef extern from "stdlib.h":
	size_t wcstombs(
		char *mbstr,
		LPCWSTR wcstr,
		size_t count
	)

cdef extern from "string.h":
	size_t wcslen(
		LPCWSTR str
	)

# Just to make things a bit prettier.
ctypedef char* tstring

ctypedef int bool
cdef bool true = (1 == 1)
cdef bool false = not true

# Get SZ value from registry.
cdef tstring szvalue(HKEY hKeyRoot, tstring hKeyName, tstring hKeyValue = NULL, DWORD szLength = MAX_PATH):
	cdef char* lszValue = NULL
	cdef HKEY hKey = NULL
	cdef HKEY rootHKEY = hKeyRoot
	cdef LONG returnStatus = ERROR_SUCCESS
	cdef DWORD dwType = REG_SZ
	cdef DWORD dwSize = szLength
	returnStatus = RegOpenKeyEx(rootHKEY, hKeyName, 0L, KEY_READ, & hKey)
	if returnStatus == ERROR_SUCCESS:
		lszValue = <tstring> malloc(sizeof(char) * <size_t> (szLength+1))
		if lszValue == NULL:
			print 'Fatal error: Could not allocate buffer for return value.'
			return NULL
		returnStatus = RegQueryValueEx(hKey, hKeyValue, NULL, & dwType, <LPBYTE> lszValue, & dwSize)
		if returnStatus != ERROR_SUCCESS:
			lszValue = ''
	return lszValue

# Byte and byte arrays.
ctypedef unsigned char  byte
ctypedef unsigned char* bytes

# Generic
ctypedef unsigned long ulong

# inline function for reading to the end of the file, recording the filesize, and then resetting to
# the start.
cdef inline ulong get_flen(FILE* fp):
	cdef long sz
	fseek(fp, 0L, SEEK_END)
	sz = ftell(fp)
	fseek(fp, 0L, SEEK_SET)
	return <ulong>sz if sz > 0L else 0L

# 12 bytes for the !<symlink>\xff\xfe tag line, + two bytes for ending 2 \x00 chars.
cdef inline ulong cyglink_len(ulong flen) except? 0L:
	cdef long datalen = <long>flen - 14L
	return  <ulong> datalen/2L \
			if datalen > 0L and not datalen % 2L \
			else 0L

DEF CYG_STARTLEN = 12
cdef bytes cyglink_start = '!<symlink>\xff\xfe'
cdef bool check_cyglink_start(FILE* fp) except -1:
	cdef bool result = false
	cdef bytes check = <bytes>malloc(sizeof(byte) * (CYG_STARTLEN + 1))
	if check == NULL:
		print 'Fatal error: Could not allocate buffer for bytes result value of check_cyglink_start.'
		return -1
	fread(<void*>check, sizeof(byte), <size_t>CYG_STARTLEN, fp)
	result = check[0:CYG_STARTLEN] == cyglink_start[0:CYG_STARTLEN]

	return result

DEF CYG_ENDLEN = 2
cdef bool check_cyglink_end(FILE* fp) except? 0:
	cdef int b, i = 0
	cdef bool result = true
	while not feof(fp):
		b = fgetc(fp)
		if b == -1:
			break
		if b != 0 or i == CYG_ENDLEN:
			result = false
			break
		i += 1
	return result

cpdef object symlink(char* source, char* link_name):
	cdef FILE* flink
	cdef char c
	flink = fopen(link_name,'wb')
	fwrite(cyglink_start, sizeof(byte), CYG_STARTLEN, flink)
	for c in source[0:<int>strlen(source)]:
		putc(<int>c, flink)
		putc(0, flink)
	fwrite('\x00\x00', sizeof(byte), 2, flink)
	fclose(flink)
	return 1==1

cpdef object readlink(char* fpath):
	cdef FILE* flink
	cdef ulong flen, plen
	cdef bytes linkpath
	cdef object result
	cdef int i = 0
	flink = fopen(fpath,'rb')
	if flink == NULL:
		print 'Error: Null reference returned from fopen. Could not open file.'
		return None
	flen = get_flen(flink)
	plen = cyglink_len(flen)
	if not plen:
		print 'Debug: Length did not match expected length. Not a symbolic link.'
		fclose(flink)
		return None
	if not check_cyglink_start(flink):
		print 'Debug: File start did not match expected ending. Not a symbolic link.'
		fclose(flink)
		return None
	linkpath = <bytes>malloc(sizeof(byte) * (plen + 1))
	if linkpath == NULL:
		print 'Fatal error: Could not allocate buffer for bytes linkpath value of readlink_cygwin.'
		fclose(flink)
		return None
	# if(fread(<void*>linkpath, sizeof(byte), <size_t>plen, flink) != <size_t>plen):
	# print 'Error: There was an error during the reading of the symbolic link path in readlink_cygwin. Bytes returned did not match expected length.'
	# free(linkpath)
	# fclose(flink)
	# return None
	while i < <int>plen:
		if feof(flink):
			print 'Error: Unexpected EOF while reading the symbolic link in readlink_cygwin.'
			free(linkpath)
			fclose(flink)
			return None
		linkpath[i] = <byte>fgetc(flink)
		if linkpath[i] == <byte>0 or fgetc(flink):
			print 'Error: Unexpected zero character or lack of expected zero character. encountered while reading symbolic link file. (character %d of buffer)' % i
			free(linkpath)
			fclose(flink)
			return None
		i += 1
	if not check_cyglink_end(flink):
		print 'Error: File ending did not match expected ending.'
		free(linkpath)
		fclose(flink)
		return None
	linkpath[plen] = '\x00'
	result = PyString_FromStringAndSize(<char*>linkpath, plen)
	free(linkpath)
	fclose(flink)
	return result

cpdef object cygroot():
	# Default value and result value
	cdef char* result
	cdef size_t rlen
	cdef object pyresult
	cdef char* cygwin_default='C:\\cygwin'
	
	# check current user first
	result = szvalue(HKEY_CURRENT_USER, 'Software\\Cygwin\\setup', 'rootdir')
	if result == NULL:
		result = szvalue(HKEY_LOCAL_MACHINE, 'Software\\Cygwin\\setup', 'rootdir')
	
	# if that doesn't work, check local machine
	if result == NULL:
		rlen = <size_t>strlen(cygwin_default)
		pyresult = PyString_FromStringAndSize(cygwin_default, rlen)
	else:
		rlen = <size_t>strlen(result)
		pyresult = PyString_FromStringAndSize(result, rlen)
		free(result)
	
	return pyresult

def islink(path):
	""" until I implement a real check, we'll just check the output of readlink """
	if readlink(path) is None:
		return False
	return True

def cygtowin(path, recurse=True):
	root = cygroot()
	if path[0:10].lower() == '/cygdrive/':
		path = re.sub(r"^/cygdrive/(?P<drive>\w)/(?P<filepath>.+)$", r"\g<drive>:/\g<filepath>", path)
	else:
		path = cygroot() + path
	
	path = path.replace('/','\\')
	if islink(path) and recurse:
		import os
		dir = os.path.abspath(os.path.dirname(path))
		path = readlink(path)
		if path[0:1] != '/':
			path = os.path.join(dir, path)
	return path