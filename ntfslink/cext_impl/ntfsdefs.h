/**
 * @file ntfsdefs.h
 * 
 * TODO: Description
 */
#ifndef _NTFSDEFS_H_
#define _NTFSDEFS_H_
#pragma once

#ifdef __cplusplus
extern "C" {
#endif

// See NTFS_VOLUME_DATA_BUFFER::BytesPerFileRecordSegment
#define BytesPerFileRecordSegment 1024
#define FILE_RECORD_OUTPUT_BUFFER_SIZE (FIELD_OFFSET(NTFS_FILE_RECORD_OUTPUT_BUFFER, FileRecordBuffer) + BytesPerFileRecordSegment)

// These types should be stored in separate
// include file, not done here
typedef struct {
	ULONG Type;
	USHORT UsaOffset;
	USHORT UsaCount;
	USN Usn;// LONGLONG
} NTFS_RECORD_HEADER, *PNTFS_RECORD_HEADER;
 
typedef struct {
	NTFS_RECORD_HEADER Ntfs;
	USHORT SequenceNumber;
	USHORT LinkCount;
	USHORT AttributesOffset;
	USHORT Flags; // 0x0001 = InUse, 0x0002 = Directory
	ULONG BytesInUse;
	ULONG BytesAllocated;
	ULONGLONG BaseFileRecord;
	USHORT NextAttributeNumber;
} FILE_RECORD_HEADER, *PFILE_RECORD_HEADER;

typedef enum ATTRIBUTE_TYPE {
	AttributeInvalid              = 0x00,         /* Not defined by Windows */
	AttributeStandardInformation  = 0x10,
	AttributeAttributeList        = 0x20,
	AttributeFileName             = 0x30,
	AttributeObjectId             = 0x40,
	AttributeSecurityDescriptor   = 0x50,
	AttributeVolumeName           = 0x60,
	AttributeVolumeInformation    = 0x70,
	AttributeData                 = 0x80,
	AttributeIndexRoot            = 0x90,
	AttributeIndexAllocation      = 0xA0,
	AttributeBitmap               = 0xB0,
	AttributeReparsePoint         = 0xC0,         /* Reparse Point = Symbolic link */
	AttributeEAInformation        = 0xD0,
	AttributeEA                   = 0xE0,
	AttributePropertySet          = 0xF0,
	AttributeLoggedUtilityStream  = 0x100
} ATTRIBUTE_TYPE;

typedef struct {
	ATTRIBUTE_TYPE AttributeType;
	ULONG Length;
	BOOLEAN Nonresident;
	UCHAR NameLength;
	USHORT NameOffset;
	USHORT Flags; // 0x0001 = Compressed
	USHORT AttributeNumber;
} ATTRIBUTE, *PATTRIBUTE;

typedef struct {
	ATTRIBUTE Attribute;
	ULONG ValueLength;
	USHORT ValueOffset;
	USHORT Flags; // 0x0001 = Indexed
} RESIDENT_ATTRIBUTE, *PRESIDENT_ATTRIBUTE;

typedef struct {
	ATTRIBUTE Attribute;
	ULONGLONG LowVcn;
	ULONGLONG HighVcn;
	USHORT RunArrayOffset;
	UCHAR CompressionUnit;
	UCHAR AlignmentOrReserved[5];
	ULONGLONG AllocatedSize;
	ULONGLONG DataSize;
	ULONGLONG InitializedSize;
	ULONGLONG CompressedSize; // Only when compressed
} NONRESIDENT_ATTRIBUTE, *PNONRESIDENT_ATTRIBUTE;

typedef struct {
	ULONGLONG CreationTime;
	ULONGLONG ChangeTime;
	ULONGLONG LastWriteTime;
	ULONGLONG LastAccessTime;
	ULONG FileAttributes;
	ULONG AlignmentOrReservedOrUnknown[3];
	ULONG QuotaId; // NTFS 3.0 only
	ULONG SecurityId; // NTFS 3.0 only
	ULONGLONG QuotaCharge; // NTFS 3.0 only
	USN Usn; // NTFS 3.0 only
} STANDARD_INFORMATION, *PSTANDARD_INFORMATION;

typedef struct {
	ATTRIBUTE_TYPE AttributeType;
	USHORT Length;
	UCHAR NameLength;
	UCHAR NameOffset;
	ULONGLONG LowVcn;
	ULONGLONG FileReferenceNumber;
	USHORT AttributeNumber;
	USHORT AlignmentOrReserved[3];
} ATTRIBUTE_LIST, *PATTRIBUTE_LIST;

typedef struct {
	ULONGLONG DirectoryFileReferenceNumber;
	ULONGLONG CreationTime; // Saved when filename last changed
	ULONGLONG ChangeTime; // ditto
	ULONGLONG LastWriteTime; // ditto
	ULONGLONG LastAccessTime; // ditto
	ULONGLONG AllocatedSize; // ditto
	ULONGLONG DataSize; // ditto
	ULONG FileAttributes; // ditto
	ULONG AlignmentOrReserved;
	UCHAR NameLength;
	UCHAR NameType; // 0x01 = Long, 0x02 = Short
	WCHAR Name[1];
} FILENAME_ATTRIBUTE, *PFILENAME_ATTRIBUTE;

typedef struct {
    GUID ObjectId;
    union {
	  struct {
		GUID BirthVolumeId;
		GUID BirthObjectId;
		GUID DomainId;
	} ;
	UCHAR ExtendedInfo[48];
    };
} OBJECTID_ATTRIBUTE, *POBJECTID_ATTRIBUTE;

typedef struct {
	//GUID ObjectId;
	ULONGLONG DirectoryFileReferenceNumber;
	BOOLEAN IsDirectory;

	ULONGLONG Size;
	ULONGLONG CreationTime;
	ULONGLONG LastWriteTime;
	ULONGLONG LastAccessTime;
	LPWSTR Name;

} MFT_FILE_INFO, *PMFT_FILE_INFO;

#define WIN32_NAME 1

typedef DWORD (__stdcall *pNtCreateFile)(
	PHANDLE        hFile,
	DWORD          dwAccess,
	PVOID          lpObjectAttrs,
	PVOID          lpIoStatusBlock,
	PLARGE_INTEGER AllocationSize,
	DWORD          dwAttributes,
	DWORD          dwShareAccess,
	DWORD          dwCreateDisposition,
	DWORD          dwCreateOptions,
	PVOID          lpEaBuffer,
	DWORD          dwEaLength
);

typedef DWORD (__stdcall *pNtReadFile)(
	IN HANDLE          hFile,
	IN HANDLE          hEvent,
	IN PVOID           lpApcRoutine,
	IN PVOID           lpApcContext,
	OUT PVOID          lpIoStatusBlock,
	OUT PVOID          lpBuffer,
	IN DWORD           dwLength,
	IN PLARGE_INTEGER  lpqByteOffset,
	IN PULONG          lpdKey
);

typedef struct _UNICODE_STRING {
	USHORT Length, MaximumLength;
	PWCH Buffer;
} UNICODE_STRING, *PUNICODE_STRING;

typedef struct _OBJECT_ATTRIBUTES {
	ULONG Length;
	HANDLE RootDirectory;
	PUNICODE_STRING ObjectName;
	ULONG Attributes;
	PVOID SecurityDescriptor;        // Points to type SECURITY_DESCRIPTOR
	PVOID SecurityQualityOfService;  // Points to type SECURITY_QUALITY_OF_SERVICE
 } OBJECT_ATTRIBUTES;

 #define InitializeObjectAttributes( p, n, a, r, s ) { \
	(p)->Length = sizeof( OBJECT_ATTRIBUTES ); \
	(p)->RootDirectory = r; \
	(p)->Attributes = a; \
	(p)->ObjectName = n; \
	(p)->SecurityDescriptor = s; \
	(p)->SecurityQualityOfService = NULL; \
}

#define OBJ_CASE_INSENSITIVE  0x00000040L
#define FILE_NON_DIRECTORY_FILE  0x00000040
#define FILE_OPEN_BY_FILE_ID  0x00002000
#define FILE_OPEN   0x00000001

#ifdef __cplusplus
}
#endif

#endif /* _NTFSDEFS_H_ */
