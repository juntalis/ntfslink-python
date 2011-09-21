/* File : junction.i */
%module(package="junction") junction
%pythoncode %{
__name__ = 'junction'
__version__ = '1.0'
__author__ = 'Charles Grunwald (Juntalis) <cgrunwald@gmail.com>'
__all__ = ['CREATE_ERROR_CREATE', 'CREATE_ERROR_SET', 'CREATE_INVALID_JUNCTION', 'CREATE_INVALID_TARGET', 'CREATE_NOT_SUPPORTED', 'CREATE_SUCCESS', 'DELETE_ERROR', 'DELETE_INVALID', 'DELETE_SUCCESS', 'create', 'delete', 'is_junction', 'isdir','rm', 'rmdir', 'unlink']
%}
%{
#define SWIG_FILE_WITH_INIT
#include "junction.h"
%}

%include "typemaps.i"
%feature("autodoc", "1");
/* Let's just grab the original header file here */
%include "windows.i"
%include "junction.h"

%pythoncode %{

def isdir(folder):
    """ Alias to junction.is_junction(folder) """
    return _junction.is_junction(folder)

def check(folder):
    """ Alias to junction.is_junction(folder) """
    return _junction.is_junction(folder)

def rmdir(folder):
    """ Alias to junction.delete(folder) """
    return _junction.delete(folder)

def rm(folder):
    """ Alias to junction.delete(folder) """
    return _junction.delete(folder)
%}
