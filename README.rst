Python NTFS Links Module
========================

What is it?
^^^^^^^^^^^

A ctypes based Python module for manipulating reparse points
(junctions/symbolic links/etc) and hard links on the Windows
version of Python. Originally this was written to be a C-extension,
but ctypes appears to be the more portable solution. At the moment,
this project is still a work in progress, and is being rewritten
from the ground up to utilize on ctypes. It currently supports the
manipulation of junction points, symbolic links, and the ability to
check for support of symbolic links.

While symbolic links are officially only supported on Windows Vista
and higher, Windows XP users can also utilize them by installing a
custom driver:


-  `Author's Homepage <http://homepage1.nifty.com/emk/>`_
-  `Source Code Download <http://homepage1.nifty.com/emk/symlink-1.06-src.zip>`_
-  `Download (32-bit) <http://homepage1.nifty.com/emk/symlink-1.06-x86.cab>`_
-  `Download (64-bit) <http://homepage1.nifty.com/emk/symlink-1.06-x64.zip>`_
-  `English Information <http://schinagl.priv.at/nt/hardlinkshellext/hardlinkshellext.html#symboliclinksforwindowsxp>`_

I have nothing to do with that project, but I did go ahead and add
logic for checking for it in the functions dealing with symbolic
link support.

Installation
~~~~~~~~~~~~

**Ignore below. The setup doesn't work at the moment, as I've begun rewriting this project from scratch. If you need some functionality already implemented, feel free to just grab what you need from the code.**

Standard module building command.

**To build in the local directory:**

::

    setup.py build

**Or to install:**

::

    setup.py install

Credits
^^^^^^^

Much of the code was derived by reimplementing pieces of the reparselib, who's full source code can be found at `reparselib <https://github.com/amdf/reparselib>`_.

Additionally, thanks goes out to the following Stack Overflow users for explaining a few concepts/methods to me:

*  `Using a struct as a function argument with the python ctypes module <http://stackoverflow.com/questions/8744246/using-a-struct-as-a-function-argument-with-the-python-ctypes-module>`_

	-  `Janne Karila <http://stackoverflow.com/users/222914/janne-karila>`_

* `Programmatically finding the target of a Windows Hard link <http://stackoverflow.com/questions/10260676/programmatically-finding-the-target-of-a-windows-hard-link>`_

	-  `Raymond Chen <http://stackoverflow.com/users/902497/raymond-chen>`_
	-  `Deanna <http://stackoverflow.com/users/588306/deanna>`_
	-  `Jay <http://stackoverflow.com/users/1510085/jay>`_

TODO:
^^^^^

See the `project issues <https://github.com/Juntalis/ntfslink-python/issues?state=open>`_.
