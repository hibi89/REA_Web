"""Fail-closed atomic publish primitives for local-only generated deliverables.

Supports Windows NTFS and Linux local filesystems. Other platforms stop
rather than use an unsafe check-then-rename of a directory. Neither function
creates public hosting nor protects against a hostile privileged filesystem.
"""
from __future__ import annotations

import ctypes
import errno
import os
from pathlib import Path
import sys


def publish_directory(stage: Path, destination: Path) -> None:
    """Atomically publish complete staged directory without replacing a target."""
    source, target = Path(stage), Path(destination)
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"Output already exists: {target}")
    if os.name == "nt":
        # Win32 MoveFile semantics: moving directory to existing name fails.
        os.rename(source, target)
    elif sys.platform.startswith("linux"):
        # Linux renameat2(RENAME_NOREPLACE) rejects even a new empty directory.
        # os.rename() on Linux could replace an owner's *empty* directory.
        libc = ctypes.CDLL(None, use_errno=True)
        try:
            renameat2 = libc.renameat2
        except AttributeError as exc:
            raise OSError("Atomic no-replace directory rename unavailable") from exc
        renameat2.argtypes = [
            ctypes.c_int, ctypes.c_char_p, ctypes.c_int,
            ctypes.c_char_p, ctypes.c_uint,
        ]
        renameat2.restype = ctypes.c_int
        rc = renameat2(-100, os.fsencode(source), -100,
                       os.fsencode(target), 1)  # RENAME_NOREPLACE
        if rc != 0:
            error = ctypes.get_errno()
            if error == errno.EEXIST:
                raise FileExistsError(error, os.strerror(error), str(target))
            raise OSError(error, os.strerror(error), str(target))
    else:
        raise OSError("Atomic no-replace directory publication not supported on this OS")


def publish_archive(stage: Path, destination: Path) -> None:
    """Publish only complete verified ZIP bytes, never a partial destination file."""
    source, target = Path(stage), Path(destination)
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"Archive already exists: {target}")
    # Both paths reside in the *same parent filesystem*; hard link is atomic.
    # Unsupported file systems fail closed with no target created.
    os.link(source, target)
