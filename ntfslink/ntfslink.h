#pragma once
#include "defs.h"

#ifndef SWIG
#include "reparse.h"
#endif

// Results
#ifdef SWIG
%rename("%(uppercase)s") "";
#endif
enum CreateJunction_Result {
	create_success = 1,
	create_invalid_target = 0,
	create_invalid_path = -1,
	create_not_supported = -2,
	create_error_create = -3,
	create_error_set = -4
};
#define create_result enum CreateJunction_Result

#ifdef SWIG
%rename("%(uppercase)s") "";
#endif
enum DeleteJunction_Result {
	delete_success = 1,
	delete_invalid = 0,
	delete_error = -1
};
#define delete_result enum DeleteJunction_Result

// Exports
#ifdef SWIG
	%rename(is_junction) IsJunction;
	%rename(junction) CreateJunction;
	%rename(symlink) CreateSymbolicLink;
	%rename(hardlink) CreateHardLink;
	%rename(unlink) DeleteJunctionRecord;
	%rename("delete") DeleteJunction;
	%rename(folder) pszDir;
	%rename(folder) LinkDirectory;
	%rename(target) LinkTarget;
#endif
#ifdef SWIG
%feature("autodoc", "Aliases: check, isdir\nReturns a bool depending on whether or not the folder specified is a junction.");
#endif
extern bool IsJunction(LPTSTR pszDir);
#ifdef SWIG
%feature("autodoc", "Create a new junction.\nPossible return values:\n	CREATE_SUCCESS - Junction successfully created.\n	CREATE_INVALID_TARGET - Invalid file name specified for the target path.\n	CREATE_INVALID_PATH - Invalid file name specified for the junction. (the new folder)\n	CREATE_NOT_SUPPORTED - Junctions are only supported on NTFS volumes.\n	CREATE_ERROR_CREATE - Generic error creating the junction.\n	CREATE_ERROR_SET - Generic error while setting the path in the Reparse point records.");
#endif
extern create_result CreateJunction(LPTSTR LinkDirectory, LPTSTR LinkTarget);
#ifdef SWIG
%feature("autodoc", "Create a new hard link.\nPossible return values:\n	CREATE_SUCCESS - Junction successfully created.\n	CREATE_INVALID_TARGET - Invalid file name specified for the target path.\n	CREATE_INVALID_PATH - Invalid file name specified for the hard link. (the new file)\n	CREATE_ERROR_CREATE - Generic error creating the hard link.");
#endif
extern create_result CreateHardLink(LPTSTR LinkPath, LPTSTR LinkTarget);
#ifdef SWIG
%feature("autodoc", "Create a new symbolic link.\nPossible return values:\n	CREATE_SUCCESS - Junction successfully created.\n	CREATE_INVALID_TARGET - Invalid file name specified for the target path.\n	CREATE_INVALID_PATH - Invalid file name specified for the symbolic link. (the new file)\n	CREATE_ERROR_CREATE - Generic error creating the symbolic link.");
#endif
extern create_result CreateSymbolicLink(LPTSTR LinkPath, LPTSTR LinkTarget);
#ifdef SWIG
%feature("autodoc", "Delete a junction. (Empty folder remains)\nPossible return values:\n	DELETE_SUCCESS - Junction successfully deleted.\n	DELETE_INVALID - Directory specified is not a junction.\n	DELETE_ERROR - Error occurred while attempting to delete the junction.");
#endif
extern delete_result DeleteJunctionRecord(LPTSTR pszDir);
#ifdef SWIG
%feature("autodoc", "Aliases: rm, rmdir\nDelete a junction and delete the left over folder.\nPossible return values:\n	DELETE_SUCCESS - Junction successfully deleted.\n	DELETE_INVALID - Directory specified is not a junction.\n	DELETE_ERROR - Error occurred while attempting to delete the junction.");
#endif
extern delete_result DeleteJunction(LPTSTR pszDir);
#ifdef SWIG
%feature("autodoc", "1");
#endif