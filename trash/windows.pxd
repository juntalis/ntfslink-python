from libc.stddef cimport wchar_t

cdef extern from "windows.h":
	# Basics
	ctypedef void VOID
	ctypedef char CHAR
	ctypedef wchar_t WCHAR
	#ifdef UNICODE
	#ctypedef WCHAR TCHAR
	#else
	ctypedef CHAR TCHAR
	#endif
	ctypedef unsigned char UCHAR
	ctypedef unsigned char BYTE
	# if unicode
	#ctypedef WCHAR TBYTE
	# else
	ctypedef UCHAR TBYTE
	# end if
	ctypedef int BOOL
	ctypedef BYTE BOOLEAN

	# Number stuff
	ctypedef int INT
	ctypedef unsigned int UINT
	ctypedef signed int INT32
	ctypedef unsigned int UINT32

	ctypedef float FLOAT

	ctypedef long LONG
	ctypedef unsigned long ULONG
	ctypedef signed int LONG32
	ctypedef unsigned long ULONG
	ctypedef unsigned int ULONG32
	ctypedef LONG __int64
	ctypedef ULONG uint64_t
	ctypedef signed long int64_t
	ctypedef int64_t INT64
	ctypedef uint64_t UINT64
	ctypedef __int64 LONG64
	ctypedef uint64_t ULONG64

	#if !defined(_M_IX86)
	ctypedef __int64 LONGLONG
	ctypedef unsigned long ULONGLONG
	#else
	#ctypedef double ULONGLONG
	#ctypedef double LONGLONG
	#endif

	ctypedef short SHORT
	ctypedef unsigned short USHORT

	# WORD & DWORD stuff
	ctypedef unsigned short WORD
	ctypedef unsigned long DWORD
	ctypedef unsigned int DWORD32
	ctypedef uint64_t DWORD64
	ctypedef ULONGLONG DWORDLONG

	# Pointers
	ctypedef void* PVOID
	ctypedef void* LPVOID
	ctypedef void* LPCVOID

	ctypedef CHAR* PCHAR
	ctypedef WCHAR* PWCHAR
	ctypedef UCHAR* PUCHAR
	ctypedef TCHAR* PTCHAR

	ctypedef BYTE* PBYTE
	ctypedef BYTE* LPBYTE
	ctypedef TBYTE* PTBYTE
	ctypedef TBYTE* LPTBYTE

	ctypedef BOOL* PBOOL
	ctypedef BOOL* LPBOOL
	ctypedef BOOLEAN* PBOOLEAN
	ctypedef BOOLEAN* LPBOOLEAN

	# Strings
	ctypedef CHAR* PSTR
	ctypedef CHAR* PCSTR
	ctypedef CHAR* LPCSTR
	ctypedef CHAR* LPSTR

	ctypedef WCHAR* PWSTR
	ctypedef WCHAR* PCWSTR
	ctypedef WCHAR* LPCWSTR
	ctypedef WCHAR* LPWSTR

	#ifdef UNICODE
	#ctypedef LPWSTR PTSTR
	#ctypedef LPWSTR LPTSTR
	#ctypedef LPCWSTR LPCTSTR
	#else
	ctypedef LPSTR PTSTR
	ctypedef LPSTR LPTSTR
	ctypedef LPCSTR LPCTSTR
	#endif

	cdef struct _UNICODE_STRING:
		USHORT Length
		USHORT MaximumLength
		PWSTR Buffer
	ctypedef _UNICODE_STRING UNICODE_STRING
	ctypedef UNICODE_STRING* PUNICODE_STRING
	ctypedef UNICODE_STRING* PCUNICODE_STRING

	ctypedef INT* PINT
	ctypedef INT* LPINT
	#if defined(_WIN64)
	#ctypedef INT64 INT_PTR
	#ctypedef INT64 LONG_PTR
	#ctypedef UINT64 UINT_PTR
	#ctypedef UINT64 ULONG_PTR
	#else
	ctypedef INT INT_PTR
	ctypedef LONG LONG_PTR
	ctypedef UINT UINT_PTR
	ctypedef ULONG ULONG_PTR
	#endif

	ctypedef INT32* PINT32
	ctypedef INT64* PINT64
	ctypedef UINT* PUINT
	ctypedef UINT_PTR* PUINT_PTR
	ctypedef UINT32* PUINT32
	ctypedef UINT64* PUINT64

	ctypedef FLOAT* PFLOAT

	ctypedef LONG* PLONG
	ctypedef LONG* LPLONG
	ctypedef LONG_PTR* PLONG_PTR
	ctypedef LONG32* PLONG32
	ctypedef LONG64* PLONG64
	ctypedef LONGLONG* PLONGLONG
	ctypedef ULONG* PULONG
	ctypedef ULONG_PTR* PULONG_PTR
	ctypedef ULONG32* PULONG32
	ctypedef ULONG64* PULONG64
	ctypedef ULONGLONG* PULONGLONG

	ctypedef SHORT* PSHORT
	ctypedef USHORT* PUSHORT

	ctypedef ULONG_PTR SIZE_T
	ctypedef SIZE_T* PSIZE_T
	ctypedef LONG_PTR SSIZE_T
	ctypedef SSIZE_T* PSSIZE_T

	#ifdef _WIN64
	#ctypedef UINT UHALF_PTR
	#else
	ctypedef USHORT UHALF_PTR
	#endif
	ctypedef UHALF_PTR* PUHALF_PTR

	ctypedef WORD* PWORD
	ctypedef WORD* LPWORD
	ctypedef DWORD* PDWORD
	ctypedef DWORD* LPDWORD
	ctypedef ULONG_PTR DWORD_PTR
	ctypedef DWORD* LPCOLORREF
	ctypedef ULONG_PTR DWORD_PTR
	ctypedef DWORDLONG* PDWORDLONG
	ctypedef DWORD_PTR* PDWORD_PTR
	ctypedef DWORD32* PDWORD32
	ctypedef DWORD64* PDWORD64
	ctypedef ULONG_PTR DWORD_PTR

	# Various DWORD typedefs
	ctypedef DWORD LCID
	ctypedef DWORD LCTYPE
	ctypedef DWORD LGRPID

	# Handles
	ctypedef PVOID HANDLE
	ctypedef HANDLE* PHANDLE
	ctypedef HANDLE* LPHANDLE
	ctypedef HANDLE HCONV
	ctypedef HANDLE HCONVLIST
	ctypedef HANDLE HDDEDATA
	ctypedef HANDLE HGLOBAL
	ctypedef HANDLE HHOOK
	ctypedef HANDLE HRSRC
	ctypedef HANDLE HSZ
	ctypedef HANDLE WINSTA
	ctypedef HANDLE HWINSTA
	ctypedef HANDLE HINSTANCE
	ctypedef HANDLE HKL
	ctypedef HANDLE HLOCAL

	# Other stuff
	ctypedef WORD ATOM
	ctypedef int HFILE
	ctypedef HINSTANCE HMODULE
	ctypedef WORD LANGID
	ctypedef PDWORD PLCID
	ctypedef HANDLE SC_HANDLE
	ctypedef LPVOID SC_LOCK
	ctypedef HANDLE SERVICE_STATUS_HANDLE
	ctypedef LONGLONG USN



# Not sure how to implement these yet
#if defined(_WIN64)
# define POINTER_32 __ptr32
#else
# define POINTER_32
#endif
#if (_MSC_VER >= 1300)
# define POINTER_64 __ptr64
#else
# define POINTER_64
#endif
#define POINTER_SIGNED __sptr
#define POINTER_UNSIGNED __uptr