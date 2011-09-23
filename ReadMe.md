Python NTFS Links Module
======================

#### What is it?

Simple python module wrapping some of the Win32 API to allow support for junctions. For information on junctions, see the MSDN entry on [Junction Points](http://msdn.microsoft.com/en-us/library/bb968829%28VS.85%29.aspx).

If you are looking for more advanced support for symbolic links and hardlinks, check out [Python for Windows Extensions](http://sourceforge.net/projects/pywin32/), which if I remember correct, allows use of Transacted filesystem actions in its win32file module.

_Update_: Added boost and cython wrappers if you prefer to use them.


#### What can it do?

* Create new junctions to existing directories.
* Deleting existing junctions, referenced by file path.
* Check whether or not an existing folder is a junction point.
* Create symbolic links to files and directories.
* Create hard links to files.

### Installation

By default, the distutils script will build ntfslink with a swig wrapper. (If it can't find swig.exe on your system PATH, it will use the pre-generated .cpp file). You can however, tell the setup script to use a cython wrapper by adding 'cython' to the end of your command. See below.

	setup.py build cython

	setup.py install cython

There is also a bjam build file in wrappers/boost to build the extension using a boost wrapper. I haven't figured out a clean way of integrating that into the setup script, but if you'd like to use a boost wrapper, simple open the Jamroot file located at wrapper/boost and change the line:

	BOOST_ROOT = C:/ShellEnv/j-tree/lib/cpp/boost_1_46_1 ;

to wherever your boost folder is, and execute the normal bjam command:

	bjam.exe release

#### Example Usage

	>>> import ntfslink as nt
	>>> nt.junction('C:\Temp','temp')
	True
	>>> nt.isjunction('temp')
	True
	>>> nt.readjunction('temp')
	'C:\\Temp'
	>>> nt.rmdir('temp')
	True
	>>> nt.isjunction('temp')
	False

Additionally, there's also ntfslink.unlink(folder), which removes the junction entry, but leaves the empty folder behind. There are also a few functions that are just aliases to the main four functions. Just open an interpreter and run help(ntfslink) for more information.

#### Credits

Based on original code by [Sysinternals](http://technet.microsoft.com/en-us/sysinternals) in their command line [Junction](http://technet.microsoft.com/en-us/sysinternals/bb896768) tool.

Used [SWIG](http://www.swig.org/) to generate the python wrapper to the code.

#### TODO:

* Look up a way to create IsHardLink and IsSymbolicLink functions
* Check MSDN to see if any complications arise from deleting symbolic links or hard links like you would normal files.