import ctypes

import pytest

from ntfslink import _attrs


def test_is_reparse_point_safe_false_for_missing_path(tmp_path):
    assert _attrs.is_reparse_point_safe(str(tmp_path / 'missing')) is False


def test_is_reparse_point_safe_false_for_plain_file(tmp_path):
    f = tmp_path / 'plain.txt'
    f.write_text('x')
    assert _attrs.is_reparse_point_safe(str(f)) is False


def test_is_reparse_point_raises_for_missing_path(tmp_path):
    with pytest.raises(OSError):
        _attrs.is_reparse_point(str(tmp_path / 'missing'))


def test_is_reparse_point_false_for_plain_dir(tmp_path):
    d = tmp_path / 'adir'
    d.mkdir()
    assert _attrs.is_reparse_point(str(d)) is False


def test_is_directory_entry_true_for_dir(tmp_path):
    d = tmp_path / 'adir'
    d.mkdir()
    assert _attrs.is_directory_entry(str(d)) is True


def test_is_directory_entry_false_for_file(tmp_path):
    f = tmp_path / 'plain.txt'
    f.write_text('x')
    assert _attrs.is_directory_entry(str(f)) is False


def test_is_directory_entry_raises_for_missing_path(tmp_path):
    with pytest.raises(OSError):
        _attrs.is_directory_entry(str(tmp_path / 'missing'))


def test_get_file_attributes_invalid_for_missing_path(tmp_path):
    from ntfslink import _consts as consts
    assert _attrs.get_file_attributes(str(tmp_path / 'missing')) == consts.INVALID_FILE_ATTRIBUTES
