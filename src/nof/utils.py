#
# Copyright (C) 2020 Satoru SATOh <ssato@redhat.com>
# SPDX-License-Identifier: MIT
#
"""Global utility routines
"""
import os.path
import os

from . import globals


def datadir_maybe_from_env():
    """
    :return: data top dir of this app
    """
    return os.environ.get("NOF_DATA_DIR", globals.NOF_DATA_DIR)


def uploaddir(datadir=None):
    """
    >>> uploaddir()
    '/var/lib/nof/uploads'
    >>> uploaddir("/tmp/nof")
    '/tmp/nof/uploads'
    """
    if datadir is None:
        datadir = datadir_maybe_from_env()

    return os.path.join(datadir, "uploads")


def ensure_dir_exists(filepath):
    """Ensure dir for filepath exists
    """
    tdir = os.path.dirname(filepath)

    if not os.path.exists(tdir):
        os.makedirs(tdir)

# vim:sw=4:ts=4:et:
