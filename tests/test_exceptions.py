from ntfslink.exceptions import InvalidHandleError, InvalidLinkError, InvalidTargetError


def test_invalid_handle_error_default_message():
    err = InvalidHandleError()
    assert 'Invalid HANDLE' in str(err)


def test_invalid_handle_error_custom_message():
    err = InvalidHandleError('custom message')
    assert str(err) == 'custom message'


def test_invalid_target_error_default_message_and_filepath():
    err = InvalidTargetError('C:\\some\\path')
    assert err.filepath == 'C:\\some\\path'
    assert 'target' in str(err).lower()


def test_invalid_target_error_custom_message():
    err = InvalidTargetError('C:\\some\\path', 'custom')
    assert str(err) == 'custom'
    assert err.filepath == 'C:\\some\\path'


def test_invalid_link_error_default_message_and_filepath():
    err = InvalidLinkError('C:\\link\\path')
    assert err.filepath == 'C:\\link\\path'
    assert 'link' in str(err).lower()


def test_invalid_link_error_custom_message():
    err = InvalidLinkError('C:\\link\\path', 'custom')
    assert str(err) == 'custom'
    assert err.filepath == 'C:\\link\\path'


def test_exceptions_are_oserror_subclasses():
    assert issubclass(InvalidHandleError, OSError)
    assert issubclass(InvalidTargetError, OSError)
    assert issubclass(InvalidLinkError, OSError)
