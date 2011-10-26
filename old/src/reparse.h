#pragma once
//--------------------------------------------------------------------
//
// Junction
// Copyright (C) 1999 Mark Russinovich
// Systems Internals - http://www.sysinternals.com
//
// Reparse point-related definitions and typedefs.
//
//--------------------------------------------------------------------

//
// Maximum reparse buffer info size. The max user defined reparse
// data is 16KB, plus there's a header.
//

#define MAX_REPARSE_SIZE	17000

#define IO_REPARSE_TAG_SYMBOLIC_LINK      IO_REPARSE_TAG_RESERVED_ZERO
#define IO_REPARSE_TAG_MOUNT_POINT              (0xA0000003L)       // winnt ntifs
#define IO_REPARSE_TAG_HSM                      (0xC0000004L)       // winnt ntifs
#define IO_REPARSE_TAG_SIS                      (0x80000007L)       // winnt ntifs


	//
	// Undocumented FSCTL_SET_REPARSE_POINT structure definition
	//
#define REPARSE_MOUNTPOINT_HEADER_SIZE   8
typedef struct {
	DWORD          ReparseTag;
	DWORD          ReparseDataLength;
	WORD           Reserved;
	WORD           ReparseTargetLength;
	WORD           ReparseTargetMaximumLength;
	WORD           Reserved1;
	WCHAR          ReparseTarget[1];
} REPARSE_MOUNTPOINT_DATA_BUFFER, *PREPARSE_MOUNTPOINT_DATA_BUFFER;



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
	};
} REPARSE_DATA_BUFFER, *PREPARSE_DATA_BUFFER;