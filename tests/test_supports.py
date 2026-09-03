import types

from ntfslink import _consts as consts
from ntfslink import supports


def _fake_backend(flags):
    return types.SimpleNamespace(query_volume_flags=lambda path, use_cache=False: flags)


VISTA = (6, 0)
XP = (5, 1)


def test_hardlinks_true_pre_vista_regardless_of_path():
    b = _fake_backend(0)
    assert supports.hardlinks('C:\\', backend=b, version=XP) is True
    assert supports.hardlinks(None, backend=b, version=XP) is True


def test_hardlinks_true_when_path_none_even_on_vista():
    b = _fake_backend(0)
    assert supports.hardlinks(None, backend=b, version=VISTA) is True


def test_hardlinks_checks_volume_flag_on_vista_plus():
    assert supports.hardlinks('C:\\', backend=_fake_backend(consts.FILE_SUPPORTS_HARD_LINKS), version=VISTA) is True
    assert supports.hardlinks('C:\\', backend=_fake_backend(0), version=VISTA) is False


def test_reparse_points_true_when_path_none():
    assert supports.reparse_points(None, backend=_fake_backend(0)) is True


def test_reparse_points_checks_volume_flag():
    b_yes = _fake_backend(consts.FILE_SUPPORTS_REPARSE_POINTS)
    b_no = _fake_backend(0)
    assert supports.reparse_points('C:\\', backend=b_yes) is True
    assert supports.reparse_points('C:\\', backend=b_no) is False


def test_junctions_is_alias_for_reparse_points():
    b = _fake_backend(consts.FILE_SUPPORTS_REPARSE_POINTS)
    assert supports.junctions('C:\\', backend=b) == supports.reparse_points('C:\\', backend=b)


def test_symlinks_false_pre_vista():
    b = _fake_backend(consts.FILE_SUPPORTS_REPARSE_POINTS)
    assert supports.symlinks('C:\\', backend=b, version=XP) is False
    assert supports.symlinks(None, backend=b, version=XP) is False


def test_symlinks_true_when_path_none_on_vista_plus():
    b = _fake_backend(0)
    assert supports.symlinks(None, backend=b, version=VISTA) is True


def test_symlinks_checks_volume_flag_on_vista_plus():
    b_yes = _fake_backend(consts.FILE_SUPPORTS_REPARSE_POINTS)
    b_no = _fake_backend(0)
    assert supports.symlinks('C:\\', backend=b_yes, version=VISTA) is True
    assert supports.symlinks('C:\\', backend=b_no, version=VISTA) is False
