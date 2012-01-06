/**
 * Some of the code below  this(particularly code dealing with symlinks) is made up of bits and
 * pieces modified from the project, "reparselib". The full source can be found at
 * https://github.com/amdf/reparselib No license was specified, but all credit goes to the author,
 * "amdf". Besides that, a lot of the information on the Win32 API calls made was picked up at
 * http://www.flexhex.com/docs/articles/hard-links.phtml#junctions
 */
#include "ntfslink.h"
#include <io.h>
#include <tchar.h>

/** Checks **/

/**
 *@brief Checks if specified path is a folder
 *@param [in] pszPath File path
 *@return TRUE if folder, FALSE otherwise
 */
BOOL IsFolder(IN LPTSTR pszPath)
{
	return (GetFileAttributes(pszPath) & FILE_ATTRIBUTE_DIRECTORY);
}

/**
 *@brief Checks an existence of a Reparse Point of a specified file
 *@param [in] sFileName File name
 *@return TRUE if exists, FALSE otherwise
 */
BOOL IsReparsePoint(IN LPCTSTR sFileName)
{
	return (GetFileAttributes(sFileName) & FILE_ATTRIBUTE_REPARSE_POINT);
}

/**
 *@brief Checks if specified path is a folder/reparse point
 *@param [in] sFileName File path
 *@return TRUE if folder|reparse point, FALSE otherwise
*/
BOOL IsReparseDir(IN LPCTSTR sFileName)
{
	return (GetFileAttributes(sFileName) & DIRPOINT_FLAG);
}

/**
 *@brief Checks if specified path exists.
 *@param [in] sFileName File path
 *@return TRUE if exists, otherwise false.
*/
BOOL PathExists(IN LPCTSTR sFilepath)
{
	return (_taccess(sFilepath, 00) == 0);
}

/** Utility functions for opening files/directories. **/

/**
 *@brief Get restore privilege in case we don't have it.
 *@param [in] bReadWrite Read and write? (if not, will use GENERIC_READ)
 */
VOID ObtainRestorePrivilege(IN BOOL bReadWrite)
{
	// Obtain restore privilege in case we don't have it
	HANDLE hToken; TOKEN_PRIVILEGES tp;
	OpenProcessToken(GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES, &hToken);
	LookupPrivilegeValue(NULL,
						 (bReadWrite ? SE_RESTORE_NAME : SE_BACKUP_NAME),
						 &tp.Privileges[0].Luid);
	tp.PrivilegeCount = 1;
	tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;
	AdjustTokenPrivileges(hToken, FALSE, &tp, sizeof(TOKEN_PRIVILEGES), NULL, NULL);
	CloseHandle(hToken);
}

/**
 *@brief TODO
 *@param [in] linkPath TODO
 *@param [in] targetPath TODO
 *@param [out] outLink TODO
 *@param [out] outTarget TODO
*/
RESULT_CREATE AbsPaths(IN LPTSTR linkPath, IN LPTSTR targetPath, OUT LPTSTR outLink, OUT LPTSTR outTarget)
{
	PTCHAR	filePart;
		// Get the full path referenced by the target
	if( !GetFullPathName(targetPath, MAX_PATH, outTarget, &filePart ))
		return RESULT_INVALID_TARGET;

	// Get the full path referenced by the directory
	if( !GetFullPathName(linkPath, MAX_PATH, outLink, &filePart ))
		return RESULT_INVALID_LINK;

	if(!PathExists(outTarget))
		return RESULT_INVALID_TARGET;
	
	return RESULT_SUCCESS;
}

/**
 *@brief Open file (reparse point) for reading & backup optionally.
 *@param [in] sFileName File name
 *@param [in] bBackup Use FILE_FLAG_BACKUP_SEMANTICS?
 *@return Handle of opened file
 */
HANDLE OpenFileForRead(IN LPCTSTR sFileName, IN BOOL bBackup)
{
	if(bBackup) ObtainRestorePrivilege(FALSE);
	return CreateFile(
		sFileName, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING,
		(bBackup)
		? FILE_FLAG_OPEN_REPARSE_POINT | FILE_FLAG_BACKUP_SEMANTICS
		: FILE_FLAG_OPEN_REPARSE_POINT, 0);
}

/**
 *@brief Open file (reparse point) for read/write
 *@param [in] sFileName File name
 *@param [in] bBackup Use FILE_FLAG_BACKUP_SEMANTICS?
 *@return Handle of opened file
 */
HANDLE OpenFileForWrite(IN LPCTSTR sFileName, IN BOOL bBackup)
{
	if(bBackup) ObtainRestorePrivilege(TRUE);
	return CreateFile(
		sFileName, GENERIC_WRITE, FILE_SHARE_READ|FILE_SHARE_WRITE, NULL, OPEN_EXISTING,
		(bBackup)
		? FILE_FLAG_OPEN_REPARSE_POINT | FILE_FLAG_BACKUP_SEMANTICS
		: FILE_FLAG_OPEN_REPARSE_POINT, 0);
}

/** Multi-use functions for getting info on reparse points. **/

/**
 *@brief Get a reparse point buffer
 *@param [in] sFileName File name
 *@param [out] pBuf Caller allocated buffer (16 Kb minimum)
 *@return TRUE if success
 */
BOOL GetReparseBuffer(IN LPCTSTR sFileName, OUT PREPARSE_GUID_DATA_BUFFER pBuf)
{
	DWORD dwRet;
	HANDLE hSrc;
	BOOL bResult = FALSE;

	if (NULL == pBuf)
		return bResult;

	if (!IsReparsePoint(sFileName))
		return bResult;

	hSrc = OpenFileForRead(sFileName,
		(GetFileAttributes(sFileName) & FILE_ATTRIBUTE_DIRECTORY));

	if (hSrc == INVALID_HANDLE_VALUE)
		return bResult;

	if (DeviceIoControl(hSrc, FSCTL_GET_REPARSE_POINT,
		NULL, 0, pBuf, MAXIMUM_REPARSE_DATA_BUFFER_SIZE, &dwRet, NULL))
			bResult = TRUE;

	CloseHandle(hSrc);
	return bResult;
}

/**
 *@brief       Get a reparse tag of a reparse point
 *@param [in]  sFileName File name
 *@param [out] pTag Pointer to reparse tag
 *@return      TRUE if succeeded or FALSE if it fails
 */
BOOL GetReparseTag(IN LPCTSTR sFileName, OUT DWORD* pTag)
{
	PREPARSE_GUID_DATA_BUFFER rd;
	BOOL bResult = FALSE;

	if (NULL == pTag)
		return FALSE;

	if (!IsReparsePoint(sFileName))
		return FALSE;

	rd = (PREPARSE_GUID_DATA_BUFFER) GlobalAlloc(GPTR, MAXIMUM_REPARSE_DATA_BUFFER_SIZE);
	if (GetReparseBuffer(sFileName, rd)) {
		*pTag = rd->ReparseTag;
		bResult = TRUE;
	}

	GlobalFree(rd);
	return bResult;
}

/**
 *  @brief       Get a GUID field of a reparse point
 *  @param [in]  sFileName File name
 *  @param [out] pGuid Pointer to GUID
 *  @return      TRUE if success
 */
BOOL GetReparseGUID(IN LPCTSTR sFileName, OUT GUID* pGuid)
{
	PREPARSE_GUID_DATA_BUFFER rd;
	BOOL bResult = FALSE;

	if (pGuid == NULL || !IsReparsePoint(sFileName))
		return FALSE;

	
	rd = (PREPARSE_GUID_DATA_BUFFER) GlobalAlloc(GPTR, MAXIMUM_REPARSE_DATA_BUFFER_SIZE);

	if (GetReparseBuffer(sFileName, rd)) {
		*pGuid = rd->ReparseGuid;
		bResult = TRUE;
	}

	GlobalFree(rd);
	return bResult;
}

/** Multi-use functions for manipulating reparse points **/

/**
 *	@brief       Get a substitute name of a mount point, junction point or symbolic link
 *	@param [in]  sFileName File name
 *	@param [out] sBuffer Substitute name from the reparse buffer
 *	@param [in]  uBufferLength Length of the sBuffer buffer
 *	@return      TRUE if success, FALSE otherwise
 */
BOOL ReadReparsePoint(IN LPCTSTR sFileName, OUT LPWSTR sBuffer, IN USHORT uBufferLength)
{
	PREPARSE_DATA_BUFFER pReparse;
	DWORD dwTag;

	if ((NULL == sBuffer) || (0 == uBufferLength))
		return FALSE;

	if (!GetReparseTag((LPCTSTR)sFileName, &dwTag))
		return FALSE;

	// If not mount point, reparse point or symbolic link
	if ( ! ( (dwTag == IO_REPARSE_TAG_MOUNT_POINT) || (dwTag == IO_REPARSE_TAG_SYMLINK) ) )
		return FALSE;

	pReparse = (PREPARSE_DATA_BUFFER)
		GlobalAlloc(GPTR, MAXIMUM_REPARSE_DATA_BUFFER_SIZE);

	if (!GetReparseBuffer(sFileName, (PREPARSE_GUID_DATA_BUFFER)pReparse)) {
		GlobalFree(pReparse);
		return FALSE;
	}

	switch (dwTag)
	{
		case IO_REPARSE_TAG_MOUNT_POINT:
			if (uBufferLength >= pReparse->MountPointReparseBuffer.SubstituteNameLength) {
				memset(sBuffer, 0, uBufferLength);
				memcpy
				(
					sBuffer,
					&pReparse->MountPointReparseBuffer.PathBuffer
					[
					pReparse->MountPointReparseBuffer.SubstituteNameOffset / SZWCHAR
					],
					pReparse->MountPointReparseBuffer.SubstituteNameLength
				);
			} else {
				GlobalFree(pReparse);
				return FALSE;
			}
			break;
		case IO_REPARSE_TAG_SYMLINK:
			if (uBufferLength >= pReparse->SymbolicLinkReparseBuffer.SubstituteNameLength) {
				memset(sBuffer, 0, uBufferLength);
				memcpy
				(
					sBuffer,
					&pReparse->SymbolicLinkReparseBuffer.PathBuffer
					[
					pReparse->SymbolicLinkReparseBuffer.SubstituteNameOffset / SZWCHAR
					],
					pReparse->SymbolicLinkReparseBuffer.SubstituteNameLength
				);
			} else {
				GlobalFree(pReparse);
				return FALSE;
			}
			break;
	}
	
	GlobalFree(pReparse);
	return TRUE;
}

/**
 *  @brief      Delete a reparse point
 *  @param[in]  sFileName File name
 *  @return     TRUE if success, FALSE otherwise
 */
BOOL DeleteReparsePoint(IN LPCTSTR sFileName)
{
	PREPARSE_GUID_DATA_BUFFER rd;
	BOOL bResult;
	GUID gu;
	DWORD dwRet, dwReparseTag;
	HANDLE hDel;

	if (!IsReparsePoint(sFileName) || !GetReparseGUID(sFileName, &gu))
		return FALSE;

	rd = (PREPARSE_GUID_DATA_BUFFER)
		GlobalAlloc(GPTR, REPARSE_GUID_DATA_BUFFER_HEADER_SIZE);

	if (GetReparseTag(sFileName, &dwReparseTag)) {
		rd->ReparseTag = dwReparseTag;
	} else {
		//! The routine cannot delete a reparse point without determining it's reparse tag
		GlobalFree(rd);
		return FALSE;
	}

	hDel = OpenFileForWrite(sFileName,(GetFileAttributes(sFileName) & FILE_ATTRIBUTE_DIRECTORY));
	if (hDel == INVALID_HANDLE_VALUE)
		return FALSE;
	

	// Try to delete a system type of the reparse point (without GUID)
	bResult = DeviceIoControl(hDel, FSCTL_DELETE_REPARSE_POINT,
		rd, REPARSE_GUID_DATA_BUFFER_HEADER_SIZE, NULL, 0,
		&dwRet, NULL);

	if (!bResult) {
		// Set up the GUID
		rd->ReparseGuid = gu;
		// Try to delete with GUID
		bResult = DeviceIoControl(hDel, FSCTL_DELETE_REPARSE_POINT,
			rd, REPARSE_GUID_DATA_BUFFER_HEADER_SIZE, NULL, 0,
			&dwRet, NULL);
	}

	GlobalFree(rd);
	CloseHandle(hDel);
	return bResult;
}

/**
 *  @brief      Creates a custom reparse point
 *  @param[in]  sFileName   File name
 *  @param[in]  pBuffer     Reparse point content
 *  @param[in]  uBufSize    Size of the content
 *  @param[in]  uGuid       Reparse point GUID
 *  @param[in]  uReparseTag Reparse point tag
 *  @return     TRUE if success, FALSE otherwise
 */
BOOL CreateCustomReparsePoint
	(IN LPCTSTR sFileName, IN PVOID pBuffer, IN UINT uBufSize, IN GUID uGuid, IN ULONG uReparseTag)
{
	HANDLE hHandle; PREPARSE_GUID_DATA_BUFFER rd;
	DWORD dwLen = 0;
	BOOL bResult = FALSE;

	if (pBuffer == NULL || uBufSize == 0 || uBufSize > MAXIMUM_REPARSE_DATA_BUFFER_SIZE)
		return bResult;
	

	hHandle = OpenFileForWrite(sFileName, (GetFileAttributes(sFileName) & FILE_ATTRIBUTE_DIRECTORY));

	if (hHandle == INVALID_HANDLE_VALUE)
		return bResult;
	

	rd = (PREPARSE_GUID_DATA_BUFFER) GlobalAlloc(GPTR, MAXIMUM_REPARSE_DATA_BUFFER_SIZE);

	rd->ReparseTag = uReparseTag;
	rd->ReparseDataLength = uBufSize;
	rd->Reserved = 0;
	rd->ReparseGuid = uGuid;

	memcpy(rd->GenericReparseBuffer.DataBuffer, pBuffer, uBufSize);

	if (DeviceIoControl(hHandle, FSCTL_SET_REPARSE_POINT, rd,
		rd->ReparseDataLength + REPARSE_GUID_DATA_BUFFER_HEADER_SIZE,
		NULL, 0, &dwLen, NULL))
			bResult = TRUE;
	
	CloseHandle(hHandle);
	GlobalFree(rd);
	return bResult;
}

RESULT_CREATE CreateJunction(IN LPTSTR LinkTarget, IN LPTSTR LinkDirectory)
{
	char		reparseBuffer[MAX_PATH*3];
	TCHAR		volumeName[] = _T("X:\\");
	TCHAR		directoryFileName[MAX_PATH];
	TCHAR		fileSystem[MAX_PATH] = _T("");
	TCHAR		targetFileName[MAX_PATH];
	TCHAR		targetNativeFileName[MAX_PATH];
	HANDLE		hFile;
	WCHAR		creationPath[MAX_PATH];
	DWORD		returnedLength;
	FILE* logFile;
	PREPARSE_MOUNTPOINT_DATA_BUFFER reparseInfo = 
		(PREPARSE_MOUNTPOINT_DATA_BUFFER) reparseBuffer;

	// Validate target and new path.
	RESULT_CREATE result = AbsPaths(LinkDirectory, LinkTarget, directoryFileName, targetFileName);
	if(result != RESULT_SUCCESS)
		return result;

	// Make sure target is a folder.
	if(!IsFolder(targetFileName))
		return RESULT_INVALID_TARGET;
	
	// Make sure that directory is on NTFS volume
	volumeName[0] = directoryFileName[0];
	GetVolumeInformation( volumeName, NULL, 0, NULL, NULL, NULL, fileSystem,
		sizeof(fileSystem)/sizeof(TCHAR));
	
	if( _tcsicmp( _T("NTFS"), fileSystem))
		return RESULT_NOT_SUPPORTED;
	
	// Make the native target name
	_stprintf( targetNativeFileName, _T("\\??\\%s"), targetFileName );
	if ( (targetNativeFileName[_tcslen( targetNativeFileName )-1] == _T('\\')) &&
		 (targetNativeFileName[_tcslen( targetNativeFileName )-2] != _T(':')))
			targetNativeFileName[_tcslen( targetNativeFileName )-1] = 0;

	// Create the link - ignore errors since it might already exist
	CreateDirectory( LinkDirectory, NULL );
	hFile = CreateFile( LinkDirectory, GENERIC_WRITE, 0,
						NULL, OPEN_EXISTING, 
						FILE_FLAG_OPEN_REPARSE_POINT|FILE_FLAG_BACKUP_SEMANTICS, NULL );
	if( hFile == INVALID_HANDLE_VALUE )
		return RESULT_ERROR_CREATE;

	#ifndef UNICODE
		mbstowcs (creationPath, (const char *)targetNativeFileName, _tcslen(targetNativeFileName));
	#else
		creationPath = targetNativeFileName;
	#endif
	
	// Build the reparse info
	memset( reparseInfo, 0, sizeof( *reparseInfo ));
	reparseInfo->ReparseTag = IO_REPARSE_TAG_MOUNT_POINT;
	
	reparseInfo->ReparseTargetLength = wcslen( creationPath ) * sizeof(WCHAR);
	reparseInfo->ReparseTargetMaximumLength = reparseInfo->ReparseTargetLength + sizeof(WCHAR);
	wcscpy( reparseInfo->ReparseTarget, creationPath );
	reparseInfo->ReparseDataLength = reparseInfo->ReparseTargetLength + 12;

	// Set the link
	if( !DeviceIoControl( hFile, FSCTL_SET_REPARSE_POINT,
				reparseInfo, 
				reparseInfo->ReparseDataLength + REPARSE_MOUNTPOINT_HEADER_SIZE,
				NULL, 0, &returnedLength, NULL )) {
		CloseHandle( hFile );
		RemoveDirectory( LinkDirectory );
		return RESULT_ERROR_SET;
	}
	CloseHandle( hFile );
	return RESULT_SUCCESS;
}