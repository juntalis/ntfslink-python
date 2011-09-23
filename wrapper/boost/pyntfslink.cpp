//#pragma comment(lib,"kernel32.lib")
#pragma comment(lib,"advapi32.lib")
#pragma comment(lib,"Shlwapi.lib")
#include <boost/python.hpp>
#include <boost/python/make_function.hpp>
#include <boost/python/str.hpp>
#include "ntfslink.h"

bool is_junction(LPTSTR folder) {
	return IsJunction(folder);
}

bool create_junction(LPTSTR source, LPTSTR link_name) {
	return CreateJunction(source, link_name) == create_success;
}

bool create_link(LPTSTR source, LPTSTR link_name) {
	return CreateHardLink(source, link_name) == create_success;
}

bool create_symlink(LPTSTR source, LPTSTR link_name) {
	return CreateSymbolicLink(source, link_name) == create_success;
}

const char * read_junction(LPTSTR folder) {
	return const_cast<const char *>(ReadJunction(folder));
}

bool delete_record(LPTSTR pszDir) {
	return DeleteJunctionRecord(pszDir) == delete_success;
}

bool delete_junction(LPTSTR pszDir) {
	return DeleteJunction(pszDir) == delete_success;
}


BOOST_PYTHON_MODULE(ntfslink)
{
	using namespace boost::python;
	def("isjunction", make_function(is_junction));
	def("link", make_function(create_link));
	def("symlink", make_function(create_symlink));
	def("junction", make_function(create_junction));
	def("readjunction", make_function(read_junction));
	def("unlink", make_function(delete_record));
	def("rmdir", make_function(delete_junction));
}
