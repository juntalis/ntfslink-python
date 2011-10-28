Python NTFS Links Module
======================

#### What is it?

Simple python module wrapping some of the Win32 API to allow support for junctions. For information on junctions, see the MSDN entry on [Junction Points](http://msdn.microsoft.com/en-us/library/bb968829%28VS.85%29.aspx).

If you are looking for more advanced support for symbolic links and hardlinks, check out [Python for Windows Extensions](http://sourceforge.net/projects/pywin32/), which if I remember correct, allows use of Transacted filesystem actions in its win32file module. I've added a example implementation of readlink, islink, and realpath using the pywin32 module to the contrib folder. Feel free to use/modify/improve upon it as you see fit. It will also work for junctions if you substitute "MOUNTPOINT" for "SYMBOLIC_LINK" in the readlink function.

Lastly, I was playing around with cygwin symbolic links and wrote a quick(dumb) implementation of readlink and symlink to work with cygwin symbolic links without any external dependency on cygwin. It requires [Cython](http://cython.org/) to build. If you don't have Cython and would like to build it without having to install Cython, let me know, and I'll attach the .c file that cython generates. Note: It does not automatically convert the cygwin path to a Windows path for either functions. It will read/write the links exactly as you put them.

#### What can it do?

* Read the target of existing junctions/symbolic links
* Remove the reparse point record from a symbolic link
* Delete existing junctions, referenced by file path.
* Check whether or not an existing folder is a junction point/symbolic link.
* Create symbolic links to files and directories.
* Create new junctions to existing directories.
* Create hard links to files.

### Installation

Standard module building command.

**To build in the local directory:**

	setup.py build

**Or to install:**

	setup.py install

**Old Instructions**

~~By default, the distutils script will build ntfslink with a swig wrapper. (If it can't find swig.exe on your system PATH, it will use the pre-generated .cpp file). You can however, tell the setup script to use a cython wrapper by adding 'cython' to the end of your command. See below.~~

~~setup.py build cython~~

~~setup.py install cython~~

~~There is also a bjam build file in wrappers/boost to build the extension using a boost wrapper. I haven't figured out a clean way of integrating that into the setup script, but if you'd like to use a boost wrapper, simple open the Jamroot file located at wrapper/boost and change the line:~~

~~BOOST_ROOT = C:/ShellEnv/j-tree/lib/cpp/boost_1_46_1 ;~~

~~to wherever your boost folder is, and execute the normal bjam command:~~

~~bjam.exe release~~

#### Example Usage

	>>> import ntfslink as nt
	>>> nt.junction('C:\Temp','temp')
	True
	>>> nt.isjunction('temp')
	True
	>>> nt.readlink('temp')
	'\\??\\C:\\Temp'
	>>> nt.unlink('temp')
	True
	>>> nt.isjunction('temp')
	False

Additionally, there's also ntfslink.unlink(folder), which removes the junction entry, but leaves the empty folder behind. There are also a few functions that are just aliases to the main four functions. Just open an interpreter and run help(ntfslink) for more information.

#### Credits

~~Some~~ Alot of the code is made up of bits and pieces modified from the project, "reparselib". The full source can be found at [reparselib](https://github.com/amdf/reparselib). No license was specified, but all credit goes to the author, [amdf](https://github.com/amdf). Besides that, a lot of the information on the Win32 API calls made was picked up at

#### TODO:

* Get rid of the crap at the beginning of the return from readlink when you're checking a junction.