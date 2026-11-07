"""Protected directory ancestry checks; same-UID/root compromise remains excluded.

Component-relative no-follow opens reject writable/foreign ancestors. Retained
identities detect later replacement, including replacement with the same leaf.
This is not an atomic SQLite VFS or protection from a malicious process owner.
"""
import os
from pathlib import Path
import stat

from app.agent.authority import AuthorityError


class StorageAncestry:
    def __init__(self, directory, *, create=False):
        self.path = Path(directory).absolute()
        if '..' in self.path.parts:
            raise AuthorityError('unsafe_storage_ancestor')
        self.identities = self._walk(create=create)
        if create:
            self.verify()

    def _walk(self, *, create=False):
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
        fd = None
        result = []
        try:
            fd = os.open('/', flags)
            for part in ('', *self.path.parts[1:]):
                if part:
                    try:
                        next_fd = os.open(part, flags, dir_fd=fd)
                    except FileNotFoundError:
                        if not create:
                            raise
                        # The retained parent has already passed its permission
                        # checks. Never resolve mkdir through an unchecked path.
                        try:os.mkdir(part, mode=0o700, dir_fd=fd)
                        except FileExistsError:pass
                        next_fd = os.open(part, flags, dir_fd=fd)
                    os.close(fd)
                    fd = next_fd
                item = os.fstat(fd)
                # Root-owned sticky /tmp protects existing user-owned entries.
                sticky_root = item.st_uid == 0 and bool(item.st_mode & stat.S_ISVTX)
                if item.st_uid not in {0, os.getuid()} or item.st_mode & 0o022 and not sticky_root:
                    raise AuthorityError('unsafe_storage_ancestor')
                result.append((item.st_dev, item.st_ino, item.st_uid, stat.S_IMODE(item.st_mode)))
            return tuple(result)
        except OSError as exc:
            raise AuthorityError('unsafe_storage_ancestor') from exc
        finally:
            if fd is not None:
                os.close(fd)

    def verify(self):
        if self._walk() != self.identities:
            raise AuthorityError('storage_ancestor_replaced')
