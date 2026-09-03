import ctypes

import pytest

from ntfslink._pyimpl import winapi
from ntfslink.exceptions import InvalidHandleError


def _fake_func(name='SomeFunc'):
    f = lambda: None
    f.__name__ = name
    return f


def test_check_bool_raises_winerror_on_falsy_result():
    with pytest.raises(OSError):
        winapi.check_bool(0, _fake_func(), ())


def test_check_bool_returns_args_on_success():
    args = (1, 2, 3)
    assert winapi.check_bool(1, _fake_func(), args) == args


def test_check_handle_raises_invalid_handle_error_for_invalid_value():
    with pytest.raises(InvalidHandleError):
        winapi.check_handle(winapi.INVALID_HANDLE_VALUE, _fake_func('CreateFileW'), ())


def test_check_handle_raises_invalid_handle_error_for_zero():
    with pytest.raises(InvalidHandleError):
        winapi.check_handle(0, _fake_func('CreateFileW'), ())


def test_check_handle_returns_result_on_success():
    assert winapi.check_handle(1234, _fake_func(), ()) == 1234
