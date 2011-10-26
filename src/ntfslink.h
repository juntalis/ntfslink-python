#ifndef NTFSLINK_H
#define NTFSLINK_H

#include <windows.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
// Definitions
#ifndef NTFSLINK_DEFS

	#define MAX_NAME_LENGTH 1024
	#define MAX_REPARSE_BUFFER 16*1024 // From reparselib
	#define REPARSE_MOUNTPOINT_HEADER_SIZE 8 // From junction source
	#define DIRPOINT_FLAG (FILE_ATTRIBUTE_DIRECTORY | FILE_ATTRIBUTE_REPARSE_POINT)
	
	#define SYMLINK_FLAG_RELATIVE 1 // From reparselib
	#define SYMLINK_FILE 0x0 
	#define SYMLINK_DIR 0x1
	
	// From junction source - slightly modified.
	#ifndef IO_REPARSE_TAG_SYMBOLIC_LINK
		#define IO_REPARSE_TAG_SYMBOLIC_LINK IO_REPARSE_TAG_RESERVED_ZERO
	#endif
	#ifndef IO_REPARSE_TAG_MOUNT_POINT
		#define IO_REPARSE_TAG_MOUNT_POINT (0xA0000003L)
	#endif
	#ifndef IO_REPARSE_TAG_HSM
		#define IO_REPARSE_TAG_HSM (0xC0000004L)
	#endif
	#ifndef IO_REPARSE_TAG_SIS
		#define IO_REPARSE_TAG_SIS (0x80000007L)
	#endif

	#define SZWCHAR sizeof(WCHAR)
	#define SZCHAR sizeof(CHAR)
	
	#define RESULT_CREATE int
	#define RESULT_ERROR_SET -4
	#define RESULT_ERROR_CREATE -3
	#define RESULT_NOT_SUPPORTED -2
	#define RESULT_INVALID_TARGET -1
	#define RESULT_INVALID_LINK 0
	#define RESULT_SUCCESS 1
#endif

/* Pretty standard with any code dealing with junctions. */
#ifndef REPARSE_DATA_BUFFER
	// Reparse point buffer.
	typedef struct _REPARSE_DATA_BUFFER {
		ULONG  ReparseTag;
		USHORT ReparseDataLength;
		USHORT Reserved;
		union {
			struct {
				USHORT SubstituteNameOffset;
				USHORT SubstituteNameLength;
				USHORT PrintNameOffset;
				USHORT PrintNameLength;
				ULONG Flags;
				WCHAR PathBuffer[1];
			} SymbolicLinkReparseBuffer;
			struct {
				USHORT SubstituteNameOffset;
				USHORT SubstituteNameLength;
				USHORT PrintNameOffset;
				USHORT PrintNameLength;
				WCHAR PathBuffer[1];
			} MountPointReparseBuffer;
			struct {
				UCHAR  DataBuffer[1];
			} GenericReparseBuffer;
		} DUMMYUNIONNAME;
	} REPARSE_DATA_BUFFER, *PREPARSE_DATA_BUFFER;
	#define REPARSE_DATA_BUFFER_HEADER_SIZE FIELD_OFFSET(REPARSE_DATA_BUFFER,GenericReparseBuffer)
#endif

/* From junction utility */
#ifndef REPARSE_MOUNTPOINT_DATA_BUFFER
	// Undocumented FSCTL_SET_REPARSE_POINT structure definition
	typedef struct {
		DWORD	ReparseTag;
		DWORD	ReparseDataLength;
		WORD	Reserved;
		WORD	ReparseTargetLength;
		WORD	ReparseTargetMaximumLength;
		WORD	Reserved1;
		WCHAR	ReparseTarget[1];
	} REPARSE_MOUNTPOINT_DATA_BUFFER, *PREPARSE_MOUNTPOINT_DATA_BUFFER;
#endif

// Function prototypes
BOOL IsFolder(IN LPTSTR pszPath);
BOOL IsReparseDir(IN LPCTSTR sFileName);
BOOL IsReparsePoint(IN LPCTSTR sFileName);
BOOL PathExists(IN LPCTSTR sFilepath);
RESULT_CREATE AbsPaths(IN LPTSTR linkPath, IN LPTSTR targetPath, OUT LPTSTR outLink, OUT LPTSTR outTarget);
BOOL GetReparseBuffer(IN LPCTSTR sFileName, OUT PREPARSE_GUID_DATA_BUFFER pBuf);
BOOL GetReparseGUID(IN LPCTSTR sFileName, OUT GUID* pGuid);
BOOL GetReparseTag(IN LPCTSTR sFileName, OUT DWORD* pTag);
BOOL DeleteReparsePoint(IN LPCTSTR sFileName);
BOOL CreateCustomReparsePoint(
	IN LPCTSTR sFileName, IN PVOID pBuffer, IN UINT uBufSize, IN GUID uGuid, IN ULONG uReparseTag
);
RESULT_CREATE CreateJunction(IN LPTSTR LinkTarget, IN LPTSTR LinkDirectory);
BOOL ReadReparsePoint(IN LPCTSTR sFileName, OUT LPWSTR sBuffer, IN USHORT uBufferLength);
#endif //NTFSLINK_H