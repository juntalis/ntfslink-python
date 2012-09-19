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
	hFile = OpenFileForWrite(link_name, True)

	# Calculate the lengths of the names.
	lensubst = len(substlink) * SZWCHAR
	lenprint = len(source) * SZWCHAR

	# Construct our structure. Note: We have enter the fields one by one due tot he fact that we still need
	# to resize the PathBuffer field.
	reparseInfo = ReparsePoint()
	reparseInfo.ReparseTag = IO_REPARSE_TAG_MOUNT_POINT

	# reparseInfo.ReparseDataLength = datalen + 12
	reparseInfo.Reserved = 0
	reparseInfo.MountPoint = MountPointBuffer()
	reparseInfo.MountPoint.SubstituteNameOffset = 0
	reparseInfo.MountPoint.SubstituteNameLength	= lensubst
	reparseInfo.MountPoint.PrintNameOffset = lensubst + SZWCHAR # Ending \0
	reparseInfo.MountPoint.PrintNameLength = lenprint

	(bufflen, reparseInfo.ReparseDataLength) = CalculateLength(MountPointBuffer, reparseInfo.MountPoint)

	# Assign the PathBuffer, then resize it, etc.
	reparseInfo.MountPoint.PathBuffer = u'%s\0%s' % (substlink, source)
	pReparseInfo = pointer(reparseInfo)
	reparseInfo.MountPoint._fields_[4] = ('PathBuffer', bufflen)
	returnedLength = DWORD(0)
	result = DeviceIoControl(
		hFile, FSCTL_SET_REPARSE_POINT, pReparseInfo,
		reparseInfo.ReparseDataLength + REPARSE_MOUNTPOINT_HEADER_SIZE,
		None, 0, byref(returnedLength), None
	) != FALSE

	CloseHandle(hFile)
	if not result: RemoveDirectory(link_name)
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

	hFile = OpenFileForRead(fpath, True)

	dwRet = DWORD()
	reparseInfo = ReparsePoint()
	result = DeviceIoControl(
		hFile, FSCTL_GET_REPARSE_POINT, None, 0L,
		byref(reparseInfo), MAX_REPARSE_BUFFER, byref(dwRet), None
	) != FALSE

	CloseHandle(hFile)
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

	hFile = OpenFileForWrite(fpath, True)
	dwRet = DWORD()

	# Try to delete it first without the reparse GUID
	reparseInfo = ReparsePoint()
	reparseInfo.ReparseTag = IO_REPARSE_TAG_MOUNT_POINT
	result = DeviceIoControl(
		hFile,
		FSCTL_DELETE_REPARSE_POINT,
		byref(reparseInfo),
		REPARSE_MOUNTPOINT_HEADER_SIZE,
		None, 0L, byref(dwRet), None
	) != FALSE

	if not result:
		# If the first try fails, we'll set the GUID and try again
		# TODO: Reimplement some of these to use the GUID class.
		raise WinError()

	CloseHandle(hFile)
	if result: RemoveDirectory(fpath)
	return result, dwRet

def example():
	import os
	sfolder = '/Temp'
	sjunction = 'temp'
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

	print 'create(%s, %s)' % (sfolder, sjunction), create(sfolder, sjunction)
	print 'check(%s)' % sjunction, check(sjunction)
	# For some reason, having read() directly followed by unlink results in the read function not returning correctly.
	# I'll try to figure it out, but since most use cases wont need to read a junction and immediately delete it,
	# I probably won't put much time into it.
	buffer = read(sjunction)
	if buffer is not None:
		import pprint
		pprint.pprint('read(%s) %s' % (sjunction, buffer))
	raw_input('Press any key to delete the "%s" junction.' % sjunction)
	print 'unlink(%s)' % sjunction, unlink(sjunction)

	if removeTemporaryFolder:
		print 'Removing the temporary folder created at %s.' % path.abspath(sfolder)
		os.rmdir(sfolder)

if __name__=='__main__':
	example()