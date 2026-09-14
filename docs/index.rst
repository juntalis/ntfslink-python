ntfslink
========

``ntfslink`` is a Windows-only Python package for manipulating NTFS
links:

* directory junctions (mount points)
* file and directory symbolic links
* NTFS hard links, including link counts and path enumeration
* filesystem/OS capability checks (does this volume support X?)

It talks to Win32 directly through :mod:`ctypes`, with an optional
compiled C extension for the reparse-buffer codec — see
:doc:`backends` for how backend selection and fallback work.

.. code-block:: python

   import ntfslink

   ntfslink.create_junction(r"C:\data\source", r"C:\data\current")
   print(ntfslink.read_link(r"C:\data\current"))
   ntfslink.delete_reparse_point(r"C:\data\current")

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   backends
   api/index

Indices and tables
===================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
