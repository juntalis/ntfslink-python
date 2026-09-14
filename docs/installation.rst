Installation
============

Requirements
------------

* Windows with an NTFS volume
* Python 3.8 or newer
* Administrator access for some operations, especially hard-link path
  enumeration through the raw NTFS MFT (see :func:`ntfslink.enumerate_hardlinks`)

Junctions can target directories without requiring symbolic-link
privileges. Symbolic links require Windows Vista or later and either
``SeCreateSymbolicLinkPrivilege`` or Windows Developer Mode — see
:doc:`backends` for the capability-check functions that let you probe for
this at runtime instead of assuming it.

From PyPI
---------

.. code-block:: shell

   python -m pip install ntfslink-py

The distribution is named ``ntfslink-py``; the importable package is
still ``ntfslink``:

.. code-block:: python

   import ntfslink

From a checkout
----------------

.. code-block:: shell

   python -m pip install .

The package ships an optional compiled C extension
(:mod:`ntfslink._cext`) that accelerates the reparse-buffer codec. If a
C toolchain isn't available, or the extension otherwise fails to build,
installation continues anyway and the pure-Python fallback backend is
used automatically — see :doc:`backends` for details.

Development install
--------------------

.. code-block:: shell

   python -m pip install -e ".[test]"
   python -m pytest

Optional extra dependency groups, declared in ``pyproject.toml``:

.. list-table::
   :header-rows: 1

   * - Extra
     - Installs
   * - ``test``
     - ``pytest``, ``pytest-cov``
   * - ``typecheck``
     - ``mypy``
   * - ``docs``
     - ``sphinx`` (this documentation build)

The test suite includes unit tests for all backends and Windows-gated
integration tests for real NTFS operations.

Building this documentation
----------------------------

.. code-block:: shell

   python -m pip install -e ".[docs]"
   cd docs
   make html      # or: make.bat html on Windows cmd.exe

The built site is written to ``docs/_build/html/index.html``.
