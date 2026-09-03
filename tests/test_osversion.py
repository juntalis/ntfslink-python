from ntfslink import _osversion


def test_windows_version_returns_real_tuple():
    major, minor = _osversion.windows_version()
    assert isinstance(major, int)
    assert isinstance(minor, int)
    assert major >= 5  # this test only ever runs on real Windows


def test_is_at_least_uses_real_version_when_not_overridden():
    assert _osversion.is_at_least(0, 0) is True
    assert _osversion.is_at_least(999, 0) is False


def test_is_vista_or_later_uses_real_version_when_not_overridden():
    # This suite only ever runs on Windows 7+, so this must be True without
    # an explicit override.
    assert _osversion.is_vista_or_later() is True
