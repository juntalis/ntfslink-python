#include "ntfslink.h"
#include <Shlwapi.h>
#include <tchar.h>
#include <mbstring.h>

// Maximum reparse point name size
#define MAX_NAME_LENGTH		1024
// Shortcut
#define DIR_ATTR	(FILE_ATTRIBUTE_DIRECTORY | FILE_ATTRIBUTE_REPARSE_POINT)
// The link target is a file.
#define SYMLINK_FILE 0x0
// The link target is a directory.
#define SYMLINK_DIR 0x1

bool IsFolder(LPTSTR pszPath)
{
	DWORD dwAttr = GetFileAttributes(pszPath);
	if(dwAttr & FILE_ATTRIBUTE_DIRECTORY) return true;
	return false;
}


create_result CheckPaths(LPTSTR newPath, LPTSTR targetPath, LPTSTR outPath, LPTSTR outTarget)
{
	PTCHAR		filePart;
		// Get the full path referenced by the target
	if( !GetFullPathName(targetPath, MAX_PATH, outTarget, &filePart ))
		return create_invalid_target;

	// Get the full path referenced by the directory
	if( !GetFullPathName(newPath, MAX_PATH, outPath, &filePart ))
		return create_invalid_path;
	
	if(!PathFileExists(outTarget))
		return create_invalid_target;
	
	return create_success;
}


HANDLE OpenDirectory(LPCTSTR pszPath, BOOL bReadWrite)
{
	// Obtain restore privilege in case we don't have it
	HANDLE hToken;
	TOKEN_PRIVILEGES tp;
	::OpenProcessToken(::GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES, &hToken);
	::LookupPrivilegeValue(NULL,
						 (bReadWrite ? SE_RESTORE_NAME : SE_BACKUP_NAME),
						 &tp.Privileges[0].Luid);
	tp.PrivilegeCount = 1;
	tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;
	::AdjustTokenPrivileges(hToken, FALSE, &tp, sizeof(TOKEN_PRIVILEGES), NULL, NULL);
	::CloseHandle(hToken);

	// Open the directory
	DWORD dwAccess = bReadWrite ? (GENERIC_READ | GENERIC_WRITE) : GENERIC_READ;
	HANDLE hDir = ::CreateFile(pszPath, dwAccess, 0, NULL, OPEN_EXISTING,
					 FILE_FLAG_OPEN_REPARSE_POINT | FILE_FLAG_BACKUP_SEMANTICS, NULL);

	return hDir;
}


bool IsJunction(LPTSTR pszDir)
{
	DWORD dwAttr = ::GetFileAttributes(pszDir);
	if (dwAttr == -1) return false;	// Not exists
	if ((dwAttr & DIR_ATTR) != DIR_ATTR) return false;	// Not dir or no reparse point

	HANDLE hDir = OpenDirectory(pszDir, FALSE);
	if (hDir == INVALID_HANDLE_VALUE) return false;	// Failed to open directory

	BYTE buf[MAXIMUM_REPARSE_DATA_BUFFER_SIZE];
	REPARSE_MOUNTPOINT_DATA_BUFFER& ReparseBuffer = (REPARSE_MOUNTPOINT_DATA_BUFFER&)buf;
	DWORD dwRet;
	BOOL br = ::DeviceIoControl(hDir, FSCTL_GET_REPARSE_POINT, NULL, 0, &ReparseBuffer,
										MAXIMUM_REPARSE_DATA_BUFFER_SIZE, &dwRet, NULL);
	::CloseHandle(hDir);
	return br ? (ReparseBuffer.ReparseTag == IO_REPARSE_TAG_MOUNT_POINT) : false;
}


delete_result DeleteJunctionRecord(LPTSTR pszDir)
{
	if(!IsJunction(pszDir))
		return delete_invalid;
	HANDLE hDir = OpenDirectory(pszDir, TRUE);

	BYTE buf[REPARSE_MOUNTPOINT_HEADER_SIZE];
	REPARSE_MOUNTPOINT_DATA_BUFFER& ReparseBuffer = (REPARSE_MOUNTPOINT_DATA_BUFFER&)buf;
	DWORD dwRet;
	memset(buf, 0, sizeof(buf));
	ReparseBuffer.ReparseTag = IO_REPARSE_TAG_MOUNT_POINT;

	if (!::DeviceIoControl(hDir, FSCTL_DELETE_REPARSE_POINT, &ReparseBuffer, REPARSE_MOUNTPOINT_HEADER_SIZE, NULL, 0, &dwRet, NULL)) {
		return delete_error;
	}
	::CloseHandle(hDir);
	return delete_success;
}


delete_result DeleteJunction(LPTSTR pszDir)
{
	delete_result result = DeleteJunctionRecord(pszDir);
	if(result != delete_success) return result;
	if(RemoveDirectory(pszDir)) return delete_success;
	else return delete_error;
}


create_result CreateJunction(LPTSTR LinkTarget, LPTSTR LinkDirectory)
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
	PREPARSE_MOUNTPOINT_DATA_BUFFER reparseInfo = 
		(PREPARSE_MOUNTPOINT_DATA_BUFFER) reparseBuffer;

	// Validate target and new path.
	create_result result = CheckPaths(LinkDirectory, LinkTarget, directoryFileName, targetFileName);
	if(result != create_success)
		return result;

	// Make sure target is a folder.
	if(!IsFolder(targetFileName))
		return create_invalid_target;
	
	// Make sure that directory is on NTFS volume
	volumeName[0] = directoryFileName[0];
	GetVolumeInformation( volumeName, NULL, 0, NULL, NULL, NULL, fileSystem,
		sizeof(fileSystem)/sizeof(TCHAR));
	
	if( _tcsicmp( _T("NTFS"), fileSystem))
		return create_not_supported;
	
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
		return create_error_create;

	#ifndef UNICODE
		mbstowcs (creationPath, (const char *)targetNativeFileName, sizeof(targetNativeFileName)/sizeof(TCHAR));
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
		return create_error_set;
	}
	CloseHandle( hFile );
	return create_success;
}


create_result CreateHardLink(LPTSTR LinkTarget, LPTSTR LinkPath)
{
	TCHAR		pathFileName[MAX_PATH];
	TCHAR		targetFileName[MAX_PATH];

	create_result result = CheckPaths(LinkPath, LinkTarget, pathFileName, targetFileName);
	if(result != create_success)
		return result;
	
	if(IsFolder(targetFileName))
		return create_invalid_target;
	
	if(!CreateHardLink(pathFileName, targetFileName, NULL))
		return create_error_create;
	
	return create_success;
}


create_result CreateSymbolicLink(LPTSTR LinkTarget, LPTSTR LinkPath)
{
	TCHAR		pathFileName[MAX_PATH];
	TCHAR		targetFileName[MAX_PATH];
	
	create_result result = CheckPaths(LinkPath, LinkTarget, pathFileName, targetFileName);
	if(result != create_success)
		return result;
	
	DWORD dwFlags = IsFolder(targetFileName) ? SYMLINK_DIR : SYMLINK_FILE;
	if(!CreateSymbolicLink(pathFileName, targetFileName, dwFlags))
		return create_error_create;
	
	return create_success;
}


LPTSTR ReadJunction(LPTSTR szJunction)
{
		TCHAR szPath[MAX_PATH];

		if (!IsJunction(szJunction)) {
			return NULL;
		}

		// Open for reading only (see OpenDirectory definition above)
		HANDLE hDir = OpenDirectory(szJunction, FALSE);

		BYTE buf[MAXIMUM_REPARSE_DATA_BUFFER_SIZE];	// We need a large buffer
		REPARSE_MOUNTPOINT_DATA_BUFFER& ReparseBuffer = (REPARSE_MOUNTPOINT_DATA_BUFFER&)buf;
		DWORD dwRet;

		if (DeviceIoControl(hDir, FSCTL_GET_REPARSE_POINT, NULL, 0, &ReparseBuffer,
										 MAXIMUM_REPARSE_DATA_BUFFER_SIZE, &dwRet, NULL)) {
			// Success
			CloseHandle(hDir);

			LPCWSTR pPath = ReparseBuffer.ReparseTarget;
			if (wcsncmp(pPath, L"\\??\\", 4) == 0) pPath += 4;	// Skip 'non-parsed' prefix
			#ifndef UNICODE
			WideCharToMultiByte(CP_ACP, 0, pPath, -1, szPath, MAX_PATH, NULL, NULL);
			#endif
		}
		else {	// Error
			DWORD dr = ::GetLastError();
			CloseHandle(hDir);
			return NULL;
		}
		
		return szPath;
}
