import os

import pytest

import ntfslink
from ntfslink.exceptions import InvalidLinkError, InvalidTargetError


def _make_dir_with_file(tmp_path, dirname='target'):
    target = tmp_path / dirname
    target.mkdir()
    (target / 'hello.txt').write_text('hi')
    return str(target)


def test_junction_roundtrip(backend, backend_name, tmp_path):
    target = _make_dir_with_file(tmp_path)
    link = str(tmp_path / 'junction')

    ntfslink.create_junction(target, link, backend=backend)

    assert ntfslink.is_junction(link, backend=backend)
    assert not ntfslink.is_symlink(link, backend=backend)
    assert ntfslink.is_reparse_point(link)
    assert os.path.isfile(os.path.join(link, 'hello.txt'))
    assert ntfslink.read_link(link, backend=backend) == target

    ntfslink.delete_reparse_point(link, backend=backend)
    assert not os.path.exists(link)
    assert os.path.isdir(target)  # original target untouched


def test_junction_creates_missing_dst(backend, tmp_path):
    target = _make_dir_with_file(tmp_path)
    link = str(tmp_path / 'junction_new')
    assert not os.path.exists(link)

    ntfslink.create_junction(target, link, backend=backend)
    assert os.path.isdir(link)


def test_junction_rejects_file_target(backend, tmp_path):
    file_path = tmp_path / 'file.txt'
    file_path.write_text('x')
    link = str(tmp_path / 'junction')

    with pytest.raises(InvalidTargetError):
        ntfslink.create_junction(str(file_path), link, backend=backend)


def test_junction_rejects_missing_target(backend, tmp_path):
    link = str(tmp_path / 'junction')
    with pytest.raises(InvalidTargetError):
        ntfslink.create_junction(str(tmp_path / 'nope'), link, backend=backend)


def test_junction_rejects_existing_file_at_dst(backend, tmp_path):
    target = _make_dir_with_file(tmp_path)
    link = tmp_path / 'junction'
    link.write_text('already here')

    with pytest.raises(InvalidLinkError):
        ntfslink.create_junction(target, str(link), backend=backend)


def test_absolute_dir_symlink_roundtrip(backend, tmp_path):
    target = _make_dir_with_file(tmp_path)
    link = str(tmp_path / 'dirlink')

    ntfslink.create_symlink(target, link, backend=backend)

    assert ntfslink.is_symlink(link, backend=backend)
    assert not ntfslink.is_junction(link, backend=backend)
    assert os.path.isfile(os.path.join(link, 'hello.txt'))
    assert ntfslink.read_link(link, backend=backend) == target

    ntfslink.delete_reparse_point(link, backend=backend)
    assert not os.path.exists(link)


def test_relative_file_symlink_roundtrip(backend, tmp_path, monkeypatch):
    target_file = tmp_path / 'file.txt'
    target_file.write_text('data')
    link = tmp_path / 'file_link.txt'

    monkeypatch.chdir(tmp_path)
    ntfslink.create_symlink('file.txt', 'file_link.txt', backend=backend)

    assert ntfslink.is_symlink('file_link.txt', backend=backend)
    assert link.read_text() == 'data'
    assert ntfslink.read_link('file_link.txt', backend=backend) == 'file.txt'

    ntfslink.delete_reparse_point('file_link.txt', backend=backend)
    assert not link.exists()
    assert target_file.exists()


def test_symlink_target_is_directory_explicit(backend, tmp_path):
    target = _make_dir_with_file(tmp_path)
    link = str(tmp_path / 'explicit_dir_link')

    ntfslink.create_symlink(target, link, target_is_directory=True, backend=backend)
    assert os.path.isdir(link)
    ntfslink.delete_reparse_point(link, backend=backend)


def test_symlink_rejects_existing_dst(backend, tmp_path):
    target = _make_dir_with_file(tmp_path)
    link = tmp_path / 'link'
    link.write_text('already here')

    with pytest.raises(InvalidLinkError):
        ntfslink.create_symlink(target, str(link), backend=backend)


def test_dangling_symlink_detected_and_protected(backend, tmp_path):
    missing_target = str(tmp_path / 'does_not_exist')
    link = str(tmp_path / 'dangling')

    ntfslink.create_symlink(missing_target, link, target_is_directory=True, backend=backend)

    assert not os.path.exists(link)  # os.path.exists follows the link
    assert ntfslink.is_reparse_point(link)  # but the link itself is there
    assert ntfslink.is_symlink(link, backend=backend)
    assert ntfslink.read_link(link, backend=backend) == missing_target

    with pytest.raises(InvalidLinkError):
        ntfslink.create_symlink(missing_target, link, target_is_directory=True, backend=backend)

    ntfslink.delete_reparse_point(link, backend=backend)
    assert not ntfslink.is_reparse_point(link)


def test_read_link_rejects_non_reparse_point(backend, tmp_path):
    plain_file = tmp_path / 'plain.txt'
    plain_file.write_text('x')
    with pytest.raises(InvalidLinkError):
        ntfslink.read_link(str(plain_file), backend=backend)


def test_delete_reparse_point_rejects_non_reparse_point(backend, tmp_path):
    plain_file = tmp_path / 'plain.txt'
    plain_file.write_text('x')
    with pytest.raises(InvalidLinkError):
        ntfslink.delete_reparse_point(str(plain_file), backend=backend)


def test_is_junction_is_symlink_false_for_plain_paths(backend, tmp_path):
    plain_file = tmp_path / 'plain.txt'
    plain_file.write_text('x')
    assert not ntfslink.is_junction(str(plain_file), backend=backend)
    assert not ntfslink.is_symlink(str(plain_file), backend=backend)
    assert not ntfslink.is_junction(str(tmp_path / 'missing'), backend=backend)
    assert not ntfslink.is_symlink(str(tmp_path / 'missing'), backend=backend)


def test_create_junction_rolls_back_created_dir_on_ioctl_failure(backend, tmp_path, monkeypatch):
    target = _make_dir_with_file(tmp_path)
    link = str(tmp_path / 'junction_fail')

    def boom(path, buffer):
        raise OSError('simulated DeviceIoControl failure')

    monkeypatch.setattr(backend, 'set_reparse_point', boom)

    with pytest.raises(OSError):
        ntfslink.create_junction(target, link, backend=backend)
    assert not os.path.exists(link)


def test_create_symlink_rolls_back_placeholder_on_ioctl_failure(backend, tmp_path, monkeypatch):
    target = _make_dir_with_file(tmp_path)
    link = str(tmp_path / 'symlink_fail')

    def boom(path, buffer):
        raise OSError('simulated DeviceIoControl failure')

    monkeypatch.setattr(backend, 'set_reparse_point', boom)

    with pytest.raises(OSError):
        ntfslink.create_symlink(target, link, backend=backend)
    assert not os.path.exists(link)


def test_create_symlink_file_placeholder_rolled_back_on_ioctl_failure(backend, tmp_path, monkeypatch):
    target = tmp_path / 'target.txt'
    target.write_text('data')
    link = str(tmp_path / 'file_symlink_fail.txt')

    def boom(path, buffer):
        raise OSError('simulated DeviceIoControl failure')

    monkeypatch.setattr(backend, 'set_reparse_point', boom)

    with pytest.raises(OSError):
        ntfslink.create_symlink(str(target), link, target_is_directory=False, backend=backend)
    assert not os.path.exists(link)


def test_create_junction_reuses_preexisting_empty_directory(backend, tmp_path):
    target = _make_dir_with_file(tmp_path)
    link = tmp_path / 'junction_preexisting'
    link.mkdir()  # dst already exists, empty — create_junction must not try to mkdir it again

    ntfslink.create_junction(target, str(link), backend=backend)
    assert ntfslink.is_junction(str(link), backend=backend)
    ntfslink.delete_reparse_point(str(link), backend=backend)


def test_create_junction_does_not_remove_preexisting_dir_on_failure(backend, tmp_path, monkeypatch):
    target = _make_dir_with_file(tmp_path)
    link = tmp_path / 'junction_preexisting_fail'
    link.mkdir()

    def boom(path, buffer):
        raise OSError('simulated DeviceIoControl failure')

    monkeypatch.setattr(backend, 'set_reparse_point', boom)

    with pytest.raises(OSError):
        ntfslink.create_junction(target, str(link), backend=backend)
    # dst pre-existed, so the rollback must leave it alone rather than removing it
    assert link.is_dir()


def test_read_link_rejects_unsupported_tag(backend, tmp_path, fake_backend):
    target = _make_dir_with_file(tmp_path, 'unsupported_tag_target')
    link = str(tmp_path / 'unsupported_tag_link')
    ntfslink.create_junction(target, link, backend=backend)
    try:
        fake_backend.parse_reparse_buffer = lambda data: (0xDEADBEEF, 0, 'x', 'x')
        with pytest.raises(NotImplementedError):
            ntfslink.read_link(link, backend=fake_backend)
    finally:
        ntfslink.delete_reparse_point(link, backend=backend)
