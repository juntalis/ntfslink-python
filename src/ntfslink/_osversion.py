"""Windows version helpers, kept injectable so tests can force either
branch regardless of the OS actually running the test suite."""
from __future__ import annotations

import sys
from typing import Optional


def windows_version() -> tuple[int, int]:
    info = sys.getwindowsversion()
    return info.major, info.minor


def is_at_least(major: int, minor: int = 0, version: Optional[tuple[int, int]] = None) -> bool:
    current = version if version is not None else windows_version()
    return current >= (major, minor)


def is_vista_or_later(version: Optional[tuple[int, int]] = None) -> bool:
    return is_at_least(6, 0, version)
