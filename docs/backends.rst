Backends and capability checks
===============================

Backend selection
------------------

Every low-level NTFS operation (building/parsing the reparse buffer,
issuing the ``FSCTL``/``CreateHardLinkW`` calls, querying volume flags)
is provided by a *backend*. All backends implement the same
:class:`ntfslink.backend.Backend` protocol and share identical
high-level behavior, so switching between them never changes what a
call to :mod:`ntfslink` does — only how it's implemented.

.. list-table::
   :header-rows: 1

   * - Backend
     - Description
   * - ``cext``
     - Compiled C extension (:mod:`ntfslink._cext`). Selected
       automatically when built and importable.
   * - ``struct``
     - Pure-Python fallback, using :mod:`struct` for reparse-buffer
       (de)serialization. The maintained fallback — faster than
       ``ctypes`` (see ``benchmarks/bench_backends.py``) — and selected
       automatically when the C extension isn't available.
   * - ``ctypes``
     - Pure-Python, using :class:`ctypes.Structure` for the codec
       instead of :mod:`struct`. Kept for regression testing; not
       selected automatically.

Selection is automatic by default — ``cext`` when importable, ``struct``
otherwise — but can be forced with the ``NTFSLINK_BACKEND`` environment
variable:

.. code-block:: shell

   set NTFSLINK_BACKEND=auto      # default
   set NTFSLINK_BACKEND=cext
   set NTFSLINK_BACKEND=struct
   set NTFSLINK_BACKEND=ctypes    # regression-testing backend

.. code-block:: python

   import ntfslink

   ntfslink.active_backend()      # 'cext', 'struct', or 'ctypes'
   ntfslink.available_backends()  # frozenset of every importable backend

The active backend is resolved once per process and cached; setting
``NTFSLINK_BACKEND`` after that point has no effect unless you call
``ntfslink.backend.reset_for_tests()`` (test-only) or start a new
process. Any public API function also accepts a ``backend=`` keyword to
override the process-wide choice for that single call.

Capability checks
------------------

:mod:`ntfslink.supports` answers "does this volume/OS support X"
without you needing to attempt the operation and catch a failure:

.. code-block:: python

   import ntfslink

   ntfslink.supports.hardlinks(r"C:\data")
   ntfslink.supports.reparse_points(r"C:\data")
   ntfslink.supports.junctions(r"C:\data")
   ntfslink.supports.symlinks(r"C:\data")

Each function accepts an optional ``path`` — omit it to ask for the
platform-level default rather than checking a specific volume. Hard
links are treated as supported on pre-Windows-7 systems, since NTFS has
supported them since Windows 2000 and the ``FILE_SUPPORTS_HARD_LINKS``
volume flag wasn't introduced until Windows 7; newer systems are checked
against that flag directly. Symbolic-link support additionally requires
Windows Vista or later, independent of the volume's reparse-point
support.

See :doc:`api/supports` for the full per-function reference.
