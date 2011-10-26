#pragma once
#include "defs.h"
#include "reparse.h"

#ifndef SWIG

/* Results */
enum Create_Result {
	create_success = 1,
	create_invalid_target = 0,
	create_invalid_path = -1,
	create_not_supported = -2,
	create_error_create = -3,
	create_error_set = -4
};
enum Delete_Result {
	delete_success = 1,
	delete_invalid = 0,
	delete_error = -1
};
#define create_result enum Create_Result
#define delete_result enum Delete_Result


extern bool IsJunction(LPTSTR folder);
extern create_result CreateHardLink(LPTSTR, LPTSTR);
extern create_result CreateSymbolicLink(LPTSTR, LPTSTR);
extern create_result CreateJunction(LPTSTR, LPTSTR);
extern LPTSTR ReadJunction(LPTSTR folder);
extern delete_result DeleteJunctionRecord(LPTSTR);
extern delete_result DeleteJunction(LPTSTR);

#endif