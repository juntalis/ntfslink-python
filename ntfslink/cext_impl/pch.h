/**
 * @file pch.h
 * 
 * TODO: Description
 */
#ifndef _PCH_H_
#define _PCH_H_
#pragma once

/** Char Type Config */
#define UNICODE 1
#define _UNICODE UNICODE

// Macro used to combine two things. (Including other macros)
#define XMERGE2(A,B) A##B
#define XMERGE(A,B)  XMERGE2(A,B)

// Stringifying macros
#define XWIDEN(X) XMERGE2(L,X)
#define XSTR2(X) #X
#define XSTRA(X) XSTR2(X)
#define XSTRW(X) XWIDEN(XSTRA(X))

/** Windows Version */
#if !defined(WINVER)
#	define WINVER 0x0501
#elif (WINVER < 0x0501)
#	error Windows XP is currently the lowest version of Windows supported by this project.
#endif
#if !defined(_WIN32_WINNT)
#	define _WIN32_WINNT 0x0501
#elif (_WIN32_WINNT < 0x0501)
#	error Windows XP is currently the lowest version of Windows supported by this project.
#endif
#if !defined(NTDDI_VERSION)
#	define NTDDI_VERSION 0x05010000
#elif (NTDDI_VERSION < 0x05010000)
#	error Windows XP is currently the lowest version of Windows supported by this project.
#endif

/** Compiler Detection & Inline Definition */
#if defined(__clang__) || defined(__MINGW32__) || defined(__GNUC__)
#	define BUILD_COMPILER_GNU
#	ifndef noret
#		define noret void __attribute__((__noreturn))
#	endif
#	ifndef inline
#		define inline __inline
#	endif
#	if defined(__i386__)
#		define BUILD_ARCH_X86
#		define BUILD_ARCH_BITS 32
#	elif defined(__x86_64__)
#		define BUILD_ARCH_X64
#		define BUILD_ARCH_BITS 64
#	endif
#elif defined(RC_INVOKED)
#	define BUILD_COMPILER_RC
#	define BUILD_ARCH_X86
#	define BUILD_ARCH_BITS 32
#	define inline 
#elif defined(_MSC_VER)
#	define BUILD_COMPILER_MSVC
#	ifndef noret
#		define noret void __declspec(noreturn)
#	endif
#	ifndef __cplusplus
#		ifdef inline
#			undef inline
#		endif
#		define inline __forceinline
#	endif
#	if (defined(_M_IA64) || defined(_M_AMD64) || defined(_WIN64))
#		define BUILD_ARCH_X64
#		define BUILD_ARCH_BITS 64
#	elif defined(_M_IX86)
#		define BUILD_ARCH_X86
#		define BUILD_ARCH_BITS 32
#	endif
#endif

#ifndef BUILD_ARCH_BITS
#	error Could not detect platform architecture.
#endif

/** Char Type Definitions */
#ifdef _UNICODE
#	define BUILD_UNICODE
#	define __TFILE__ XWIDEN(__FILE__)
#	define XSTR(X) XSTRW(X)
#	define ISFUNC_CHAR wint_t
#else
#	ifndef _MBCS
#		define _MBCS 1
#	endif
#	define BUILD_MBCS
#	define __TFILE__ __FILE__
#	define XSTR(X) XSTRA(X)
#	define ISFUNC_CHAR int
#endif

/** System Includes */
#include <windows.h>
#include <winioctl.h>
#include <tchar.h>
#include <stdio.h>
#include <string.h>
#include <crtdbg.h>

#define W_EMPTY L""
#define WSIZE(COUNT) ((COUNT) * sizeof(WCHAR))
#define WLEN(WBUFFER)  (sizeof(WBUFFER) / sizeof(WCHAR))

#define T_EMPTY _T("")
#define TSIZE(COUNT) ((COUNT) * sizeof(TCHAR))
#define TLEN(TBUFFER)  (sizeof(TBUFFER) / sizeof(TCHAR))

// Compiler-specific Boolean Declarations
#ifdef BUILD_COMPILER_GNU
#	include <stdbool.h>
#	include <stdint.h>
#	ifndef _INTPTR_T_DEFINED
#		ifdef BUILD_ARCH_X64
		typedef int64_t  intptr_t;
		typedef uint64_t uintptr_t;
#		else
		typedef int32_t  intptr_t;
		typedef uint32_t uintptr_t;
#		endif
#	endif
	typedef int8_t    s8;
	typedef int16_t   s16;
	typedef int32_t   s18;
	typedef int64_t   s64;
	typedef intptr_t  sPtr;
	
	typedef uint8_t   u8;
	typedef uint16_t  u16;
	typedef uint32_t  u18;
	typedef uint64_t  u64;
	typedef uintptr_t uPtr;
#else
#	ifdef BUILD_COMPILER_MSVC
	typedef signed __int8 bool;
	typedef signed   __int8    s8;
	typedef signed   __int16   s16;
	typedef signed   __int32   s32;
	typedef signed   __int64   s64;
	typedef signed   __int3264 sPtr;
	
	typedef unsigned __int8    u8;
	typedef unsigned __int16   u16;
	typedef unsigned __int32   u32;
	typedef unsigned __int64   u64;
	typedef unsigned __int3264 uPtr;
#	else
	typedef BOOLEAN bool;
#	endif
#	define true TRUE
#	define false FALSE
#endif

/** Utility Constants */
#ifndef MAX_PATH
#	define MAX_PATH _MAX_PATH
#endif

#ifndef FILE_SHARE_READWRITE
#	define FILE_SHARE_READWRITE (FILE_SHARE_READ | FILE_SHARE_WRITE)
#endif

// Since sizeof will add 1 for the trailing \0, we'll leave off the leading '\' so the count
// isn't off.
#define SYSDIR_SUBDIR "system32"

/** Utility Macros */
#define Add2Ptr(PTR,OFFSET) (((PUCHAR)(PTR)) + (OFFSET))

#define VALID_HANDLE(hSubject) \
	((hSubject) && ((hSubject) != INVALID_HANDLE_VALUE))

#define INVALID_HANDLE(hSubject) \
	(!VALID_HANDLE(hSubject))

#define HAS_FLAG(dwSubject,dwFlag) \
	(((dwSubject) & (dwFlag)) == (dwFlag))

#define xfree(BUF) \
	_xfree_((void*)(BUF))

static inline void _xfree_(void* ptr)
{
	if(ptr) free(ptr);
}

/** Utility deallocation function */
static inline void *xmalloc(size_t size)
{
	void *ptr = malloc(size);
	if(!ptr) perror("malloc failed.");
	memset(ptr, 0, size);
	return ptr;
}

#define xalloc(type) \
	((type)xmalloc(sizeof(type)))

#define xaalloc(type,count) \
	((type*)xmalloc(((size_t)count) * sizeof(type)))

#define xsalloc(type,count) \
	xaalloc(type,((count)+1))

#define stralloc(count) xsalloc(char,count)
#define wcsalloc(count) xsalloc(wchar_t,count)
#define tcsalloc(count) xsalloc(TCHAR,count)

static TCHAR* vtcsprintf_alloc(const TCHAR* lpMessage, va_list lpArgs)
{
	TCHAR *lpResult;
	size_t szDisplayBuf;
	
	// Check the resulting size of the buffer.
	szDisplayBuf = (size_t)_vsctprintf(lpMessage, lpArgs) + 1;

	// Allocate our buffer.
	if(!(lpResult = (TCHAR*)calloc(szDisplayBuf, sizeof(TCHAR)))) {
		return NULL;
	}

	// Finally, fill in the message.
	_vsntprintf(lpResult, szDisplayBuf, lpMessage, lpArgs);
	return lpResult;
}

static TCHAR* tcsprintf_alloc(const TCHAR* lpMessage, ...)
{
	va_list lpArgs = NULL;
	TCHAR* lpDisplayBuf = NULL;
	// Allocate buffer for our resulting format string.
	va_start(lpArgs, lpMessage);
	lpDisplayBuf = vtcsprintf_alloc(lpMessage, lpArgs);
	va_end(lpArgs);
}

static inline noret FatalStatement(char* prefix, char* statement)
{
	fprintf(stderr, "%s: FATAL:%s\n", prefix, statement);
	ExitProcess(1);
}

#define CheckStatement(statement) \
	if(!(statement)) {\
		FatalStatement("[" __FILE__ ":" XSTRA(__LINE__) "]", XSTRA(statement)); \
	}

void ErrorMessage(DWORD dwError, LPCTSTR lpMessage, ...)
{
	va_list lpArgs = NULL;
	TCHAR* lpMsgBuf = NULL, *lpDisplayBuf = NULL, *lpFormatted = NULL;
	size_t szErrLen, szFormatted, szMessage;
	szErrLen = (szMessage = _tcslen(lpMessage));
	if(dwError == ERROR_SUCCESS) dwError = GetLastError();
	if(dwError != ERROR_SUCCESS) {
		const TCHAR *lpErrMsg = NULL;
		FormatMessage(
			FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM |FORMAT_MESSAGE_IGNORE_INSERTS,
			NULL, dwError, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), (TCHAR*)&lpErrMsg, 0, NULL
		);

		szErrLen += _tcslen(lpErrMsg) + 39;
		// Allocate our buffer for the error message.
		CheckStatement(lpMsgBuf = (TCHAR*)calloc(szErrLen + 1, sizeof(TCHAR)));
		memset(lpMsgBuf, 0, TSIZE(szErrLen + 1));
		_sntprintf(lpMsgBuf, szErrLen, _T("ERROR: %s - Windows Error [0x%08X]: %s\n"), lpMessage, dwError, lpErrMsg);
		LocalFree((HLOCAL)lpErrMsg);
	} else {
		szErrLen += 8;
		CheckStatement(lpMsgBuf = (TCHAR*)calloc(szErrLen + 1, sizeof(TCHAR)));
		memset(lpMsgBuf, 0, TSIZE(szErrLen));
		_sntprintf(lpMsgBuf, szErrLen, _T("ERROR: %s\n"), lpMessage);
	}
	
	va_start(lpArgs, lpMessage);
	if(szMessage != (szFormatted = _vsctprintf(lpMessage, lpArgs))) {
		CheckStatement(lpDisplayBuf = vtcsprintf_alloc(lpMsgBuf, lpArgs));
		free(lpMsgBuf);
	} else {
		lpDisplayBuf = lpMsgBuf;
	}
	va_end(lpArgs);
	
	_ftprintf(stderr, (LPCTSTR)lpDisplayBuf);
	xfree(lpDisplayBuf);
}

#define ShowError(dwError,...) \
	ErrorMessage(dwError, __VA_ARGS__)

#define ShowWin32Error(fnFailed) \
	ErrorMessage(ERROR_SUCCESS, XSTR(fnFailed))

#define FatalError(dwError,...) { \
		ErrorMessage(dwError, __VA_ARGS__); \
		ExitProcess(dwError); \
	}

#define FatalApi(fnFailed) FatalError(ERROR_SUCCESS, XSTR(fnFailed))
#ifdef _UNICODE
#	define AbortMe() FatalError(ERROR_SUCCESS, XWIDEN(__FUNCTION__))
#else
#	define AbortMe() FatalError(ERROR_SUCCESS, __FUNCTION__)
#endif

#endif /* _PCH_H_ */
