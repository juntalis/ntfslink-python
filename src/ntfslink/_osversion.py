"""Windows version helpers, kept injectable so tests can force either
branch regardless of the OS actually running the test suite."""
import sys


def windows_version():
    info = sys.getwindowsversion()
    return info.major, info.minor


def is_at_least(major, minor=0, version=None):
    current = version if version is not None else windows_version()
    return current >= (major, minor)


def is_vista_or_later(version=None):
    return is_at_least(6, 0, version)
