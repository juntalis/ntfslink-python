from common import *

__all__ = ['create', 'check', 'read', 'unlink']

def create(source, link_name):
	"""
	Create a junction at link_name pointing to source directory.

	See: os.symlink
	"""
	source = str(source).strip('\0 ')
	link_name = str(link_name).strip('\0 ')
	if not path.isdir(source):
		raise Exception('Junction source does not exist or is not a directory.')

	link_name = path.abspath(link_name)
	if path.exists(link_name):
		raise Exception('Filepath for new junction already exists.')

	if not CreateDirectory(link_name):
		raise Exception('Failed to create new directory for target junction.')

	# SubstituteName
	substlink = TranslatePath(source)
	ObtainRestorePrivilege(True)
	hFile = CreateFile(link_name, GENERIC_WRITE, FILE_SHARE_READ_WRITE, OPEN_EXISTING, FILE_FLAG_REPARSE_BACKUP)
	if hFile == HANDLE(INVALID_HANDLE_VALUE):
		raise InvalidHandleException('Failed to open directory for junction creation.')

	# Calculate the lengths of the names.
	lensubst = len(substlink) * sizeof(c_wchar)
	lenprint = len(source) * sizeof(c_wchar)

	# Construct our structure. Note: We have enter the fields one by one due tot he fact that we still need
	# to resize the PathBuffer field.
	reparseInfo = ReparsePoint()
	reparseInfo.ReparseTag = IO_REPARSE_TAG_MOUNT_POINT

	# reparseInfo.ReparseDataLength = datalen + 12
	reparseInfo.Reserved = 0
	reparseInfo.MountPoint = MountPointBuffer()
	reparseInfo.MountPoint.SubstituteNameOffset = 0
	reparseInfo.MountPoint.SubstituteNameLength	= lensubst
	reparseInfo.MountPoint.PrintNameOffset = lensubst + sizeof(c_wchar) # Ending \0
	reparseInfo.MountPoint.PrintNameLength = lenprint

	(bufflen, reparseInfo.ReparseDataLength) = CalculateLength(MountPointBuffer, reparseInfo.MountPoint)

	# Assign the PathBuffer, then resize it, etc.
	reparseInfo.MountPoint.PathBuffer = u'%s\0%s' % (substlink, source)
	pReparseInfo = pointer(reparseInfo)
	reparseInfo.MountPoint._fields_[4] = ('PathBuffer', bufflen)
	returnedLength = DWORD(0)
	result = BOOL(
		windll.kernel32.DeviceIoControl(
			hFile,
			DWORD(FSCTL_SET_REPARSE_POINT),
			pReparseInfo,
			DWORD(reparseInfo.ReparseDataLength + REPARSE_MOUNTPOINT_HEADER_SIZE),
			LPVOID(NULL),
			DWORD(0),
			byref(returnedLength),
			LPOVERLAPPED(NULL)
		)
	) != FALSE

	windll.kernel32.CloseHandle(hFile)
	if not result:
		RemoveDirectory(link_name)

	return result

def check(fpath):
	"""
	Checks if fpath is a junction.

	See: os.path.islink
	"""
	return IsReparseDir(fpath)

def read(fpath):
	"""
	Read the target of the junction at fpath.

	See: os.readlink
	"""
	if not check(fpath):
		raise InvalidLinkException("%s is not a junction." % fpath)

	ObtainRestorePrivilege()
	hFile = CreateFile(fpath, GENERIC_READ, FILE_SHARE_READ, OPEN_EXISTING, FILE_FLAG_REPARSE_BACKUP)

	if hFile == HANDLE(INVALID_HANDLE_VALUE):
		raise InvalidHandleException('Failed to open directory for junction reading.')

	dwRet = DWORD()
	reparseInfo = ReparsePoint()
	result = BOOL(
		windll.kernel32.DeviceIoControl(
			hFile,
			DWORD(FSCTL_GET_REPARSE_POINT),
			None,
			DWORD(0),
			byref(reparseInfo),
			DWORD(MAX_REPARSE_BUFFER),
			byref(dwRet),
			LPOVERLAPPED(NULL)
		)
	) != FALSE

	windll.kernel32.CloseHandle(hFile)
	if result:
		# Unfortunately I cant figure out a way to get the PrintName. The problem is, PathBuffer should currently
		# contain a c_wchar array that holds SubstituteName\0PrintName\0. Unfortunately, since it automatically
		# converts it to a unicode string, I've been unable to figure out a way to access the data past the first
		# terminating \0. So instead, we'll just use the SubstituteName and remove the \??\ from the front.
		target = str(reparseInfo.MountPoint.PathBuffer)
		if target[:4] == '\\??\\':
			target = target[4:]
		return target

	return None


def unlink(fpath):
	"""
	Remove the junction at fpath.

	See: os.rmdir
	"""
	if not check(fpath):
		raise InvalidLinkException("%s is not a junction." % fpath)

	ObtainRestorePrivilege()
	hFile = CreateFile(fpath, GENERIC_READ, FILE_SHARE_DELETE, OPEN_EXISTING, FILE_FLAG_REPARSE_BACKUP)

	if hFile == HANDLE(INVALID_HANDLE_VALUE):
		raise InvalidHandleException('Failed to open directory for junction reading.')

	dwRet = DWORD()
	reparseInfo = ReparsePoint()
	reparseInfo.ReparseTag = IO_REPARSE_TAG_MOUNT_POINT
	result = BOOL(
		windll.kernel32.DeviceIoControl(
			hFile,
			DWORD(FSCTL_DELETE_REPARSE_POINT),
			byref(reparseInfo),
			DWORD(REPARSE_MOUNTPOINT_HEADER_SIZE),
			LPVOID(NULL),
			DWORD(0),
			byref(dwRet),
			LPOVERLAPPED(NULL)
		)
	) != FALSE

	windll.kernel32.CloseHandle(hFile)
	if result:
		RemoveDirectory(fpath)

	return result

def example():
	import os
	sfolder = '/Temp'
	if path.isfile(sfolder):
		import random
		while path.isfile(sfolder):
			sfolder += '%d' % int(random.uniform(1, 10))

	print 'Junction Example'
	removeTemporaryFolder = False
	if not path.isdir(sfolder):
		os.mkdir(sfolder)
		print 'Temporarily created %s folder for the purpose of this example.' % path.abspath(sfolder)
		removeTemporaryFolder = True

	print 'create(%s, \'temp\')' % sfolder, create(sfolder, 'temp')
	print 'check(\'temp\')', check('temp')
	# For some reason, having read() directly followed by unlink results in the read function not returning correctly.
	# I'll try to figure it out, but since most use cases wont need to read a junction and immediately delete it,
	# I probably won't put much time into it.
	buffer = read('temp')
	if buffer is not None:
		import pprint
		pprint.pprint('read(\'temp\') %s' % buffer)
	raw_input('Press any key to delete the \'temp\' junction.')
	print 'unlink(\'temp\')', unlink('temp')

	if removeTemporaryFolder:
		print 'Removing the temporary folder created at %s.' % path.abspath(sfolder)
		os.rmdir(sfolder)





if __name__=='__main__':
	example()