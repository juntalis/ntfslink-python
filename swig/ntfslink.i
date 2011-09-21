/* File : junction.i */
%module(package="ntfslink") ntfslink

%pythoncode %{
__all__ = ['CREATE_ERROR_CREATE', 'CREATE_ERROR_SET', 'CREATE_INVALID_JUNCTION', 'CREATE_INVALID_TARGET', 'CREATE_NOT_SUPPORTED', 'CREATE_SUCCESS', 'DELETE_ERROR', 'DELETE_INVALID', 'DELETE_SUCCESS', 'junction', 'delete', 'is_junction', 'isdir','rm', 'rmdir', 'unlink', 'symlink', 'hardlink']
%}

%{
#define SWIG_FILE_WITH_INIT
#include "ntfslink.h"
%}

%include "typemaps.i"
%feature("autodoc", "1");
/* Let's just grab the original header file here */
%include "windows.i"
%include "ntfslink.h"

%pythoncode %{

def check(folder):
    """ Alias to junction.is_junction(folder) """
    return _ntfslink.is_junction(folder)

def rmdir(folder):
    """ Alias to junction.delete(folder) """
    return _ntfslink.delete(folder)

def rm(folder):
    """ Alias to junction.delete(folder) """
    return _ntfslink.delete(folder)
%}
