Python Junction Module
======================

#### What is it?

Simple python module wrapping some of the Win32 API to allow support for junctions. For information on junctions, see the MSDN entry on [Junction Points](http://msdn.microsoft.com/en-us/library/bb968829%28VS.85%29.aspx).

#### What can it do?

* Create new junctions to existing directories.
* Deleting existing junctions, referenced by file path.
* Check whether or not an existing folder is a junction point.

#### Example Usage

	result = junction.create('temp', 'C:\\Temp')
	# if C:\Temp exists and everything works out, result would be
	# junction.CREATE_SUCCESS right now.
	if junction.is_junction('temp'):
		print 'Junction was successfully created.'
		junction.delete('temp')

Additionally, there's also junction.unlink(folder), which removes the junction entry, but leaves the empty folder behind. There are also a few functions that are just aliases to the main four functions. Just open an interpreter and run help(junction) for more information.

#### Credits

Based on original code by [Sysinternals](http://technet.microsoft.com/en-us/sysinternals) in their command line [Junction](http://technet.microsoft.com/en-us/sysinternals/bb896768) tool.

Used [SWIG](http://www.swig.org/) to generate the python wrapper to the code.