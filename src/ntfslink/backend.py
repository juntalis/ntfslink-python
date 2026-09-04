"""Backend dispatcher: picks the C extension when available, otherwise
falls back to a pure-Python (``ctypes``-Win32-call) backend. Selection can
be forced via the ``NTFSLINK_BACKEND`` environment variable
(``cext`` | ``ctypes`` | ``struct`` | ``auto``, default ``auto``).
"""
from __future__ import annotations

import os
from types import ModuleType
from typing import Optional, Protocol, TypeAlias


class Backend(Protocol):
    """Describes the primitive-operation surface every backend (the C
    extension module, :func:`ntfslink._pyimpl.backend.make_backend`'s
    ``SimpleNamespace``, and tests' ``FakeBackend``) provides. It exists
    only for static checking — nothing at runtime constructs or checks
    against it, callers just duck-type against ``get_backend()``'s result.
    """
    def build_reparse_buffer(
        self, tag: int, subst_name: str, print_name: str, flags: int = 0,
    ) -> bytes: ...

    def parse_reparse_buffer(self, data: bytes) -> tuple[int, int, str, str]: ...

    def set_reparse_point(self, path: str, buffer: bytes) -> None: ...

    def get_reparse_buffer(self, path: str) -> bytes: ...

    def delete_reparse_point_ioctl(self, path: str, tag: int) -> None: ...

    def create_hard_link(self, src: str, dst: str) -> None: ...

    def get_link_count(self, path: str) -> int: ...

    def get_file_reference_number(self, path: str) -> int: ...

    def get_ntfs_file_record(self, volume_root_path: str, file_reference_number: int) -> bytes: ...

    def volume_root(self, path: str) -> str: ...

    def query_volume_flags(self, path: str, use_cache: bool = False) -> int: ...

    def ensure_privileges(self) -> None: ...


OptBackend: TypeAlias = Optional[Backend]

_active: OptBackend = None
_active_kind: Optional[str] = None


def _load_cext() -> ModuleType:
    from . import _cext
    return _cext


def _load_pyimpl(codec: str) -> Backend:
    from ._pyimpl.backend import make_backend
    return make_backend(codec)


def _resolve(override: Optional[str] = None) -> tuple[Backend, str]:
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


def get_backend() -> Backend:
    global _active, _active_kind
    if _active is None:
        _active, _active_kind = _resolve()
    return _active


def active_backend() -> str:
    get_backend()
    assert _active_kind is not None
    return _active_kind


def available_backends() -> frozenset[str]:
    result = {'ctypes', 'struct'}
    try:
        _load_cext()
        result.add('cext')
    except ImportError:
        pass
    return frozenset(result)


def reset_for_tests() -> None:
    """Test-only hook: forget the cached backend choice so the next call
    to ``get_backend()``/``active_backend()`` re-reads ``NTFSLINK_BACKEND``."""
    global _active, _active_kind
    _active = None
    _active_kind = None
