Python NTFS Links Module
======================

#### What is it?

Simple python module wrapping some of the Win32 API to allow support for junctions. For information on junctions, see the MSDN entry on [Junction Points](http://msdn.microsoft.com/en-us/library/bb968829%28VS.85%29.aspx).

If you are looking for more advanced support for symbolic links and hardlinks, check out [Python for Windows Extensions](http://sourceforge.net/projects/pywin32/), which if I remember correct, allows use of Transacted filesystem actions in its win32file module.

_Update_: Renamed the module and added some simple wrappers around CreateSymbolicLink and CreateHardLink, which can now be called through ntfslink.symlink and ntfslink.hardlink respectively. Additionally, junctions are now created with ntfslink.junction.


#### What can it do?

* Create new junctions to existing directories.
* Deleting existing junctions, referenced by file path.
* Check whether or not an existing folder is a junction point.
* Create symbolic links to files and directories.
* Create hard links to files.

#### Example Usage

	result = ntfslink.junction('temp', 'C:\\Temp')
	# if C:\Temp exists and everything works out, result would be
	# ntfslink.CREATE_SUCCESS right now.
	if ntfslink.is_junction('temp'):
		print 'Junction was successfully created.'
		ntfslink.delete('temp')

Additionally, there's also ntfslink.unlink(folder), which removes the junction entry, but leaves the empty folder behind. There are also a few functions that are just aliases to the main four functions. Just open an interpreter and run help(ntfslink) for more information.

#### Credits

Based on original code by [Sysinternals](http://technet.microsoft.com/en-us/sysinternals) in their command line [Junction](http://technet.microsoft.com/en-us/sysinternals/bb896768) tool.

Used [SWIG](http://www.swig.org/) to generate the python wrapper to the code.

#### TODO:

* Add documentation
* Pick some logical names for the functions to clearly distinguish what does what
* Look up a way to create IsHardLink and IsSymbolicLink functions
* Check MSDN to see if any complications arise from deleting symbolic links or hard links like you would normal files.