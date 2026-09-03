"""Backend dispatcher: picks the C extension when available, otherwise
falls back to a pure-Python (``ctypes``-Win32-call) backend. Selection can
be forced via the ``NTFSLINK_BACKEND`` environment variable
(``cext`` | ``ctypes`` | ``struct`` | ``auto``, default ``auto``).
"""
import os

_active = None
_active_kind = None


def _load_cext():
    from . import _cext
    return _cext


def _load_pyimpl(codec):
    from ._pyimpl.backend import make_backend
    return make_backend(codec)


def _resolve(override=None):
    choice = (override if override is not None else os.environ.get('NTFSLINK_BACKEND', 'auto')).lower()

    if choice == 'auto':
        try:
            return _load_cext(), 'cext'
        except ImportError:
            # struct beats ctypes.Structure for reparse-buffer (de)serialization
            # by ~1.5x (see benchmarks/bench_backends.py and RESULTS.md) — it's
            # the maintained fallback; 'ctypes' stays selectable via the
            # override for regression testing.
            return _load_pyimpl('struct'), 'struct'
    if choice == 'cext':
        return _load_cext(), 'cext'
    if choice in ('ctypes', 'struct'):
        return _load_pyimpl(choice), choice
    raise ValueError(f'Unknown NTFSLINK_BACKEND value: {choice!r}')


def get_backend():
    global _active, _active_kind
    if _active is None:
        _active, _active_kind = _resolve()
    return _active


def active_backend():
    get_backend()
    return _active_kind


def available_backends():
    result = {'ctypes', 'struct'}
    try:
        _load_cext()
        result.add('cext')
    except ImportError:
        pass
    return frozenset(result)


def reset_for_tests():
    """Test-only hook: forget the cached backend choice so the next call
    to ``get_backend()``/``active_backend()`` re-reads ``NTFSLINK_BACKEND``."""
    global _active, _active_kind
    _active = None
    _active_kind = None
