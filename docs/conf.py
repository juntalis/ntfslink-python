"""Sphinx configuration for ntfslink."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join('..', 'src')))

import ntfslink  # noqa: E402

project = 'ntfslink'
copyright = '2026, Charles Grunwald'
author = 'Charles Grunwald'
release = '.'.join(str(part) for part in ntfslink.__version__)
version = release

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}

autodoc_member_order = 'bysource'
autodoc_typehints = 'description'

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'alabaster'
html_static_path = ['_static']
