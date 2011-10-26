/* File : ntfslink.i */

// Module docstring.
%define DOCSTRING
"Simple python module wrapping some of the Win32 API to allow support for
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

"
%enddef

// Specify our module.
%module(package="ntfslink", docstring=DOCSTRING) ntfslink

// Turn off auto-documentation.
%feature("autodoc", "0");

//Exports, etc.
%pythoncode %{
__all__ = ['isjunction', 'link', 'symlink', 'junction', 'readjunction', 'rmdir', 'unlink']
%}

// Unparsed C++.
%{
#define SWIG_FILE_WITH_INIT
#include "ntfslink.h"
%}

%include "windows.i"

// IsJunction - Straight call
%feature("autodoc", "isjunction(folder) -> bool") IsJunction;
%feature("docstring", "True if path refers to a directory/file entry that is a symbolic link.") IsJunction;
%rename(isjunction) IsJunction;
extern bool IsJunction(LPTSTR);


// CreateHardLink - Wrapper
%{
bool link(LPTSTR source, LPTSTR link) {
	return CreateHardLink(source, link) == create_success;
}
%}
%feature("autodoc", "link(source, link_name) -> bool") link;
%feature("docstring", "\n        Create a hard link pointing to source named link_name.\n\n        Returns boolean indicating success.\n        ") link;
bool link(LPTSTR,LPTSTR);


// CreateSymbolicLink - Wrapper
%{
bool symlink(LPTSTR source, LPTSTR link) {
	return CreateSymbolicLink(source, link) == create_success;
}
%}
%feature("autodoc", "symlink(source, link_name) -> bool") symlink;
%feature("docstring", "\n        Create a symbolic link pointing to source named link_name.\n\n        Returns boolean indicating success.\n        ") symlink;
bool symlink(LPTSTR, LPTSTR);


// CreateJunction - Wrapper
%{
bool junction(LPTSTR source, LPTSTR link) {
	return CreateJunction(source, link) == create_success;
}
%}
%feature("autodoc", "junction(source, link_name) -> bool") junction;
%feature("docstring", "\n        Create a junction pointing to source named link_name.\n\n        Returns boolean indicating success.\n        ") junction;
bool junction(LPTSTR, LPTSTR);


// ReadJunction - Straight call
%feature("autodoc", "readjunction(folder) -> string") ReadJunction;
%feature("docstring", " Return a string representing the path to which the symbolic link points\n    or an empty string on failure/non-existant junction. ") ReadJunction;
%rename(readjunction) ReadJunction;
extern LPTSTR ReadJunction(LPTSTR);


// DeleteJunctionRecord - Wrapper
%{
bool unlink(LPTSTR pszDir) {
	return DeleteJunctionRecord(pszDir) == delete_success;
}
%}
%feature("autodoc", "unlink(folder) -> bool") unlink;
%feature("docstring", "\n    Remove a junction point record or \"reparse point\" from a folder.\n    \n    NOTE: An empty folder will remain where the junction point was. To remove the reparse point and\n    delete the remaining folder, use ntfslink.rmdir()\n    \n    Returns boolean indicating success.\n    ") unlink;
bool unlink(LPTSTR);


// DeleteJunction - Wrapper
%{
bool rmdir(LPTSTR pszDir) {
	return DeleteJunction(pszDir) == delete_success;
}
%}
%feature("autodoc", "rmdir(folder) -> bool") rmdir;
%feature("docstring", "\n    Remove a junction point folder.\n    \n    NOTE: Use this, not shutil.rmtree or os.removedirs. Those will delete the\n    contents of the target folder, in addition to the junction point.\n    \n    Returns boolean indicating success.\n    ") rmdir;
bool rmdir(LPTSTR);

