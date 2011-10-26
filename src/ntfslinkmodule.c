
#include "Python.h"
#include "ntfslink.h"

/** Helpers for working with the arguments incoming from Python **/

/**
 *@brief Turn a char* into a LPTSTR (whatever it currently is)
 *@param [in] sInput char* to target
 *@param [out] sResult Output buffer pointer. Should be null. (will alloc if needed)
 *@param [in] szLength size_t containing the length of the string.
*/
BOOL NormalizeInput(IN char* sInput, OUT LPTSTR* sResult, IN size_t szLength)
{
	#ifdef UNICODE
		*sResult = (LPTSTR)
			GlobalAlloc(GPTR, SZWCHAR * (szLength+1));
		if(*sResult == NULL) return FALSE;
		mbstowcs(*(LPWSTR*)sResult, sInput, szLength);
	#else
		*sResult = (LPTSTR)sInput;
	#endif
	return TRUE;
}

/**
 *@brief Deallocate previous allocated buffer if necessary.
 *@param [in] sBuffer char* to target
*/
VOID CleanupStr(IN LPTSTR* sInput)
{
	#ifdef UNICODE
		if(sInput != NULL)
			GlobalFree(sInput);
	#endif
	return;
}

/**
 * And now for the python module code, etc.
 */
PyDoc_STRVAR(ntfslink_islink_doc,
" NOTE: Just noticed that Python has support for this on Windows in the current version.. Huh.\nDetermine whether the file is a symbolic link.\nSee: os.path.islink\n"
);
static PyObject * ntfslink_islink(PyObject *self, PyObject *args)
{
	char* input; size_t slen; DWORD dwTag; LPTSTR sFileName = NULL;
	PyObject* result = Py_False;
	if (!PyArg_ParseTuple(args, "s#:islink", &input, &slen))
		Py_RETURN_FALSE;
	
	if(!NormalizeInput(input, &sFileName, slen))
		Py_RETURN_FALSE;
	
	if (IsReparsePoint((LPCTSTR)sFileName))
		if (GetReparseTag((LPCTSTR)sFileName, &dwTag))
			if(dwTag == IO_REPARSE_TAG_SYMLINK)
				result = Py_True;
	
	CleanupStr(sFileName);
	return result;
}

PyDoc_STRVAR(ntfslink_isjunction_doc,
" Determine whether the folder is a junction. \n See: os.path.islink/ospath.ismount\n"
);
static PyObject * ntfslink_isjunction(PyObject *self, PyObject *args)
{
	char* input; size_t slen; DWORD dwTag; LPTSTR sFileName = NULL;
	PyObject* result = Py_False;
	if (!PyArg_ParseTuple(args, "s#:isjunction", &input, &slen))
		Py_RETURN_FALSE;
	
	if(!NormalizeInput(input, &sFileName, slen))
		Py_RETURN_FALSE;
	
	if (IsReparseDir((LPCTSTR)sFileName))
		if (GetReparseTag((LPCTSTR)sFileName, &dwTag))
			if(dwTag == IO_REPARSE_TAG_MOUNT_POINT)
				result = Py_True;
	
	CleanupStr(sFileName);
	return result;
}

PyDoc_STRVAR(ntfslink_readlink_doc,
" Reads in a the file path of a symbolic link or junction and returns the path to its target. (Or None if invalid)\nSee: os.readlink\n"
);
static PyObject * ntfslink_readlink(PyObject *self, PyObject *args)
{
	char* input; size_t slen; LPTSTR sFileName = NULL;
	size_t targlen; WCHAR buffer[MAX_PATH];
	char* cresult; PyObject * result = Py_None;
	
	if (!PyArg_ParseTuple(args, "s#:readlink",  &input, &slen))
		return result;
	
	if(!NormalizeInput(input, &sFileName, slen))
		return result;
	
	if(ReadReparsePoint(sFileName, (LPWSTR)&buffer, (USHORT)MAX_PATH)) {
		targlen = wcslen((LPCWSTR)buffer);
		cresult = (char*)GlobalAlloc(GPTR, SZCHAR * targlen);
		wcstombs(cresult, (LPCWSTR)buffer, targlen);
		result = PyString_FromStringAndSize(cresult, targlen);
		GlobalFree(cresult);
	}
	
	CleanupStr(sFileName);
	return result;
}

PyDoc_STRVAR(ntfslink_link_doc,
" Create a hard link pointing to source named link_name.\nReturns boolean indicating success.\nSee: os.link\n"
);
static PyObject * ntfslink_link(PyObject *self, PyObject *args)
{
	char* inputSrc; size_t srclen;
	char* inputLink; size_t linklen;
	LPTSTR srcFileName = NULL; LPTSTR linkFileName = NULL;
	TCHAR linkAbsFilename[MAX_PATH];
	TCHAR srcAbsFileName[MAX_PATH];
	PyObject* result = Py_False;
	
	if (!PyArg_ParseTuple(args, "s#s#:link", &inputSrc, &srclen, &inputLink, &linklen))
		Py_RETURN_FALSE;
	
	if(!NormalizeInput(inputSrc, &srcFileName, srclen))
		Py_RETURN_FALSE;
	
	if(!NormalizeInput(inputLink, &linkFileName, linklen)) {
		CleanupStr(srcFileName);
		Py_RETURN_FALSE;
	}

	if(AbsPaths(linkFileName, srcFileName, linkAbsFilename, srcAbsFileName) == RESULT_SUCCESS)
		if(!IsFolder(srcAbsFileName))
			if(CreateHardLink(linkAbsFilename, srcAbsFileName, NULL))
				result = Py_True;
	
	CleanupStr(srcFileName);
	CleanupStr(linkFileName);
	return result;
}

PyDoc_STRVAR(ntfslink_symlink_doc,
" Create a symbolic link pointing to source named link_name.\nReturns boolean indicating success.\nSee: os.symlink\n"
);
static PyObject * ntfslink_symlink(PyObject *self, PyObject *args)
{
	char* inputSrc; size_t srclen;
	char* inputLink; size_t linklen;
	LPTSTR srcFileName = NULL; LPTSTR linkFileName = NULL;
	TCHAR linkAbsFilename[MAX_PATH];
	TCHAR srcAbsFileName[MAX_PATH];
	DWORD dwFlags;
	PyObject* result = Py_False;
	
	if (!PyArg_ParseTuple(args, "s#s#:symlink", &inputSrc, &srclen, &inputLink, &linklen))
		Py_RETURN_FALSE;
	
	if(!NormalizeInput(inputSrc, &srcFileName, srclen))
		Py_RETURN_FALSE;
	
	if(!NormalizeInput(inputLink, &linkFileName, linklen)) {
		CleanupStr(srcFileName);
		Py_RETURN_FALSE;
	}

	if(AbsPaths(linkFileName, srcFileName, linkAbsFilename, srcAbsFileName) == RESULT_SUCCESS) {
		dwFlags = IsFolder(srcAbsFileName) ? SYMLINK_DIR : SYMLINK_FILE;
		if(CreateSymbolicLink(linkAbsFilename, srcAbsFileName, dwFlags))
			result = Py_True;
	}
	CleanupStr(srcFileName);
	CleanupStr(linkFileName);
	return result;
}

PyDoc_STRVAR(ntfslink_junction_doc,
" Create a junction point pointing to source named link_name.\nReturns boolean indicating success.\nSee: os.symlink\n"
);
static PyObject * ntfslink_junction(PyObject *self, PyObject *args)
{
	char* inputSrc; size_t srclen;
	char* inputLink; size_t linklen;
	LPTSTR srcFileName = NULL; LPTSTR linkFileName = NULL;
	PyObject* result = Py_False;
	
	if (!PyArg_ParseTuple(args, "s#s#:junction", &inputSrc, &srclen, &inputLink, &linklen)) {
		Py_RETURN_FALSE;
	}
	
	if(!NormalizeInput(inputSrc, &srcFileName, srclen))
		Py_RETURN_FALSE;
	
	if(!NormalizeInput(inputLink, &linkFileName, linklen)) {
		CleanupStr(srcFileName);
		Py_RETURN_FALSE;
	}

	if(CreateJunction(srcFileName, linkFileName) == RESULT_SUCCESS)
		result = Py_True;
		
	CleanupStr(srcFileName);
	CleanupStr(linkFileName);
	return result;
}

PyDoc_STRVAR(ntfslink_unlink_doc,
" Remove a junction point record, symbolic link, or \"reparse point\" from a folder/file.\nNOTE: For junction points, it also removes the blank folder after removing the record.\nReturns boolean indicating success.\n"
);
static PyObject * ntfslink_unlink(PyObject *self, PyObject *args)
{
	char* input; size_t slen; DWORD dwTag; LPTSTR sFileName = NULL;
	PyObject* result = Py_False;
	if (!PyArg_ParseTuple(args, "s#:unlink", &input, &slen))
		Py_RETURN_FALSE;
	
	if(!NormalizeInput(input, &sFileName, slen))
		Py_RETURN_FALSE;
	
	if (IsReparsePoint((LPCTSTR)sFileName) && GetReparseTag((LPCTSTR)sFileName, &dwTag)) {
		if(DeleteReparsePoint((LPCTSTR)sFileName)) {
			if(dwTag == IO_REPARSE_TAG_SYMLINK) {
				result = Py_True;
			} else if(dwTag == IO_REPARSE_TAG_MOUNT_POINT) {
				if(RemoveDirectory(sFileName))
					result = Py_True;
			}
		}
	}
	CleanupStr(sFileName);
	return result;
}

// Exported functions
static struct PyMethodDef ntfslink_methods[] = {
	{"islink", (PyCFunction)ntfslink_islink, METH_VARARGS,
	 ntfslink_islink_doc},
	{"isjunction", (PyCFunction)ntfslink_isjunction, METH_VARARGS,
	 ntfslink_readlink_doc},
	{"readlink", (PyCFunction)ntfslink_readlink, METH_VARARGS,
	 ntfslink_readlink_doc},
	{"link", (PyCFunction)ntfslink_link, METH_VARARGS,
	 ntfslink_link_doc},
	{"symlink", (PyCFunction)ntfslink_symlink, METH_VARARGS,
	 ntfslink_symlink_doc},
	{"junction", (PyCFunction)ntfslink_junction, METH_VARARGS,
	 ntfslink_junction_doc},
	{"unlink", (PyCFunction)ntfslink_unlink, METH_VARARGS,
	 ntfslink_unlink_doc},
	{"rm", (PyCFunction)ntfslink_unlink, METH_VARARGS,
	 ntfslink_unlink_doc},
	{NULL, NULL}
};

PyDoc_STRVAR(ntfslink_doc,
" Simple python wrapper around some Win32 API calls to support symbolic links, junctions, and hardlinks."
);
PyMODINIT_FUNC initntfslink(void)
{
	PyObject *mod;

	mod = Py_InitModule3("ntfslink", ntfslink_methods,
			     ntfslink_doc);
	if (mod == NULL)
		return;

}