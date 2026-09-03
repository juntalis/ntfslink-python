"""Exception types raised by :mod:`ntfslink`."""


class InvalidHandleError(OSError):
    """A Win32 call returned ``INVALID_HANDLE_VALUE``."""

    def __init__(self, descr=None):
        super().__init__(descr or 'Invalid HANDLE value detected!')


class _InvalidFilePathError(OSError):

    def __init__(self, filepath, descr, default_descr):
        super().__init__(descr or default_descr)
        self.filepath = filepath


class InvalidTargetError(_InvalidFilePathError):
    """The target (source) of a link operation is invalid."""

    def __init__(self, filepath, descr=None):
        super().__init__(filepath, descr, 'Invalid target path specified!')


class InvalidLinkError(_InvalidFilePathError):
    """The link (destination) path of a link operation is invalid."""

    def __init__(self, filepath, descr=None):
        super().__init__(filepath, descr, 'Invalid link path specified!')


__all__ = ['InvalidHandleError', 'InvalidTargetError', 'InvalidLinkError']
