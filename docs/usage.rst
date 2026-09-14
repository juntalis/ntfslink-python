Usage
=====

Junctions
---------

A directory junction (mount point) makes ``dst`` resolve to ``src``
without requiring any special privilege — this is the mechanism behind
things like ``Documents and Settings`` compatibility shims on modern
Windows.

.. code-block:: python

   import ntfslink

   ntfslink.create_junction(r"C:\data\source", r"C:\data\current")
   ntfslink.is_junction(r"C:\data\current")      # True
   ntfslink.read_link(r"C:\data\current")        # 'C:\\data\\source'
   ntfslink.delete_reparse_point(r"C:\data\current")

``src`` must already exist and be a directory; junction targets are
always normalized to absolute paths. See
:func:`ntfslink.create_junction`.

Symbolic links
--------------

Symbolic links can target files or directories, and — unlike
junctions — support relative targets and require either
``SeCreateSymbolicLinkPrivilege`` or Windows Developer Mode.

.. code-block:: python

   ntfslink.create_symlink(
       r"C:\data\report.txt",
       r"C:\data\latest.txt",
       target_is_directory=False,
   )
   ntfslink.is_symlink(r"C:\data\latest.txt")    # True

Pass ``target_is_directory`` explicitly whenever the target doesn't
exist yet — otherwise it's inferred from the target and there's nothing
to inspect. See :func:`ntfslink.create_symlink`.

Inspecting and removing links
------------------------------

:func:`ntfslink.is_reparse_point`, :func:`ntfslink.is_junction`, and
:func:`ntfslink.is_symlink` never raise for a path that doesn't exist —
they simply return ``False``. :func:`ntfslink.delete_reparse_point`
works for either link type: it detaches the reparse point and removes
the now-plain placeholder underneath it.

.. code-block:: python

   if ntfslink.is_reparse_point(path):
       ntfslink.delete_reparse_point(path)

Hard links
----------

NTFS hard links share a single file record between multiple directory
entries — there's no "original" once created, and no cross-directory or
cross-volume support.

.. code-block:: python

   ntfslink.create_hardlink(r"C:\data\report.txt", r"C:\data\report-copy.txt")
   ntfslink.hardlink_count(r"C:\data\report.txt")          # 2
   ntfslink.enumerate_hardlinks(r"C:\data\report.txt")
   # ['C:\\data\\report.txt', 'C:\\data\\report-copy.txt']

:func:`ntfslink.enumerate_hardlinks` walks the raw NTFS MFT and
generally requires an elevated process — see
:func:`ntfslink.enumerate_hardlinks` for the details and its Windows
XP SP2-compatible design rationale. Directories cannot be hard-linked;
NTFS doesn't support it.

Error handling
--------------

Invalid source and destination paths raise
:exc:`ntfslink.exceptions.InvalidTargetError` and
:exc:`ntfslink.exceptions.InvalidLinkError` respectively — both carry
the offending path as ``.filepath``. Low-level Win32 failures surface as
:exc:`ntfslink.exceptions.InvalidHandleError` or, for the raw
``GetFileAttributesW``-backed attribute checks, a plain
:exc:`OSError` from :func:`ctypes.WinError`.

.. code-block:: python

   from ntfslink.exceptions import InvalidLinkError, InvalidTargetError

   try:
       ntfslink.create_junction(src, dst)
   except InvalidTargetError as exc:
       print(f"bad source {exc.filepath}: {exc}")
   except InvalidLinkError as exc:
       print(f"bad destination {exc.filepath}: {exc}")

Backend override
-----------------

Every public function accepts an optional ``backend=`` keyword, which
selects the low-level implementation for a single call rather than
process-wide. This is mainly useful for tests; see :doc:`backends` for
the process-wide selection mechanism (``NTFSLINK_BACKEND``) and what
each backend actually is.
