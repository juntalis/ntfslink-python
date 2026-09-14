"""ntfslink: NTFS reparse point (junction/symlink) and hard link
manipulation for Windows.

The public API is re-exported here directly; submodules (:mod:`.reparse`,
:mod:`.hardlinks`, :mod:`.backend`) are implementation detail and not
part of the stable interface except where noted.

>>> import ntfslink
>>> ntfslink.create_junction(r"C:\\data\\source", r"C:\\data\\current")
>>> ntfslink.read_link(r"C:\\data\\current")
'C:\\\\data\\\\source'
>>> ntfslink.delete_reparse_point(r"C:\\data\\current")
"""
import sys

if sys.platform != 'win32':  # pragma: no cover — covered by test_import_guard.py in a subprocess, invisible to this process's coverage run
    raise ImportError('ntfslink is a Windows-only package (NTFS reparse points/hard links).')

__version__ = (2, 0, 0)

from . import exceptions  # noqa: E402
from .backend import active_backend, available_backends  # noqa: E402
from .hardlinks import create_hardlink, enumerate_hardlinks, hardlink_count  # noqa: E402
from .reparse import (  # noqa: E402
    create_junction,
    create_symlink,
    delete_reparse_point,
    is_junction,
    is_symlink,
    read_link,
)
from ._attrs import is_reparse_point_safe as is_reparse_point  # noqa: E402
from . import supports  # noqa: E402

__all__ = [
    '__version__',
    'active_backend', 'available_backends',
    'create_junction', 'create_symlink', 'read_link', 'delete_reparse_point',
    'is_reparse_point', 'is_junction', 'is_symlink',
    'create_hardlink', 'hardlink_count', 'enumerate_hardlinks',
    'supports', 'exceptions',
]
