import os

import pytest

import ntfslink
from ntfslink.exceptions import InvalidLinkError, InvalidTargetError


def _norm(paths):
    return {os.path.normcase(os.path.abspath(p)) for p in paths}


def test_create_hardlink_and_count(backend, tmp_path):
    target = tmp_path / 'target.txt'
    target.write_text('data')
    link = str(tmp_path / 'link.txt')

    assert ntfslink.hardlink_count(str(target), backend=backend) == 1
    ntfslink.create_hardlink(str(target), link, backend=backend)
    assert ntfslink.hardlink_count(str(target), backend=backend) == 2
    assert open(link).read() == 'data'


def test_create_hardlink_rejects_missing_source(backend, tmp_path):
    with pytest.raises(InvalidTargetError):
        ntfslink.create_hardlink(str(tmp_path / 'missing'), str(tmp_path / 'link'), backend=backend)


def test_create_hardlink_rejects_directory_source(backend, tmp_path):
    d = tmp_path / 'adir'
    d.mkdir()
    with pytest.raises(InvalidTargetError):
        ntfslink.create_hardlink(str(d), str(tmp_path / 'link'), backend=backend)


def test_create_hardlink_rejects_existing_dst(backend, tmp_path):
    target = tmp_path / 'target.txt'
    target.write_text('data')
    dst = tmp_path / 'existing.txt'
    dst.write_text('already here')

    with pytest.raises(InvalidLinkError):
        ntfslink.create_hardlink(str(target), str(dst), backend=backend)


def test_enumerate_hardlinks_single_link(backend, tmp_path):
    target = tmp_path / 'lonely.txt'
    target.write_text('data')

    links = ntfslink.enumerate_hardlinks(str(target), backend=backend)
    assert _norm(links) == _norm([str(target)])


def test_enumerate_hardlinks_multiple_same_directory(backend, tmp_path):
    target = tmp_path / 'target.txt'
    target.write_text('data')
    link1 = str(tmp_path / 'link1.txt')
    link2 = str(tmp_path / 'link2.txt')
    ntfslink.create_hardlink(str(target), link1, backend=backend)
    ntfslink.create_hardlink(str(target), link2, backend=backend)

    links = ntfslink.enumerate_hardlinks(str(target), backend=backend)
    assert len(links) == 3
    assert _norm(links) == _norm([str(target), link1, link2])
    assert len(links) == ntfslink.hardlink_count(str(target), backend=backend)


def test_enumerate_hardlinks_across_directories(backend, tmp_path):
    subdir = tmp_path / 'nested' / 'deeper'
    subdir.mkdir(parents=True)
    target = tmp_path / 'target.txt'
    target.write_text('data')
    nested_link = str(subdir / 'nested_link.txt')

    ntfslink.create_hardlink(str(target), nested_link, backend=backend)

    links = ntfslink.enumerate_hardlinks(str(target), backend=backend)
    assert _norm(links) == _norm([str(target), nested_link])


def test_enumerate_hardlinks_long_and_short_name_not_double_counted(backend, tmp_path):
    # A name with spaces/long-enough-to-need-an-8.3-alias still stores an
    # extra short-name $FILE_NAME attribute pointing at the same directory
    # — enumerate_hardlinks must report the link once, not twice.
    target = tmp_path / 'a rather long file name.txt'
    target.write_text('data')

    links = ntfslink.enumerate_hardlinks(str(target), backend=backend)
    assert len(links) == 1
    assert ntfslink.hardlink_count(str(target), backend=backend) == 1
