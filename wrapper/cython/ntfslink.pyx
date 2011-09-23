r"""
Simple python module wrapping some of the Win32 API to allow support for
junctions, symbolic links, and hardlinks. For information on junctions, see the
MSDN entry on `Junction Points<http://msdn.microsoft.com/en-us/library/bb968829%28VS.85%29.aspx>`_, `Hard Links<http://msdn.microsoft.com/en-us/library/aa365006%28v=VS.85%29.aspx>`_,
and `Symbolic Links<http://msdn.microsoft.com/en-us/library/aa365680%28v=VS.85%29.aspx>`_

TODO:
- Find a way to implement the following functions:

    ntfslink.readlink(path)
      Return a string representing the path to which the symbolic link points.

    ntfslink.islink(path)
      Return True if path refers to a directory/file entry that is a symbolic
      link.

- Look into wrapping `Volume Mount Points<http://msdn.microsoft.com/en-us/library/aa365733%28v=VS.85%29.aspx>`_.

- Look into wrapping `Wow64FsRedirection<http://msdn.microsoft.com/en-us/library/aa365744%28v=VS.85%29.aspx>`_.

- Write a python module to direct calls to the correct modules depending on
  current operating system.

"""
DEF UNICODE = 0
IF UNICODE == 1:
	cimport python_unicode
	cdef extern from "windows.h":
		# If UNICODE is defined, we'll be using LPWSTRs
		ctypedef unicode LPTSTR
ELSE:
	cdef extern from "windows.h":
		# Otherwise, we'll be using LPCSTRs
		ctypedef char* LPTSTR

# Just to make things a bit prettier.
ctypedef LPTSTR tstring
ctypedef int bool

# Import our C++ code.
cdef extern from "ntfslink.h":
	
	# Result enums.
	ctypedef enum create_result:
		create_success = 1
		create_invalid_target = 0
		create_invalid_path = -1
		create_not_supported = -2
		create_error_create = -3
		create_error_set = -4
	ctypedef enum delete_result:
		delete_success = 1
		delete_invalid = 0
		delete_error = -1
	
	# Functions
	bool IsJunction(tstring)
	create_result CreateHardLink(tstring,tstring)
	create_result CreateSymbolicLink(tstring,tstring)
	create_result CreateJunction(tstring,tstring)
	tstring ReadJunction(tstring)
	delete_result DeleteJunctionRecord(tstring)
	delete_result DeleteJunction(tstring)
	

cpdef object isjunction(tstring folder):
	""" Return True if path refers to a directory/file entry that is a symbolic link. """
	return IsJunction(folder) == 1

cpdef object link(tstring source, tstring link_name):
	"""
	Create a hard link pointing to source named link_name.
	
	Returns boolean indicating success.
	"""
	result = CreateHardLink(source, link_name)
	return result == create_success

cpdef object symlink(tstring source, tstring link_name):
	"""
	Create a symbolic link pointing to source named link_name.
	
	Returns boolean indicating success.
	"""
	result = CreateSymbolicLink(source, link_name)
	return result == create_success

cpdef object junction(tstring source, tstring link_name):
	"""
	Create a junction pointing to source named link_name.
	
	Returns boolean indicating success.
	"""
	result = CreateJunction(source, link_name)
	return result == create_success

cdef tstring read_junction(tstring folder):
	return ReadJunction(folder)

def readjunction(folder):
	""" Return a string representing the path to which the symbolic link points, or an empty string. """
	if folder is None:
		return ''
	result = read_junction(folder)
	if result is None:
		return ''
	return str(result)

cpdef object unlink(tstring folder):
	"""
	Remove a junction point record or "reparse point" from a folder.
	
	NOTE: An empty folder will remain where the junction point was. To remove the reparse point and
	delete the remaining folder, use ntfslink.rmdir()
	
	Returns boolean indicating success.
	"""
	result = DeleteJunctionRecord(folder)
	
	return result == delete_success

cpdef object rmdir(tstring folder):
	"""
	Remove a junction point folder.
	
	WARNING: Use this, not shutil.rmtree or os.removedirs. Those will delete the contents of the target
	folder, in addition to the junction point.
	
	Returns boolean indicating success.
	"""
	result = DeleteJunction(folder)
	
	return result == delete_success