"""Creation must validate its retained parent before any filesystem mutation."""
import os

import pytest

from app.agent.authority import AuthorityError
from app.agent.ledger import private_directory
from app.agent.storage_paths import StorageAncestry


@pytest.mark.parametrize("mode", [0o722, 0o770, 0o777])
def test_unsafe_ancestor_refused_before_creating_descendants(tmp_path, mode):
    parent = tmp_path / "untrusted"
    parent.mkdir(mode=0o700)
    parent.chmod(mode)
    child = parent / "new" / "private"
    with pytest.raises(AuthorityError, match="unsafe_storage_ancestor"):
        private_directory(child, create=True)
    assert not (parent / "new").exists()


def test_private_nested_creation_is_descriptor_relative_and_owner_only(tmp_path):
    parent = tmp_path / "trusted"
    parent.mkdir(mode=0o700)
    target = parent / "new" / "private"
    original = os.umask(0)
    try:
        assert private_directory(target, create=True) == target
    finally:
        os.umask(original)
    assert (parent / "new").stat().st_mode & 0o777 == 0o700
    assert target.stat().st_mode & 0o777 == 0o700
    guard = StorageAncestry(target)
    guard.verify()


def test_symlink_ancestor_cannot_redirect_creation(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir(mode=0o700)
    alias = tmp_path / "alias"
    alias.symlink_to(outside, target_is_directory=True)
    with pytest.raises(AuthorityError):
        private_directory(alias / "new", create=True)
    assert not (outside / "new").exists()


def test_creation_race_refuses_competing_leaf_without_following_it(tmp_path, monkeypatch):
    outside = tmp_path / "outside"
    outside.mkdir(mode=0o700)
    parent = tmp_path / "trusted"
    parent.mkdir(mode=0o700)
    original = os.mkdir

    def race(path, mode=0o777, *, dir_fd=None):
        if path == "new" and dir_fd is not None:
            os.symlink(str(outside), path, dir_fd=dir_fd)
        return original(path, mode=mode, dir_fd=dir_fd)

    monkeypatch.setattr(os, "mkdir", race)
    with pytest.raises(AuthorityError, match="unsafe_storage_ancestor"):
        private_directory(parent / "new" / "victim", create=True)
    assert not (outside / "victim").exists()
