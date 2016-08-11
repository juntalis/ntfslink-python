/**
 * @file findlinks.c
 * @brief Find links
 */
#include "pch.h"
#include "ntfsdefs.h"

typedef struct _FILENAME_PART {
	LPWSTR Data;
	UCHAR DataLength;
	struct _FILENAME_PART *Next;
	struct _FILENAME_PART *Prev;
} FILENAME_PART;

typedef BOOL(*PROCESSFILERECORD)(IN PFILE_RECORD_HEADER lpFileRecordHeader, IN OPTIONAL LPVOID lpUserData);
typedef BOOL(*ENUMATTRIBUTEPROC)(IN PATTRIBUTE lpAttr, IN OPTIONAL LPVOID lpUserData, IN OUT LPBOOL lpbContinue);

BOOL ReadFileNamePartsProcessFileRecord(IN PFILE_RECORD_HEADER lpFileRecordHeader, IN OPTIONAL LPVOID lpUserData);

FILENAME_PART* AllocateNextPart(FILENAME_PART* lpCurrent)
{
	FILENAME_PART* lpNext = NULL;
	if(lpNext = (FILENAME_PART*)malloc(sizeof(FILENAME_PART))) {
		memset((void*)lpNext, 0, sizeof(FILENAME_PART));
		lpNext->Prev = lpCurrent;
	}
	return (lpCurrent->Next = lpNext);
}

BOOL CopyFileNamePart(IN OUT FILENAME_PART* lpPart, IN PFILENAME_ATTRIBUTE lpFileName)
{
	BOOL bResult = FALSE;
	SIZE_T szBuffer = sizeof(WCHAR) * (lpFileName->NameLength + 1);
	if(lpPart->Data = (LPWSTR)malloc(szBuffer)) {
		lpPart->DataLength = lpFileName->NameLength;
		memset((void*)lpPart->Data, 0, szBuffer);
		wcsncpy(lpPart->Data, (const wchar_t*)lpFileName->Name, lpPart->DataLength);
		bResult = TRUE;
	}
	return bResult;
}

BOOL EnumRecordAttributes(PFILE_RECORD_HEADER lpFileRecordHeader, IN ENUMATTRIBUTEPROC fnEnumAttrs, IN OPTIONAL LPVOID lpUserData)
{
	BOOL bSuccess = TRUE, bContinue = TRUE;
	PATTRIBUTE lpAttr = (PATTRIBUTE)((LPBYTE)lpFileRecordHeader + lpFileRecordHeader->AttributesOffset);
	
	// Loop through our attributes (unless our handler says to stop)
	while(bContinue && lpAttr && lpAttr->AttributeType <= AttributeLoggedUtilityStream) {
		// Process attribute
		if(!(bSuccess = fnEnumAttrs(lpAttr, lpUserData, &bContinue)))
			break;
		
		// Figure out the current attribute size, then move on to the next.
		if(lpAttr->Nonresident) {
			lpAttr = (PATTRIBUTE)Add2Ptr(lpAttr, sizeof(NONRESIDENT_ATTRIBUTE));
		} else if(lpAttr->Length && lpAttr->Length < lpFileRecordHeader->BytesInUse) {
			lpAttr = (PATTRIBUTE)Add2Ptr(lpAttr, lpAttr->Length);
		} else {
			lpAttr = NULL;
		}
	}
	
	return bSuccess;
}

BOOL ProcessFileRecord(IN HANDLE hVolume, IN LARGE_INTEGER FileReferenceNumber, IN PROCESSFILERECORD fnProcessFileRecord, IN OPTIONAL LPVOID lpUserData)
{
	BOOL bSuccess = FALSE;
	DWORD dwRead, dwBufferSize = FILE_RECORD_OUTPUT_BUFFER_SIZE;
	C_ASSERT(sizeof(FileReferenceNumber) == sizeof(NTFS_FILE_RECORD_INPUT_BUFFER));
	NTFS_FILE_RECORD_OUTPUT_BUFFER* nrb = (NTFS_FILE_RECORD_OUTPUT_BUFFER*)malloc(dwBufferSize);
	if(DeviceIoControl(hVolume, FSCTL_GET_NTFS_FILE_RECORD, &FileReferenceNumber, sizeof(FileReferenceNumber), nrb, dwBufferSize, &dwRead, NULL)) {
		// FSCTL_GET_NTFS_FILE_RECORD retrieves one MFT entry
		// FILE_RECORD_HEADER is the Base struct for the MFT entry
		// that we will work from
		PFILE_RECORD_HEADER lpFileRecordHeader = (PFILE_RECORD_HEADER)nrb->FileRecordBuffer;
		
		// Verify that the first four bytes are: FILE
		if(lpFileRecordHeader->Ntfs.Type == 'ELIF') {
			bSuccess = fnProcessFileRecord(lpFileRecordHeader, lpUserData);
		}
	}
	
	return bSuccess;
}

typedef struct {
	HANDLE hVolume;
	FILENAME_PART* Tail;
} ReadFileNamePartsData;

typedef struct {
	HANDLE hVolume;
	USHORT LinkCount;
	USHORT CurrentLink;
	ReadFileNamePartsData* LinkData;
} ReadHardlinksData;

BOOL ReadFileNamePartsEnumAttributes(IN PATTRIBUTE lpAttr, IN OPTIONAL LPVOID lpUserData, IN OUT LPBOOL lpbContinue)
{
	BOOL bSuccess = TRUE;
	ReadFileNamePartsData* lpData = (ReadFileNamePartsData*)lpUserData;
	*lpbContinue = TRUE;
	if(lpAttr->AttributeType == AttributeFileName) {
		PRESIDENT_ATTRIBUTE lpResident = (PRESIDENT_ATTRIBUTE)lpAttr;
		PFILENAME_ATTRIBUTE lpFileName = (PFILENAME_ATTRIBUTE)Add2Ptr(lpAttr, lpResident->ValueOffset);
		if(lpFileName->NameType & WIN32_NAME || lpFileName->NameType == 0) {
			FILENAME_PART* lpNext;
			bSuccess = FALSE;
			if((lpNext = AllocateNextPart(lpData->Tail)) && CopyFileNamePart(lpNext, lpFileName)) {
				lpData->Tail = lpNext;
				if(lpFileName->DirectoryFileReferenceNumber == 0x5 || lpFileName->NameType == 3) {
					bSuccess = TRUE;
				} else {
					bSuccess = ProcessFileRecord(lpData->hVolume, *((LARGE_INTEGER*)&lpFileName->DirectoryFileReferenceNumber), ReadFileNamePartsProcessFileRecord, lpUserData);
				}
			}
			*lpbContinue = FALSE;
		}
	}
	return bSuccess;
}

BOOL ReadFileNamePartsProcessFileRecord(IN PFILE_RECORD_HEADER lpFileRecordHeader, IN OPTIONAL LPVOID lpUserData)
{
	return EnumRecordAttributes(lpFileRecordHeader, ReadFileNamePartsEnumAttributes, lpUserData);
}

BOOL ReadHardlinksEnumAttributes(IN PATTRIBUTE lpAttr, IN OPTIONAL LPVOID lpUserData, IN OUT LPBOOL lpbContinue)
{
	BOOL bSuccess = TRUE;
	ReadHardlinksData* lpData = (ReadHardlinksData*)lpUserData;
	*lpbContinue = TRUE;
	if(lpAttr->AttributeType == AttributeFileName) {
		ReadFileNamePartsData* lpReadData;
		PRESIDENT_ATTRIBUTE lpResident = (PRESIDENT_ATTRIBUTE)lpAttr;
		PFILENAME_ATTRIBUTE lpFileName = (PFILENAME_ATTRIBUTE)Add2Ptr(lpAttr, lpResident->ValueOffset);
		if(lpFileName->NameType & WIN32_NAME || lpFileName->NameType == 0) {
			bSuccess = FALSE;
			lpReadData = &(lpData->LinkData[lpData->CurrentLink++]);
			if(lpReadData->Tail = (FILENAME_PART*)malloc(sizeof(FILENAME_PART))) {
				memset((void*)lpReadData->Tail, 0, sizeof(FILENAME_PART));
				if(CopyFileNamePart(lpReadData->Tail, lpFileName)) {
					lpReadData->hVolume = lpData->hVolume;
					bSuccess = ProcessFileRecord(lpData->hVolume, *((LARGE_INTEGER*)&lpFileName->DirectoryFileReferenceNumber), ReadFileNamePartsProcessFileRecord, (LPVOID)lpReadData);
				}
			}
		}
	}
	
	return bSuccess;
}

BOOL ReadHardlinksProcessFileRecord(IN PFILE_RECORD_HEADER lpFileRecordHeader, IN OPTIONAL LPVOID lpUserData)
{
	BOOL bSuccess = FALSE;
	ReadHardlinksData* lpData = (ReadHardlinksData*)lpUserData;
	size_t szDataSize = sizeof(ReadFileNamePartsData) * lpFileRecordHeader->LinkCount;
	lpData->LinkCount = lpFileRecordHeader->LinkCount;
	if(lpData->LinkData = (ReadFileNamePartsData*)malloc(szDataSize)) {
		lpData->CurrentLink = 0;
		memset((void*)lpData->LinkData, 0, szDataSize);
		if(!(bSuccess = EnumRecordAttributes(lpFileRecordHeader, ReadHardlinksEnumAttributes, lpUserData))) {
			//free((void*)lpData->LinkData);
			//lpData->LinkData = NULL;
		}
	}
	return bSuccess;
}

VOID ReadHardLinks(IN HANDLE hVolume, IN LARGE_INTEGER FileRef)
{
	ReadHardlinksData rhlData = { hVolume };
	if(ProcessFileRecord(hVolume, FileRef, ReadHardlinksProcessFileRecord, (LPVOID)&rhlData)) {
		USHORT i = 0;
		for(; i < rhlData.LinkCount; i++) {
			wprintf(L"%u/%u", i, rhlData.LinkCount);
			ReadFileNamePartsData pRFNPD = rhlData.LinkData[i];
			FILENAME_PART* lpCurrent = pRFNPD.Tail;
			while(lpCurrent->Prev) {
			FILENAME_PART* lpLast = lpCurrent;
			if(!lpLast) break;
				wprintf(L"%s\\", lpCurrent->Data);
				lpCurrent = lpCurrent->Prev;
				free((void*)lpLast->Data);
				free((void*)lpLast);
				if(!lpCurrent->Prev) {
					wprintf(L"%s\n", lpCurrent->Data);
				}
			}
			
			free((void*)lpCurrent->Data);
			free((void*)lpCurrent);
		}
		free(rhlData.LinkData);
	} else {
		wprintf(L"ReadHardLinks failed!\n");
	}
}

VOID ReadHardLinkParts(IN HANDLE hVolume, IN LARGE_INTEGER FileRef)
{
	DWORD dwRead, dwBufferSize = FILE_RECORD_OUTPUT_BUFFER_SIZE;
	C_ASSERT(sizeof(FileRef) == sizeof(NTFS_FILE_RECORD_INPUT_BUFFER));
	NTFS_FILE_RECORD_OUTPUT_BUFFER* nrb = (NTFS_FILE_RECORD_OUTPUT_BUFFER*)malloc(dwBufferSize);
	if(DeviceIoControl(hVolume, FSCTL_GET_NTFS_FILE_RECORD, &FileRef, sizeof(FileRef), nrb, dwBufferSize, &dwRead, NULL)) {
		// FSCTL_GET_NTFS_FILE_RECORD retrieves one MFT entry
		// FILE_RECORD_HEADER is the Base struct for the MFT entry
		// that we will work from
		
		PFILE_RECORD_HEADER lpFileRecordHeader = (PFILE_RECORD_HEADER)nrb->FileRecordBuffer;
		if(lpFileRecordHeader->Ntfs.Type == 'ELIF') {
			PATTRIBUTE lpAttr = (PATTRIBUTE)((LPBYTE)lpFileRecordHeader + lpFileRecordHeader->AttributesOffset);
			while(lpAttr && lpAttr->AttributeType <= AttributeLoggedUtilityStream) {
				// Only process $FILE_NAME attributes
				if(lpAttr->AttributeType == AttributeFileName) {
					PRESIDENT_ATTRIBUTE lpResident = (PRESIDENT_ATTRIBUTE)lpAttr;
					PFILENAME_ATTRIBUTE lpFileName = (PFILENAME_ATTRIBUTE)Add2Ptr(lpAttr, lpResident->ValueOffset);
					if(lpFileName->NameType & WIN32_NAME || lpFileName->NameType == 0) {
						
						// Reached the root
						if(lpFileName->DirectoryFileReferenceNumber == 0x5) {
							wprintf(L"Hit Root\n");
						}
						
						lpFileName->Name[lpFileName->NameLength] = L'\0';
						wprintf(L"FileName :%s\n", lpFileName->Name) ;
					}
				}
				
				if(lpAttr->Nonresident) {
					lpAttr = (PATTRIBUTE)Add2Ptr(lpAttr, sizeof(NONRESIDENT_ATTRIBUTE));
				} else if(lpAttr->Length && lpAttr->Length < lpFileRecordHeader->BytesInUse) {
					lpAttr = (PATTRIBUTE)Add2Ptr(lpAttr, lpAttr->Length);
				} else {
					lpAttr = NULL;
				}
			}
		}
	}
	free(nrb);
}

// Open the volume
HANDLE OpenVolume(WCHAR wcVolume)
{
	static HANDLE hVolume = NULL;
	static WCHAR lpsVolumeRoot[] = L"\\\\.\\A:";
	
	// Uppercase volume letters.
	if(iswlower((wint_t)wcVolume)) {
		wcVolume = towupper((wint_t)wcVolume);
	}
	
	if(VALID_HANDLE(hVolume)) {
		if(wcVolume == lpsVolumeRoot[4])
			return hVolume;
		CloseHandle(hVolume);
	}

	lpsVolumeRoot[4] = wcVolume;
	hVolume = CreateFileW(lpsVolumeRoot, GENERIC_READ, FILE_SHARE_READWRITE, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
	return VALID_HANDLE(hVolume) ? hVolume : NULL;
}

HANDLE OpenVolumeOfFilePath(IN LPCWSTR lpsFilePath, OUT WCHAR* lpwcVolume)
{
	HANDLE hVolume = NULL;
	WCHAR lpVolumePath[MAX_PATH + 1] = W_EMPTY;
	*lpwcVolume = L'\0';
	if(GetVolumePathName(lpsFilePath, lpVolumePath, WLEN(lpVolumePath))) {
		hVolume = OpenVolume(*lpwcVolume = *lpVolumePath);
	}
	return hVolume;
}
 
int __cdecl _tmain(int argc, TCHAR* argv[])
{
	WCHAR wcVolume;
	LPCWSTR lpFileName;
	HANDLE hFile, hVolume;
	LARGE_INTEGER FileRef;
	BY_HANDLE_FILE_INFORMATION fiItem;
	DWORD dwFileAttrs, dwFlagsAndAttributes = FILE_ATTRIBUTE_NORMAL;
	
	// Check command-line arguments.
	if(argc == 1) {
		_tprintf(_T("Usage: %s <filepath>\n"), argv[0]);
		return 0;
	}
	
	// Determine the flags we'll use for opening our filepath (based on whether or not lpFileName
	// contains a folder path)
	lpFileName = (LPCWSTR)argv[1];
	dwFileAttrs = GetFileAttributesW(lpFileName);
	if(HAS_FLAG(dwFileAttrs, INVALID_FILE_ATTRIBUTES)) {
		FatalError(ERROR_PATH_NOT_FOUND, _T("%s does not exist."), lpFileName);
	} else if(HAS_FLAG(dwFileAttrs, FILE_ATTRIBUTE_DIRECTORY)) {
		dwFlagsAndAttributes |= FILE_FLAG_BACKUP_SEMANTICS;
	}
	
	hFile = CreateFile(lpFileName, GENERIC_READ, FILE_SHARE_READWRITE, NULL, OPEN_EXISTING, dwFlagsAndAttributes, NULL);
	CheckStatement(VALID_HANDLE(hFile));
	GetFileInformationByHandle(hFile, &fiItem);
	CloseHandle(hFile);
	
	if(!(hVolume = OpenVolumeOfFilePath(lpFileName, &wcVolume))) {
		FatalApi(CreateFile);
	}
	
	FileRef.LowPart  = fiItem.nFileIndexLow;
	FileRef.HighPart = fiItem.nFileIndexHigh;
	ReadHardLinks(hVolume, FileRef);
	CloseHandle(hVolume);
	return 0;
}
